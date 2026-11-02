import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_URL } from '../../config'
import { catchError, jsonResponse, mockFetch } from '../../test/http'
import { ApiError, NETWORK_ERROR_STATUS } from './errors'
import { request } from './request'

describe('request', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends JSON with the cookie and returns the parsed response', async () => {
    const fetchMock = mockFetch(jsonResponse({ ok: true }))

    const data = await request('/auth/login/', { method: 'POST', body: { a: 1 } })

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

  it('adds the given headers', async () => {
    const fetchMock = mockFetch(jsonResponse({ ok: true }))

    await request('/startups/', { headers: { Authorization: 'Bearer token' } })

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_URL}/startups/`,
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer token' }),
      }),
    )
  })

  it('returns undefined for an empty response', async () => {
    mockFetch(new Response(null, { status: 204 }))

    await expect(request('/auth/logout/', { method: 'POST' })).resolves.toBeUndefined()
  })

  it('turns DRF errors into ApiError', async () => {
    mockFetch(
      jsonResponse(
        { detail: 'Too many attempts', email: ['Enter a valid email address.'] },
        { status: 429, headers: { 'Retry-After': '900' } },
      ),
    )

    const error = await catchError(request('/auth/login/'))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(429)
    expect(error.message).toBe('Too many attempts')
    expect(error.fieldErrors).toEqual({ email: ['Enter a valid email address.'] })
    expect(error.retryAfter).toBe(900)
  })

  it('reports a connection drop while reading the body as status 0', async () => {
    const response = new Response('{"ok": true}')
    vi.spyOn(response, 'text').mockRejectedValue(new TypeError('network error'))
    mockFetch(response)

    const error = await catchError(request('/health/'))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(NETWORK_ERROR_STATUS)
  })

  it('passes an aborted request through as is', async () => {
    const abort = new DOMException('The operation was aborted.', 'AbortError')
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(abort)

    await expect(request('/health/')).rejects.toBe(abort)
  })

  it('reports a network failure as status 0', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))

    const error = await catchError(request('/health/'))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(NETWORK_ERROR_STATUS)
  })
})
