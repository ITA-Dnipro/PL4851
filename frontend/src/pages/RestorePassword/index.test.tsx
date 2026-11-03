import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import RestorePassword from '.'
import { confirmPasswordReset } from '../../api/auth'
import { ApiError } from '../../api/client/errors'

vi.mock('../../api/auth', () => ({
  confirmPasswordReset: vi.fn(),
}))

const PASSWORD = 'SecurePass123!'
const UID = 'test-uid'
const TOKEN = 'test-token'

function renderRestorePassword(
  url = `/reset-password?uid=${UID}&token=${TOKEN}`,
) {
  const user = userEvent.setup()

  render(
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route path="/reset-password" element={<RestorePassword />} />
        <Route path="/login" element={<p>Login page</p>} />
        <Route path="/forgot-password" element={<p>Forgot password page</p>} />
      </Routes>
    </MemoryRouter>,
  )

  return user
}

function submitButton() {
  return screen.getByRole('button', { name: 'Змінити пароль' })
}

async function fillForm(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText('Новий пароль'), PASSWORD)
  await user.type(screen.getByLabelText('Підтвердження пароля'), PASSWORD)
}

describe('RestorePassword page', () => {
  afterEach(() => {
    vi.mocked(confirmPasswordReset).mockReset()
  })

  it('shows the password form when uid and token are present in the URL', () => {
    renderRestorePassword()

    expect(screen.getByLabelText('Новий пароль')).toBeInTheDocument()
    expect(screen.getByLabelText('Підтвердження пароля')).toBeInTheDocument()
    expect(submitButton()).toBeDisabled()
  })

  it('shows an error and resend link when uid or token is missing', () => {
    renderRestorePassword('/reset-password?uid=test-uid')

    expect(screen.getByRole('alert')).toHaveTextContent(
      'Посилання для відновлення пароля відсутнє або недійсне.',
    )

    expect(
      screen.getByRole('link', { name: 'Запросити нове посилання' }),
    ).toHaveAttribute('href', '/forgot-password')

    expect(screen.queryByLabelText('Новий пароль')).not.toBeInTheDocument()
  })

  it('sends uid, token and password to the API', async () => {
    vi.mocked(confirmPasswordReset).mockResolvedValue({
      detail: 'Password has been reset.',
    })

    const user = renderRestorePassword()

    await fillForm(user)
    await user.click(submitButton())

    expect(confirmPasswordReset).toHaveBeenCalledExactlyOnceWith({
      uid: UID,
      token: TOKEN,
      password: PASSWORD,
    })
  })

  it('reads uid and token from the URL hash', async () => {
    vi.mocked(confirmPasswordReset).mockResolvedValue({
      detail: 'Password has been reset.',
    })

    const user = renderRestorePassword(
      '/reset-password#uid=hash-uid&token=hash-token',
    )

    await fillForm(user)
    await user.click(submitButton())

    expect(confirmPasswordReset).toHaveBeenCalledExactlyOnceWith({
      uid: 'hash-uid',
      token: 'hash-token',
      password: PASSWORD,
    })
  })

  it('shows success and a login link after password reset', async () => {
    vi.mocked(confirmPasswordReset).mockResolvedValue({
      detail: 'Password has been reset.',
    })

    const user = renderRestorePassword()

    await fillForm(user)
    await user.click(submitButton())

    expect(
      await screen.findByText('Пароль успішно змінено.'),
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: 'Перейти до входу' }),
    ).toHaveAttribute('href', '/login')

    expect(screen.queryByLabelText('Новий пароль')).not.toBeInTheDocument()
  })

  it('shows a resend link when the token is invalid or expired', async () => {
    vi.mocked(confirmPasswordReset).mockRejectedValue(
      new ApiError(400, 'Invalid or expired token.'),
    )

    const user = renderRestorePassword()

    await fillForm(user)
    await user.click(submitButton())

    expect(
      await screen.findByRole('alert'),
    ).toHaveTextContent(
      'Посилання для відновлення пароля відсутнє або недійсне.',
    )

    expect(
      screen.getByRole('link', { name: 'Запросити нове посилання' }),
    ).toHaveAttribute('href', '/forgot-password')
  })

  it('shows password complexity errors returned by the backend', async () => {
    vi.mocked(confirmPasswordReset).mockRejectedValue(
      new ApiError(
        422,
        'Validation error',
        { password: ['This password is too common.'] },
      ),
    )

    const user = renderRestorePassword()

    await fillForm(user)
    await user.click(submitButton())

    expect(
      await screen.findByRole('alert'),
    ).toHaveTextContent('This password is too common.')

    expect(submitButton()).toBeEnabled()
  })

  it('disables the submit button while the request is pending', async () => {
    vi.mocked(confirmPasswordReset).mockReturnValue(
      new Promise(() => {}),
    )

    const user = renderRestorePassword()

    await fillForm(user)
    await user.click(submitButton())

    expect(
      screen.getByRole('button', { name: 'Збереження…' }),
    ).toBeDisabled()

    expect(confirmPasswordReset).toHaveBeenCalledTimes(1)
  })
})
