import { vi } from 'vitest'

import type { AuthContextValue } from '../context/AuthContext'

// A complete auth context for tests that mock useAuth
export function authValue(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    status: 'anonymous',
    isAuthenticated: false,
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
    ...overrides,
  }
}
