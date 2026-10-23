import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import UserMenu from '.'
import type { AuthContextValue } from '../../context/AuthContext'
import { useAuth } from '../../hooks/useAuth'
import { authValue } from '../../test/auth'

vi.mock('../../hooks/useAuth')

const logout = vi.fn<AuthContextValue['logout']>()

function renderMenu() {
  const user = userEvent.setup()
  render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <p>Outside</p>
      <UserMenu />
      <Routes>
        <Route path="/" element={<p>Home page</p>} />
        <Route path="/dashboard" element={<p>Dashboard</p>} />
        <Route path="/profile" element={<p>Profile page</p>} />
      </Routes>
    </MemoryRouter>,
  )
  return user
}

function trigger() {
  return screen.getByRole('button', { name: 'Мій профіль' })
}

describe('UserMenu', () => {
  beforeEach(() => {
    logout.mockReset()
    vi.mocked(useAuth).mockReturnValue(
      authValue({ status: 'authenticated', isAuthenticated: true, logout }),
    )
  })

  it('opens and closes the dropdown with the button', async () => {
    const user = renderMenu()

    expect(trigger()).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByRole('link', { name: 'Профіль' })).not.toBeInTheDocument()

    await user.click(trigger())
    expect(trigger()).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByRole('link', { name: 'Профіль' })).toBeVisible()

    await user.click(trigger())
    expect(trigger()).toHaveAttribute('aria-expanded', 'false')
  })

  it('closes on Escape and returns the focus to the button', async () => {
    const user = renderMenu()
    await user.click(trigger())

    await user.keyboard('{Escape}')

    expect(trigger()).toHaveAttribute('aria-expanded', 'false')
    expect(trigger()).toHaveFocus()
  })

  it('closes on a click outside', async () => {
    const user = renderMenu()
    await user.click(trigger())

    await user.click(screen.getByText('Outside'))

    expect(trigger()).toHaveAttribute('aria-expanded', 'false')
  })

  it('links to the profile page', async () => {
    const user = renderMenu()
    await user.click(trigger())

    await user.click(screen.getByRole('link', { name: 'Профіль' }))

    expect(screen.getByText('Profile page')).toBeInTheDocument()
    expect(trigger()).toHaveAttribute('aria-expanded', 'false')
  })

  it('logs out and goes to the home page', async () => {
    logout.mockResolvedValue()
    const user = renderMenu()
    await user.click(trigger())

    await user.click(screen.getByRole('button', { name: 'Вийти' }))

    expect(logout).toHaveBeenCalledTimes(1)
    expect(await screen.findByText('Home page')).toBeInTheDocument()
  })

  it('goes to the home page even if the logout request fails', async () => {
    logout.mockRejectedValue(new Error('Network error'))
    const user = renderMenu()
    await user.click(trigger())

    await user.click(screen.getByRole('button', { name: 'Вийти' }))

    expect(await screen.findByText('Home page')).toBeInTheDocument()
  })
})
