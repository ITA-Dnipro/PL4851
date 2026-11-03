import { ApiError, NETWORK_ERROR_STATUS } from '../../api/client/errors'
import { NETWORK_ERROR_MESSAGE, UNKNOWN_ERROR_MESSAGE } from '../../utils/apiMessages'
import { EMAIL_FORMAT_MESSAGE } from '../../utils/email'
import { PASSWORDS_MISMATCH_MESSAGE, REGISTER_FIELDS } from './validation'
import type { RegisterErrors, RegisterField } from './validation'

export const EMAIL_TAKEN_MESSAGE = 'Ця електронна пошта вже зареєстрована'
export const WEAK_PASSWORD_MESSAGE =
  'Цей пароль занадто поширений або схожий на ваші дані. Оберіть інший'
export const INVALID_DATA_MESSAGE = 'Перевірте введені дані'
export const INVALID_VALUE_MESSAGE = 'Перевірте введене значення'

// Backend field errors are in English, so the form shows its own texts
const FIELD_MESSAGES: Partial<Record<RegisterField, string>> = {
  email: EMAIL_FORMAT_MESSAGE,
  // The form already checks the rules from the hint, so the backend can only
  // reject a common password or one similar to the email or name
  password: WEAK_PASSWORD_MESSAGE,
  password_confirm: PASSWORDS_MISMATCH_MESSAGE,
}

export function rateLimitMessage(retryAfter: number | null) {
  if (!retryAfter) {
    return 'Забагато спроб реєстрації. Спробуйте пізніше'
  }
  const minutes = Math.ceil(retryAfter / 60)
  return `Забагато спроб реєстрації. Спробуйте через ${minutes} хв`
}

export interface RegisterServerErrors {
  // Shown under the fields
  fields: RegisterErrors
  // Shown above the submit button
  form: string | null
}

// Where to show a rejected registration: under a field or above the button
export function getRegisterErrors(error: unknown): RegisterServerErrors {
  if (!(error instanceof ApiError)) {
    return { fields: {}, form: UNKNOWN_ERROR_MESSAGE }
  }

  switch (error.status) {
    case 400: {
      const fields: RegisterErrors = {}
      for (const field of REGISTER_FIELDS) {
        if (error.fieldErrors[field]) {
          fields[field] = FIELD_MESSAGES[field] ?? INVALID_VALUE_MESSAGE
        }
      }
      const hasFieldErrors = Object.keys(fields).length > 0
      return { fields, form: hasFieldErrors ? null : INVALID_DATA_MESSAGE }
    }
    case 409:
      return { fields: { email: EMAIL_TAKEN_MESSAGE }, form: null }
    case 429:
      return { fields: {}, form: rateLimitMessage(error.retryAfter) }
    case NETWORK_ERROR_STATUS:
      return { fields: {}, form: NETWORK_ERROR_MESSAGE }
    default:
      return { fields: {}, form: UNKNOWN_ERROR_MESSAGE }
  }
}
