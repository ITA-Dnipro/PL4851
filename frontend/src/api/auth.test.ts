import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_URL } from '../config'
import { jsonResponse, mockFetch } from '../test/http'
import { requestPasswordReset } from './auth'

describe('requestPasswordReset', () => {
  afterEach(() => vi.restoreAllMocks())

  it('posts the email to the password reset endpoint', async () => {
    const detail = 'If the email exists, you will receive reset instructions.'
    const fetchMock = mockFetch(jsonResponse({ detail }))

    await expect(requestPasswordReset({ email: 'founder@example.com' })).resolves.toEqual({
      detail,
    })

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_URL}/auth/password-reset/`,
      expect.objectContaining({ method: 'POST', body: '{"email":"founder@example.com"}' }),
    )
  })
})
