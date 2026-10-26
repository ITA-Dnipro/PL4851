import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import ProtectedRoute from '.'
import type { AuthStatus } from '../../context/AuthContext'
import { useAuth } from '../../hooks/useAuth'
import { authValue } from '../../test/auth'

vi.mock('../../hooks/useAuth')

function LoginPage() {
  const location = useLocation()
  const from = (location.state as { from?: { pathname: string } } | null)?.from
  return <p>Login page, from {from?.pathname}</p>
}

function renderAt(status: AuthStatus) {
  vi.mocked(useAuth).mockReturnValue(
    authValue({ status, isAuthenticated: status === 'authenticated' }),
  )
  render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<p>Dashboard</p>} />
        </Route>
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  it('shows the page to a signed-in user', () => {
    renderAt('authenticated')

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('sends an anonymous user to the login page and remembers the page', () => {
    renderAt('anonymous')

    expect(screen.getByText('Login page, from /dashboard')).toBeInTheDocument()
  })

  it('shows nothing while the session is being restored', () => {
    renderAt('loading')

    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
    expect(screen.queryByText(/Login page/)).not.toBeInTheDocument()
  })
})
