import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_URL } from '../config'
import { jsonResponse, mockFetch } from '../test/http'
import { register } from './auth'
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
