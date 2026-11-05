import { describe, expect, it } from 'vitest'

import {
  validateNewPassword,
  validateConfirmPassword,
} from './validation'

describe('validateNewPassword', () => {
  it('rejects an empty password', () => {
    expect(validateNewPassword('')).toBe(
      'Введіть новий пароль',
    )
  })

  it('rejects passwords shorter than 8 characters', () => {
    expect(validateNewPassword('Abc123!')).toBe(
      'Пароль повинен містити щонайменше 8 символів',
    )
  })

  it('rejects numeric-only passwords', () => {
    expect(validateNewPassword('12345678')).toBe(
      'Пароль не може складатися лише з цифр',
    )
  })

  it('accepts a valid password', () => {
    expect(validateNewPassword('SecurePass123!')).toBeNull()
  })
})

describe('validateConfirmPassword', () => {
  it('rejects an empty confirmation', () => {
    expect(validateConfirmPassword('SecurePass123!', '')).toBe(
      'Підтвердіть новий пароль',
    )
  })

  it('rejects mismatched passwords', () => {
    expect(
      validateConfirmPassword('SecurePass123!', 'DifferentPass123!'),
    ).toBe('Паролі не збігаються')
  })

  it('accepts matching passwords', () => {
    expect(
      validateConfirmPassword('SecurePass123!', 'SecurePass123!'),
    ).toBeNull()
  })
})
