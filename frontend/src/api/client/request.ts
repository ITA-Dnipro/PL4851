import { API_URL } from '../../config'
import { ApiError, NETWORK_ERROR_STATUS } from './errors'
import type { FieldErrors } from './errors'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export interface RequestOptions {
  method?: HttpMethod
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
}

// A plain request to the backend: JSON in and out, the refresh token cookie
// included, failures as ApiError. Endpoints that need a signed-in user use
// authRequest, which adds the access token on top of this.
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, signal } = options
  const headers: Record<string, string> = { Accept: 'application/json', ...options.headers }
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  let response: Response
  let data: unknown
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      // Send and save the refresh token cookie
      credentials: 'include',
      signal,
    })
    // Reading the body can fail too if the connection drops halfway
    data = await readJson(response)
  } catch (error) {
    // An aborted request isn't an API error: let the caller ignore it
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }
    throw new ApiError(NETWORK_ERROR_STATUS, 'Network error')
  }

  if (!response.ok) {
    throw toApiError(response, data)
  }
  return data as T
}

async function readJson(response: Response): Promise<unknown> {
  // 204 and other empty responses have no body to parse
  const text = await response.text()
  if (!text) {
    return undefined
  }
  try {
    return JSON.parse(text)
  } catch {
    return undefined
  }
}

function toApiError(response: Response, data: unknown): ApiError {
  let message = `Request failed with status ${response.status}`
  const fieldErrors: FieldErrors = {}

  if (data && typeof data === 'object') {
    // DRF puts general errors in "detail" and field errors under field names
    for (const [key, value] of Object.entries(data)) {
      if (key === 'detail' && typeof value === 'string') {
        message = value
      } else if (Array.isArray(value)) {
        fieldErrors[key] = value.map(String)
      }
    }
  }

  const retryAfter = Number(response.headers.get('Retry-After'))
  return new ApiError(
    response.status,
    message,
    fieldErrors,
    retryAfter > 0 ? retryAfter : null,
  )
}
