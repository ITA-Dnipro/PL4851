import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useContext } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { login, logout } from '../api/auth'
import { getAccessToken, setAccessToken } from '../api/client/accessToken'
import { refreshAccessToken } from '../api/client/authRequest'
import { ApiError } from '../api/client/errors'
import AuthProvider from './AuthProvider'
import { AuthContext } from './AuthContext'

vi.mock('../api/auth', () => ({ login: vi.fn(), logout: vi.fn() }))
vi.mock('../api/client/authRequest', () => ({ refreshAccessToken: vi.fn() }))

const USER = { id: 1, email: 'founder@example.com', role: 'startup' as const }

// A JWT that expires in the given number of minutes
function tokenExpiringIn(minutes: number) {
  const exp = Math.floor(Date.now() / 1000) + minutes * 60
  return `header.${btoa(JSON.stringify({ exp }))}.signature`
}

// Makes the mocked refresh behave like the real one: it gets a new token
// (expiring in 15 minutes from now) or ends the session, and updates the token store
function refreshSucceeds() {
  vi.mocked(refreshAccessToken).mockImplementation(async () => {
    const token = tokenExpiringIn(15)
    setAccessToken(token)
    return token
  })
}

function refreshFails() {
  vi.mocked(refreshAccessToken).mockImplementation(async () => {
    setAccessToken(null)
    return null
  })
}

// Shows the context state and calls its actions, like a real component would
function Probe() {
  const auth = useContext(AuthContext)!
  return (
    <>
      <p>status: {auth.status}</p>
      <p>user: {auth.user?.email ?? 'none'}</p>
      <button type="button" onClick={() => auth.login({ email: 'a', password: 'b', remember: false })}>
        log in
      </button>
      <button type="button" onClick={() => auth.logout().catch(() => {})}>
        log out
      </button>
    </>
  )
}

function renderProvider() {
  render(
    <AuthProvider>
      <Probe />
    </AuthProvider>,
  )
}

describe('AuthProvider', () => {
  beforeEach(() => {
    refreshFails()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
    setAccessToken(null)
  })

  it('restores the session from the refresh cookie on start', async () => {
    refreshSucceeds()

    renderProvider()

    expect(await screen.findByText('status: authenticated')).toBeInTheDocument()
  })

  it('becomes anonymous without a refresh cookie', async () => {
    renderProvider()

    expect(await screen.findByText('status: anonymous')).toBeInTheDocument()
  })

  it('becomes anonymous when the backend is unreachable on start', async () => {
    vi.mocked(refreshAccessToken).mockRejectedValue(new ApiError(0, 'Network error'))

    renderProvider()

    expect(await screen.findByText('status: anonymous')).toBeInTheDocument()
  })

  it('logs in and keeps the access token in memory', async () => {
    const access = tokenExpiringIn(15)
    vi.mocked(login).mockResolvedValue({ access, user: USER })
    renderProvider()
    await screen.findByText('status: anonymous')

    await userEvent.click(screen.getByRole('button', { name: 'log in' }))

    expect(await screen.findByText('status: authenticated')).toBeInTheDocument()
    expect(screen.getByText(`user: ${USER.email}`)).toBeInTheDocument()
    expect(getAccessToken()).toBe(access)
  })

  it('keeps a login that finished before the startup refresh failed', async () => {
    let failRefresh: (error: unknown) => void = () => {}
    vi.mocked(refreshAccessToken).mockReturnValue(
      new Promise((_, reject) => {
        failRefresh = reject
      }),
    )
    vi.mocked(login).mockResolvedValue({ access: tokenExpiringIn(15), user: USER })
    renderProvider()

    await userEvent.click(screen.getByRole('button', { name: 'log in' }))
    await screen.findByText('status: authenticated')
    await act(async () => failRefresh(new ApiError(0, 'Network error')))

    expect(screen.getByText('status: authenticated')).toBeInTheDocument()
  })

  it('logs out locally even if the request fails', async () => {
    refreshSucceeds()
    vi.mocked(logout).mockRejectedValue(new ApiError(0, 'Network error'))
    renderProvider()
    await screen.findByText('status: authenticated')

    await userEvent.click(screen.getByRole('button', { name: 'log out' }))

    expect(await screen.findByText('status: anonymous')).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
  })

  it('refreshes the access token a minute before it expires', async () => {
    vi.useFakeTimers()
    refreshSucceeds()
    renderProvider()
    await act(async () => {})
    expect(refreshAccessToken).toHaveBeenCalledTimes(1)

    await act(async () => {
      vi.advanceTimersByTime(13 * 60 * 1000)
    })
    expect(refreshAccessToken).toHaveBeenCalledTimes(1)

    await act(async () => {
      vi.advanceTimersByTime(60 * 1000)
    })
    expect(refreshAccessToken).toHaveBeenCalledTimes(2)
  })

  it('does not refresh in a loop when a new token already looks expired', async () => {
    vi.useFakeTimers()
    // As if the client clock were ahead of the server
    vi.mocked(refreshAccessToken).mockImplementation(async () => {
      const token = tokenExpiringIn(0)
      setAccessToken(token)
      return token
    })
    renderProvider()
    await act(async () => {})

    await act(async () => {
      vi.advanceTimersByTime(60 * 1000)
    })

    // The start plus one refresh per 30 seconds
    expect(refreshAccessToken).toHaveBeenCalledTimes(3)
  })

  it('logs out when the scheduled refresh finds the session over', async () => {
    vi.useFakeTimers()
    refreshSucceeds()
    renderProvider()
    await act(async () => {})
    refreshFails()

    await act(async () => {
      vi.advanceTimersByTime(14 * 60 * 1000)
    })

    expect(screen.getByText('status: anonymous')).toBeInTheDocument()
  })
})
