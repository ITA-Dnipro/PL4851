import { ApiError, NETWORK_ERROR_STATUS } from '../../api/client/errors'
import { NETWORK_ERROR_MESSAGE, UNKNOWN_ERROR_MESSAGE } from '../../utils/apiMessages'

export { NETWORK_ERROR_MESSAGE, UNKNOWN_ERROR_MESSAGE }

export const INVALID_DATA_MESSAGE = 'Перевірте введені дані'
export const INVALID_CREDENTIALS_MESSAGE = 'Електронна пошта чи пароль вказані некоректно'

export function lockoutMessage(retryAfter: number | null) {
  if (!retryAfter) {
    return 'Забагато спроб входу. Спробуйте пізніше'
  }
  const minutes = Math.ceil(retryAfter / 60)
  return `Забагато спроб входу. Спробуйте через ${minutes} хв`
}

// The message shown under the form when the backend rejects the login
export function getLoginErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return UNKNOWN_ERROR_MESSAGE
  }

  switch (error.status) {
    case 400:
      return INVALID_DATA_MESSAGE
    case 401:
      return INVALID_CREDENTIALS_MESSAGE
    case 429:
      return lockoutMessage(error.retryAfter)
    case NETWORK_ERROR_STATUS:
      return NETWORK_ERROR_MESSAGE
    default:
      return UNKNOWN_ERROR_MESSAGE
  }
}
