import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import Login from '.'
import { login } from '../../api/auth'
import type { LoginResponse } from '../../api/auth'
import { ApiError, NETWORK_ERROR_STATUS } from '../../api/errors'
import {
  INVALID_CREDENTIALS_MESSAGE,
  NETWORK_ERROR_MESSAGE,
  lockoutMessage,
} from './errors'
import { EMAIL_FORMAT_MESSAGE } from './validation'

vi.mock('../../api/auth', () => ({ login: vi.fn() }))

const EMAIL = 'founder@example.com'
const PASSWORD = 'secret'

const loginResponse: LoginResponse = {
  access: 'access-token',
  user: { id: 1, email: EMAIL, role: 'startup' },
}

function renderLogin() {
  const user = userEvent.setup()
  render(
    <MemoryRouter initialEntries={['/login']}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<p>Home page</p>} />
      </Routes>
    </MemoryRouter>,
  )
  return user
}

function submitButton() {
  return screen.getByRole('button', { name: 'Увійти' })
}

async function fillForm(user: ReturnType<typeof userEvent.setup>, email = EMAIL) {
  await user.type(screen.getByLabelText('Електронна пошта'), email)
  await user.type(screen.getByLabelText('Пароль'), PASSWORD)
}

describe('Login page', () => {
  afterEach(() => {
    vi.mocked(login).mockReset()
  })

  it('keeps the submit button disabled until the form is valid', async () => {
    const user = renderLogin()

    expect(submitButton()).toBeDisabled()

    await fillForm(user)

    expect(submitButton()).toBeEnabled()
  })

  it('shows the email error only after leaving the field', async () => {
    const user = renderLogin()
    const email = screen.getByLabelText('Електронна пошта')

    await user.type(email, 'exgmail.com')
    expect(screen.queryByText(EMAIL_FORMAT_MESSAGE)).not.toBeInTheDocument()

    await user.tab()
    expect(screen.getByText(EMAIL_FORMAT_MESSAGE)).toBeInTheDocument()
    expect(email).toHaveAttribute('aria-invalid', 'true')

    await user.clear(email)
    await user.type(email, EMAIL)
    expect(screen.queryByText(EMAIL_FORMAT_MESSAGE)).not.toBeInTheDocument()
  })

  it('shows and hides the password', async () => {
    const user = renderLogin()
    const password = screen.getByLabelText('Пароль')

    expect(password).toHaveAttribute('type', 'password')

    await user.click(screen.getByRole('button', { name: 'Показати пароль' }))
    expect(password).toHaveAttribute('type', 'text')

    await user.click(screen.getByRole('button', { name: 'Приховати пароль' }))
    expect(password).toHaveAttribute('type', 'password')
  })

  it('sends the trimmed email with "remember me" and goes to the home page', async () => {
    vi.mocked(login).mockResolvedValue(loginResponse)
    const user = renderLogin()

    await fillForm(user, `  ${EMAIL} `)
    await user.click(screen.getByRole('checkbox', { name: 'Запам’ятати мене' }))
    await user.click(submitButton())

    expect(await screen.findByText('Home page')).toBeInTheDocument()
    expect(login).toHaveBeenCalledWith({ email: EMAIL, password: PASSWORD, remember: true })
  })

  it('disables the button while the request is in progress', async () => {
    // Never resolves, so the page stays in the loading state
    vi.mocked(login).mockReturnValue(new Promise(() => {}))
    const user = renderLogin()

    await fillForm(user)
    await user.click(submitButton())

    expect(screen.getByRole('button', { name: 'Вхід…' })).toBeDisabled()
  })

  it('shows the credentials error and hides it once the user edits the form', async () => {
    vi.mocked(login).mockRejectedValue(new ApiError(401, 'Invalid email or password'))
    const user = renderLogin()

    await fillForm(user)
    await user.click(submitButton())

    expect(await screen.findByText(INVALID_CREDENTIALS_MESSAGE)).toBeInTheDocument()
    expect(submitButton()).toBeEnabled()

    await user.type(screen.getByLabelText('Пароль'), '1')
    expect(screen.queryByText(INVALID_CREDENTIALS_MESSAGE)).not.toBeInTheDocument()
  })

  it.each([
    [new ApiError(429, 'Too many attempts', {}, 900), lockoutMessage(900)],
    [new ApiError(NETWORK_ERROR_STATUS, 'Network error'), NETWORK_ERROR_MESSAGE],
  ])('shows a message when the login fails: %s', async (error, message) => {
    vi.mocked(login).mockRejectedValue(error)
    const user = renderLogin()

    await fillForm(user)
    await user.click(submitButton())

    expect(await screen.findByText(message)).toBeInTheDocument()
  })

  it('links to password recovery and registration', () => {
    renderLogin()

    expect(screen.getByRole('link', { name: 'Забули пароль?' })).toHaveAttribute(
      'href',
      '/forgot-password',
    )
    expect(screen.getByRole('link', { name: 'Зареєструйтесь' })).toHaveAttribute(
      'href',
      '/register',
    )
  })
})
