import { createContext } from 'react'

import type { AuthUser, LoginRequest } from '../api/auth'

// "loading" until the session is restored after a page reload
export type AuthStatus = 'loading' | 'authenticated' | 'anonymous'

export interface AuthContextValue {
  status: AuthStatus
  isAuthenticated: boolean
  // Known after login; after a page reload it stays null until GET /api/auth/me/ exists
  user: AuthUser | null
  login: (data: LoginRequest) => Promise<void>
  logout: () => Promise<void>
  // Gets a new access token; resolves to false when the session is over
  refresh: () => Promise<boolean>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
