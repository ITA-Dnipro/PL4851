import { useContext } from 'react'

import { AuthContext } from '../context/AuthContext'
import type { AuthContextValue } from '../context/AuthContext'

export type { AuthUser } from '../api/auth'

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext)
  if (!value) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return value
}
