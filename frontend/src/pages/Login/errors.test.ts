import { describe, expect, it } from 'vitest'

import { ApiError, NETWORK_ERROR_STATUS } from '../../api/client/errors'
import {
  INVALID_CREDENTIALS_MESSAGE,
  INVALID_DATA_MESSAGE,
  NETWORK_ERROR_MESSAGE,
  UNKNOWN_ERROR_MESSAGE,
  getLoginErrorMessage,
  lockoutMessage,
} from './errors'

describe('getLoginErrorMessage', () => {
  it.each([
    [400, INVALID_DATA_MESSAGE],
    [401, INVALID_CREDENTIALS_MESSAGE],
    [NETWORK_ERROR_STATUS, NETWORK_ERROR_MESSAGE],
    [500, UNKNOWN_ERROR_MESSAGE],
  ])('maps status %i to its message', (status, message) => {
    expect(getLoginErrorMessage(new ApiError(status, 'Backend text'))).toBe(message)
  })

  it('shows the lockout time for 429', () => {
    const error = new ApiError(429, 'Backend text', {}, 900)

    expect(getLoginErrorMessage(error)).toBe(lockoutMessage(900))
  })

  it('falls back to a generic message for errors that are not ApiError', () => {
    expect(getLoginErrorMessage(new Error('Unexpected'))).toBe(UNKNOWN_ERROR_MESSAGE)
  })
})

describe('lockoutMessage', () => {
  it('rounds the wait up to whole minutes', () => {
    expect(lockoutMessage(900)).toContain('15 хв')
    expect(lockoutMessage(61)).toContain('2 хв')
  })

  it('omits the time when the backend did not send it', () => {
    expect(lockoutMessage(null)).not.toMatch(/хв/)
  })
})
