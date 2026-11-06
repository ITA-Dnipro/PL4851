import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_URL } from '../config'
import { jsonResponse, mockFetch } from '../test/http'
import { register, requestPasswordReset } from './auth'
import type { RegisterRequest } from './auth'

const data: RegisterRequest = {
  email: 'founder@example.com',
  password: 'Craft-2026',
  password_confirm: 'Craft-2026',
  first_name: 'Andrii',
  last_name: 'Test',
  company_name: 'Handmade Co',
  role: 'startup',
  legal_form: 'sole_proprietor',
}

describe('register', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('posts the form and returns the created account', async () => {
    const created = { id: 12, email: data.email, detail: 'Verification email sent.' }
    const fetchMock = mockFetch(jsonResponse(created, { status: 201 }))

    await expect(register(data)).resolves.toEqual(created)

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_URL}/auth/register/`,
      expect.objectContaining({ method: 'POST', body: JSON.stringify(data) }),
    )
  })
})

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
