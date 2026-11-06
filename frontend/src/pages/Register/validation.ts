import type { LegalForm, UserRole } from '../../api/auth'
import { EMAIL_FORMAT_MESSAGE, isValidEmail } from '../../utils/email'

export interface RegisterFormValues {
  company_name: string
  email: string
  password: string
  password_confirm: string
  last_name: string
  first_name: string
  // Empty until the user picks an option
  role: UserRole | ''
  legal_form: LegalForm | ''
}

export type RegisterField = keyof RegisterFormValues
export type RegisterErrors = Partial<Record<RegisterField, string>>

// In the order of the form
export const REGISTER_FIELDS: RegisterField[] = [
  'company_name',
  'email',
  'password',
  'password_confirm',
  'last_name',
  'first_name',
  'role',
  'legal_form',
]

// Texts from the registration mockup
export const REQUIRED_MESSAGES: Record<RegisterField, string> = {
  company_name: 'Не ввели назву компанії',
  email: 'Не ввели електронну пошту',
  password: 'Не ввели пароль',
  password_confirm: 'Не ввели пароль ще раз',
  last_name: 'Не ввели прізвище',
  first_name: 'Не ввели ім’я',
  role: 'Виберіть кого ви представляєте',
  legal_form: 'Виберіть який суб’єкт господарювання ви представляєте',
}
export const PASSWORD_HINT =
  'Пароль повинен мати 8+ символів, містити принаймні велику, малу літеру (A..Z, a..z) та цифру (0..9).'
export const PASSWORD_RULES_MESSAGE = 'Пароль не відповідає вимогам'
export const PASSWORDS_MISMATCH_MESSAGE =
  'Паролі не співпадають. Будь ласка, введіть однакові паролі в обидва поля'

const PASSWORD_MIN_LENGTH = 8
// Latin letters only and no Cyrillic, the same rule as on the backend
const PASSWORD_PATTERNS = [/[A-Z]/, /[a-z]/, /[0-9]/]
const CYRILLIC = /[Ѐ-ԯ]/

export function isStrongPassword(password: string) {
  return (
    password.length >= PASSWORD_MIN_LENGTH &&
    PASSWORD_PATTERNS.every((pattern) => pattern.test(password)) &&
    !CYRILLIC.test(password)
  )
}

// All errors of the form at once; a field without an error is missing
export function validateRegisterForm(values: RegisterFormValues): RegisterErrors {
  const errors: RegisterErrors = {}

  for (const field of ['company_name', 'email', 'last_name', 'first_name'] as const) {
    if (!values[field].trim()) {
      errors[field] = REQUIRED_MESSAGES[field]
    }
  }
  if (!errors.email && !isValidEmail(values.email)) {
    errors.email = EMAIL_FORMAT_MESSAGE
  }

  // Passwords are not trimmed: spaces are part of the password
  if (!values.password) {
    errors.password = REQUIRED_MESSAGES.password
  } else if (!isStrongPassword(values.password)) {
    errors.password = PASSWORD_RULES_MESSAGE
  }
  if (!values.password_confirm) {
    errors.password_confirm = REQUIRED_MESSAGES.password_confirm
  } else if (values.password_confirm !== values.password) {
    errors.password_confirm = PASSWORDS_MISMATCH_MESSAGE
  }

  if (!values.role) {
    errors.role = REQUIRED_MESSAGES.role
  }
  if (!values.legal_form) {
    errors.legal_form = REQUIRED_MESSAGES.legal_form
  }

  return errors
}
