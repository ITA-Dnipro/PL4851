import { describe, expect, it } from 'vitest'

import {
  EMAIL_FORMAT_MESSAGE,
  EMAIL_REQUIRED_MESSAGE,
  PASSWORD_REQUIRED_MESSAGE,
  validateEmail,
  validatePassword,
} from './validation'

describe('validateEmail', () => {
  it.each(['name@example.com', '  name@example.com  ', 'first.last+tag@mail.co.ua'])(
    'accepts %s',
    (email) => {
      expect(validateEmail(email)).toBeNull()
    },
  )

  it.each(['', '   '])('requires a value: "%s"', (email) => {
    expect(validateEmail(email)).toBe(EMAIL_REQUIRED_MESSAGE)
  })

  it.each(['exgmail.com', 'name@', 'name@example', 'na me@example.com'])(
    'rejects %s',
    (email) => {
      expect(validateEmail(email)).toBe(EMAIL_FORMAT_MESSAGE)
    },
  )
})

describe('validatePassword', () => {
  it('accepts any non-empty password, even a short one', () => {
    expect(validatePassword('123')).toBeNull()
  })

  it('requires a value', () => {
    expect(validatePassword('')).toBe(PASSWORD_REQUIRED_MESSAGE)
  })
})
