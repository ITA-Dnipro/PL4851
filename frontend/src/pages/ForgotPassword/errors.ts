import { ApiError, NETWORK_ERROR_STATUS } from '../../api/client/errors'
import { NETWORK_ERROR_MESSAGE, UNKNOWN_ERROR_MESSAGE } from '../Login/errors'
import { EMAIL_FORMAT_MESSAGE } from '../Login/validation'

// No wait time: the backend doesn't expose Retry-After to the browser (CORS)
export const TOO_MANY_REQUESTS_MESSAGE = 'Забагато запитів. Спробуйте пізніше'

export interface ResetRequestFailure {
  message: string
  // The backend rejected the address itself, so the field is marked invalid
  invalidEmail: boolean
}

// What to show under the email field when the reset request fails
export function getResetRequestFailure(error: unknown): ResetRequestFailure {
  if (!(error instanceof ApiError)) {
    return { message: UNKNOWN_ERROR_MESSAGE, invalidEmail: false }
  }

  switch (error.status) {
    case 400:
      // Django checks addresses more strictly than our pattern, e.g. a one-letter domain ending.
      // Any other bad request isn't the user's typo, so it gets the generic text
      return error.fieldErrors.email
        ? { message: EMAIL_FORMAT_MESSAGE, invalidEmail: true }
        : { message: UNKNOWN_ERROR_MESSAGE, invalidEmail: false }
    case 429:
      return { message: TOO_MANY_REQUESTS_MESSAGE, invalidEmail: false }
    case NETWORK_ERROR_STATUS:
      return { message: NETWORK_ERROR_MESSAGE, invalidEmail: false }
    default:
      return { message: UNKNOWN_ERROR_MESSAGE, invalidEmail: false }
  }
}
