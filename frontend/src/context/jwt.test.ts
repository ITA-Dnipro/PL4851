import { describe, expect, it } from 'vitest'

import { getTokenExpiry } from './jwt'

function tokenWith(payload: object) {
  const encoded = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')
  return `header.${encoded}.signature`
}

describe('getTokenExpiry', () => {
  it('returns the expiry in milliseconds', () => {
    expect(getTokenExpiry(tokenWith({ exp: 1_700_000_000 }))).toBe(1_700_000_000_000)
  })

  it('returns null for a token without exp', () => {
    expect(getTokenExpiry(tokenWith({ user_id: '1' }))).toBeNull()
  })

  it('returns null for something that is not a JWT', () => {
    expect(getTokenExpiry('not-a-token')).toBeNull()
  })
})
