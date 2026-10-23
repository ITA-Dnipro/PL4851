import { refresh } from '../auth'
import { getAccessToken, setAccessToken } from './accessToken'
import { ApiError } from './errors'
import { request } from './request'
import type { RequestOptions } from './request'

let refreshing: Promise<string | null> | null = null

// request() for endpoints that need a signed-in user: sends the access token and,
// when it has expired (401), gets a new one and repeats the request once
export async function authRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  try {
    return await request<T>(path, withAccessToken(options))
  } catch (error) {
    if (error instanceof ApiError && error.status === 401 && (await refreshAccessToken())) {
      return request<T>(path, withAccessToken(options))
    }
    throw error
  }
}

// Gets a new access token with the refresh cookie. Returns null when the session
// is over. Parallel calls wait for the same request instead of sending their own.
export function refreshAccessToken(): Promise<string | null> {
  refreshing ??= requestAccessToken().finally(() => {
    refreshing = null
  })
  return refreshing
}

async function requestAccessToken(): Promise<string | null> {
  try {
    const { access } = await refresh()
    setAccessToken(access)
    return access
  } catch (error) {
    // The cookie is missing, expired or revoked. Other errors (no connection)
    // don't end the session.
    if (error instanceof ApiError && error.status === 401) {
      setAccessToken(null)
      return null
    }
    throw error
  }
}

function withAccessToken(options: RequestOptions): RequestOptions {
  const token = getAccessToken()
  if (!token) {
    return options
  }
  return { ...options, headers: { ...options.headers, Authorization: `Bearer ${token}` } }
}
