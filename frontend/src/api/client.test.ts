import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_URL } from '../config'
import { apiRequest } from './client'
import { ApiError, NETWORK_ERROR_STATUS } from './errors'

function mockFetch(response: Response) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValue(response)
}

function jsonResponse(data: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(data), init)
}

async function catchError(promise: Promise<unknown>): Promise<ApiError> {
  try {
    await promise
  } catch (error) {
    return error as ApiError
  }
  throw new Error('The request did not fail')
}

describe('apiRequest', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends JSON with the cookie and returns the parsed response', async () => {
    const fetchMock = mockFetch(jsonResponse({ ok: true }))

    const data = await apiRequest('/auth/login/', { method: 'POST', body: { a: 1 } })

    expect(data).toEqual({ ok: true })
    expect(fetchMock).toHaveBeenCalledWith(
      `${API_URL}/auth/login/`,
      expect.objectContaining({
        method: 'POST',
        body: '{"a":1}',
        credentials: 'include',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
      }),
    )
  })

  it('returns undefined for an empty response', async () => {
    mockFetch(new Response(null, { status: 204 }))

    await expect(apiRequest('/auth/logout/', { method: 'POST' })).resolves.toBeUndefined()
  })

  it('turns DRF errors into ApiError', async () => {
    mockFetch(
      jsonResponse(
        { detail: 'Too many attempts', email: ['Enter a valid email address.'] },
        { status: 429, headers: { 'Retry-After': '900' } },
      ),
    )

    const error = await catchError(apiRequest('/auth/login/'))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(429)
    expect(error.message).toBe('Too many attempts')
    expect(error.fieldErrors).toEqual({ email: ['Enter a valid email address.'] })
    expect(error.retryAfter).toBe(900)
  })

  it('reports a network failure as status 0', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))

    const error = await catchError(apiRequest('/health/'))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(NETWORK_ERROR_STATUS)
  })
})
