export const MIN_PASSWORD_LENGTH = 8

export function validateNewPassword(password: string): string | null {
  if (!password) {
    return 'Введіть новий пароль'
  }

  if (password.length < MIN_PASSWORD_LENGTH) {
    return 'Пароль повинен містити щонайменше 8 символів'
  }

  if (/^\d+$/.test(password)) {
    return 'Пароль не може складатися лише з цифр'
  }

  return null
}

export function validateConfirmPassword(
  password: string,
  confirmPassword: string,
): string | null {
  if (!confirmPassword) {
    return 'Підтвердіть новий пароль'
  }

  if (password !== confirmPassword) {
    return 'Паролі не збігаються'
  }

  return null
}
