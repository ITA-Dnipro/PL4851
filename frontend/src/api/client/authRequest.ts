import { refresh } from '../auth'
import { getAccessToken, getSession, sessionEnded, setAccessToken } from './accessToken'
import { ApiError } from './errors'
import { request } from './request'
import type { RequestOptions } from './request'

// The refresh in progress and the session it was started in
let refreshing: { session: number; promise: Promise<string | null> } | null = null

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
// is over. Parallel calls in the same session wait for the same request instead of
// sending their own.
export function refreshAccessToken(): Promise<string | null> {
  // After logout only a new login can start a session
  if (sessionEnded()) {
    return Promise.resolve(null)
  }
  const session = getSession()
  if (refreshing?.session !== session) {
    const promise = requestAccessToken(session).finally(() => {
      if (refreshing?.promise === promise) {
        refreshing = null
      }
    })
    refreshing = { session, promise }
  }
  return refreshing.promise
}

async function requestAccessToken(session: number): Promise<string | null> {
  try {
    const { access } = await refresh()
    // A login or logout happened meanwhile: keep the token it set
    if (session !== getSession()) {
      return getAccessToken()
    }
    setAccessToken(access)
    return access
  } catch (error) {
    // The cookie is missing, expired or revoked. Other errors (no connection)
    // don't end the session.
    if (error instanceof ApiError && error.status === 401) {
      if (session !== getSession()) {
        return getAccessToken()
      }
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
