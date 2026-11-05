// Both sides of "@" are non-empty parts split by single dots (at least one in
// the domain); no spaces
const EMAIL_PATTERN = /^[^\s@.]+(\.[^\s@.]+)*@[^\s@.]+(\.[^\s@.]+)+$/

export const EMAIL_FORMAT_MESSAGE = 'Введіть адресу електронної пошти у форматі name@example.com'

export function isValidEmail(value: string) {
  return EMAIL_PATTERN.test(value.trim())
}
