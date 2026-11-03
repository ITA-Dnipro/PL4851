import { describe, expect, it } from 'vitest'

import { EMAIL_FORMAT_MESSAGE } from '../../utils/email'
import {
  PASSWORD_RULES_MESSAGE,
  PASSWORDS_MISMATCH_MESSAGE,
  REQUIRED_MESSAGES,
  isStrongPassword,
  validateRegisterForm,
} from './validation'
import type { RegisterFormValues } from './validation'

const validForm: RegisterFormValues = {
  company_name: 'Handmade Co',
  email: 'founder@example.com',
  password: 'Craft-2026',
  password_confirm: 'Craft-2026',
  last_name: 'Test',
  first_name: 'Andrii',
  role: 'startup',
  legal_form: 'sole_proprietor',
}

const emptyForm: RegisterFormValues = {
  company_name: '',
  email: '',
  password: '',
  password_confirm: '',
  last_name: '',
  first_name: '',
  role: '',
  legal_form: '',
}

describe('isStrongPassword', () => {
  it.each(['Craft-2026', 'Abcdefg1', 'Pass word 9!'])('accepts %s', (password) => {
    expect(isStrongPassword(password)).toBe(true)
  })

  it.each([
    ['too short', 'Abcde1!'],
    ['no uppercase', 'craft-2026'],
    ['no lowercase', 'CRAFT-2026'],
    ['no digit', 'Craftmerge'],
    ['Cyrillic letters', 'Пароль-Ok7'],
    ['a Ukrainian letter', 'Craft2026ї'],
  ])('rejects a password with %s', (_, password) => {
    expect(isStrongPassword(password)).toBe(false)
  })
})

describe('validateRegisterForm', () => {
  it('accepts a filled form', () => {
    expect(validateRegisterForm(validForm)).toEqual({})
  })

  it('requires every field with the mockup texts', () => {
    expect(validateRegisterForm(emptyForm)).toEqual(REQUIRED_MESSAGES)
  })

  it('treats spaces as an empty text field', () => {
    const errors = validateRegisterForm({
      ...validForm,
      company_name: '  ',
      email: ' ',
      last_name: '   ',
      first_name: ' ',
    })

    expect(errors).toEqual({
      company_name: REQUIRED_MESSAGES.company_name,
      email: REQUIRED_MESSAGES.email,
      last_name: REQUIRED_MESSAGES.last_name,
      first_name: REQUIRED_MESSAGES.first_name,
    })
  })

  it('checks the email format', () => {
    expect(validateRegisterForm({ ...validForm, email: 'exgmail.com' })).toEqual({
      email: EMAIL_FORMAT_MESSAGE,
    })
  })

  it('checks the password rules', () => {
    const errors = validateRegisterForm({
      ...validForm,
      password: 'craft-2026',
      password_confirm: 'craft-2026',
    })

    expect(errors).toEqual({ password: PASSWORD_RULES_MESSAGE })
  })

  it('reports different passwords on the confirmation field', () => {
    expect(validateRegisterForm({ ...validForm, password_confirm: 'Craft-2027' })).toEqual({
      password_confirm: PASSWORDS_MISMATCH_MESSAGE,
    })
  })

  it('compares the passwords without trimming spaces', () => {
    expect(validateRegisterForm({ ...validForm, password_confirm: 'Craft-2026 ' })).toEqual({
      password_confirm: PASSWORDS_MISMATCH_MESSAGE,
    })
  })

  it('requires the confirmation even when the password is missing', () => {
    expect(
      validateRegisterForm({ ...validForm, password: '', password_confirm: '' }),
    ).toEqual({
      password: REQUIRED_MESSAGES.password,
      password_confirm: REQUIRED_MESSAGES.password_confirm,
    })
  })
})
