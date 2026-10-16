// Something before and after "@" and a dot in the domain, no spaces
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export const EMAIL_REQUIRED_MESSAGE = 'Введіть електронну пошту'
export const EMAIL_FORMAT_MESSAGE = 'Введіть адресу електронної пошти у форматі name@example.com'
export const PASSWORD_REQUIRED_MESSAGE = 'Введіть пароль'

// Each validator returns an error message, or null when the value is valid

export function validateEmail(value: string): string | null {
  const email = value.trim()
  if (!email) {
    return EMAIL_REQUIRED_MESSAGE
  }
  if (!EMAIL_PATTERN.test(email)) {
    return EMAIL_FORMAT_MESSAGE
  }
  return null
}

// Only checks that a password was entered: length and complexity rules apply
// when a password is created, while login must accept any existing password
export function validatePassword(value: string): string | null {
  return value ? null : PASSWORD_REQUIRED_MESSAGE
}
