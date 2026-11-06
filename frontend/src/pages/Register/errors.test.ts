import { describe, expect, it } from 'vitest'

import { ApiError, NETWORK_ERROR_STATUS } from '../../api/client/errors'
import { NETWORK_ERROR_MESSAGE, UNKNOWN_ERROR_MESSAGE } from '../../utils/apiMessages'
import { EMAIL_FORMAT_MESSAGE } from '../../utils/email'
import {
  EMAIL_TAKEN_MESSAGE,
  INVALID_DATA_MESSAGE,
  INVALID_VALUE_MESSAGE,
  WEAK_PASSWORD_MESSAGE,
  getRegisterErrors,
  rateLimitMessage,
} from './errors'
import { PASSWORDS_MISMATCH_MESSAGE } from './validation'

describe('getRegisterErrors', () => {
  it('shows a taken email under the email field', () => {
    expect(getRegisterErrors(new ApiError(409, 'Conflict'))).toEqual({
      fields: { email: EMAIL_TAKEN_MESSAGE },
      form: null,
    })
  })

  it('shows backend field errors under their fields with the form texts', () => {
    const error = new ApiError(400, 'Bad Request', {
      email: ['Enter a valid email address.'],
      password: ['This password is too common.'],
      password_confirm: ['Passwords do not match.'],
      company_name: ['Ensure this field has no more than 255 characters.'],
    })

    expect(getRegisterErrors(error)).toEqual({
      fields: {
        email: EMAIL_FORMAT_MESSAGE,
        password: WEAK_PASSWORD_MESSAGE,
        password_confirm: PASSWORDS_MISMATCH_MESSAGE,
        company_name: INVALID_VALUE_MESSAGE,
      },
      form: null,
    })
  })

  it('falls back to a form message when a 400 has no known fields', () => {
    const error = new ApiError(400, 'Bad Request', { non_field_errors: ['Invalid data.'] })

    expect(getRegisterErrors(error)).toEqual({ fields: {}, form: INVALID_DATA_MESSAGE })
  })

  it('reports the rate limit with the waiting time', () => {
    const error = new ApiError(429, 'Too Many Requests', {}, 1800)

    expect(getRegisterErrors(error)).toEqual({ fields: {}, form: rateLimitMessage(1800) })
    expect(rateLimitMessage(1800)).toBe('Забагато спроб реєстрації. Спробуйте через 30 хв')
    expect(rateLimitMessage(null)).toBe('Забагато спроб реєстрації. Спробуйте пізніше')
  })

  it('reports a lost connection', () => {
    expect(getRegisterErrors(new ApiError(NETWORK_ERROR_STATUS, 'Failed to fetch'))).toEqual({
      fields: {},
      form: NETWORK_ERROR_MESSAGE,
    })
  })

  it.each([new ApiError(500, 'Server Error'), new Error('boom')])(
    'reports anything else as an unknown error',
    (error) => {
      expect(getRegisterErrors(error)).toEqual({ fields: {}, form: UNKNOWN_ERROR_MESSAGE })
    },
  )
})
