import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import { login as loginRequest, logout as logoutRequest } from '../api/auth'
import type { AuthUser, LoginRequest } from '../api/auth'
import {
  endSession,
  getAccessToken,
  startSession,
  subscribeToAccessToken,
} from '../api/client/accessToken'
import { refreshAccessToken } from '../api/client/authRequest'
import { AuthContext } from './AuthContext'
import type { AuthContextValue, AuthStatus } from './AuthContext'
import { getTokenExpiry } from './jwt'

// Refresh the access token this long before it expires
const REFRESH_BEFORE_EXPIRY_MS = 60 * 1000
// Never sooner than this: with a client clock far ahead of the server every new
// token would look expired, and the refreshes would run in a loop
const MIN_REFRESH_DELAY_MS = 30 * 1000

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading')
  const [user, setUser] = useState<AuthUser | null>(null)

  // Follow the access token: it also changes inside authRequest when a refresh fails
  useEffect(() => {
    let refreshTimer: ReturnType<typeof setTimeout> | undefined

    const unsubscribe = subscribeToAccessToken((token) => {
      clearTimeout(refreshTimer)
      if (!token) {
        setUser(null)
        setStatus('anonymous')
        return
      }

      setStatus('authenticated')
      const expiry = getTokenExpiry(token)
      if (expiry) {
        const delay = Math.max(
          expiry - Date.now() - REFRESH_BEFORE_EXPIRY_MS,
          MIN_REFRESH_DELAY_MS,
        )
        // A failed refresh (no connection) is retried on the next 401
        refreshTimer = setTimeout(() => refreshAccessToken().catch(() => {}), delay)
      }
    })

    return () => {
      clearTimeout(refreshTimer)
      unsubscribe()
    }
  }, [])

  // After a page reload the access token is gone, but the refresh cookie may be there
  useEffect(() => {
    refreshAccessToken().catch(() => {
      // The backend is unreachable; a login that already finished keeps its session
      if (!getAccessToken()) {
        setStatus('anonymous')
      }
    })
  }, [])

  const login = useCallback(async (data: LoginRequest) => {
    const response = await loginRequest(data)
    setUser(response.user)
    startSession(response.access)
  }, [])

  const logout = useCallback(async () => {
    // Sign out locally first: it works even if the request fails, and no refresh
    // (in progress or new) can bring the session back
    endSession()
    await logoutRequest()
  }, [])

  const refresh = useCallback(async () => Boolean(await refreshAccessToken()), [])

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      isAuthenticated: status === 'authenticated',
      user,
      login,
      logout,
      refresh,
    }),
    [status, user, login, logout, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
