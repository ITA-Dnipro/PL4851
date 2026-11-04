import { describe, expect, it } from 'vitest'

import { ApiError, NETWORK_ERROR_STATUS } from '../../api/client/errors'
import { NETWORK_ERROR_MESSAGE, UNKNOWN_ERROR_MESSAGE } from '../Login/errors'
import { EMAIL_FORMAT_MESSAGE } from '../Login/validation'
import { TOO_MANY_REQUESTS_MESSAGE, getResetRequestFailure } from './errors'

describe('getResetRequestFailure', () => {
  it.each([
    [400, EMAIL_FORMAT_MESSAGE, true],
    [429, TOO_MANY_REQUESTS_MESSAGE, false],
    [NETWORK_ERROR_STATUS, NETWORK_ERROR_MESSAGE, false],
    [500, UNKNOWN_ERROR_MESSAGE, false],
  ])('maps status %i to its message', (status, message, invalidEmail) => {
    // A Retry-After from the backend must not add a wait time to the message
    const error = new ApiError(status, 'Backend text', {}, 900)

    expect(getResetRequestFailure(error)).toEqual({ message, invalidEmail })
  })

  it('falls back to a generic message for errors that are not ApiError', () => {
    expect(getResetRequestFailure(new Error('Unexpected'))).toEqual({
      message: UNKNOWN_ERROR_MESSAGE,
      invalidEmail: false,
    })
  })
})
