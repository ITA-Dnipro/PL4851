import { describe, expect, it } from 'vitest'

import { isValidEmail } from './email'

describe('isValidEmail', () => {
  it.each(['name@example.com', '  name@example.com  ', 'first.last+tag@mail.co.ua'])(
    'accepts %s',
    (email) => {
      expect(isValidEmail(email)).toBe(true)
    },
  )

  it.each(['', 'exgmail.com', 'name@', 'name@example', 'na me@example.com'])(
    'rejects "%s"',
    (email) => {
      expect(isValidEmail(email)).toBe(false)
    },
  )
})
