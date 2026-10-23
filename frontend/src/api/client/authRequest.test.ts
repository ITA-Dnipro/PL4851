import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_URL } from '../../config'
import { catchError, jsonResponse, mockFetch } from '../../test/http'
import { getAccessToken, setAccessToken } from './accessToken'
import { authRequest } from './authRequest'

function authorizationOf(call: unknown[]) {
  return ((call[1] as RequestInit).headers as Record<string, string>).Authorization
}

describe('authRequest', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    setAccessToken(null)
  })

  it('sends the access token', async () => {
    setAccessToken('old-token')
    const fetchMock = mockFetch(jsonResponse({ ok: true }))

    await authRequest('/profile/')

    expect(authorizationOf(fetchMock.mock.calls[0])).toBe('Bearer old-token')
  })

  it('refreshes the token on 401 and repeats the request', async () => {
    setAccessToken('old-token')
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ detail: 'expired' }, { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ access: 'new-token' }))
      .mockResolvedValueOnce(jsonResponse({ ok: true }))

    const data = await authRequest('/profile/')

    expect(data).toEqual({ ok: true })
    expect(fetchMock.mock.calls[1][0]).toBe(`${API_URL}/auth/refresh/`)
    expect(authorizationOf(fetchMock.mock.calls[2])).toBe('Bearer new-token')
    expect(getAccessToken()).toBe('new-token')
  })

  it('sends one refresh for parallel requests', async () => {
    setAccessToken('old-token')
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (url, init) => {
      if (String(url).endsWith('/auth/refresh/')) {
        return jsonResponse({ access: 'new-token' })
      }
      const authorization = (init?.headers as Record<string, string>).Authorization
      return authorization === 'Bearer new-token'
        ? jsonResponse({ ok: true })
        : jsonResponse({ detail: 'expired' }, { status: 401 })
    })

    await Promise.all([authRequest('/profile/'), authRequest('/saved/')])

    const refreshCalls = fetchMock.mock.calls.filter(([url]) =>
      String(url).endsWith('/auth/refresh/'),
    )
    expect(refreshCalls).toHaveLength(1)
  })

  it('ends the session when the refresh fails', async () => {
    setAccessToken('old-token')
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ detail: 'expired' }, { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ detail: 'no cookie' }, { status: 401 }))

    const error = await catchError(authRequest('/profile/'))

    expect(error.status).toBe(401)
    expect(getAccessToken()).toBeNull()
  })

  it('keeps the session when the refresh fails without a connection', async () => {
    setAccessToken('old-token')
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ detail: 'expired' }, { status: 401 }))
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))

    const error = await catchError(authRequest('/profile/'))

    expect(error.status).toBe(0)
    expect(getAccessToken()).toBe('old-token')
  })
})
