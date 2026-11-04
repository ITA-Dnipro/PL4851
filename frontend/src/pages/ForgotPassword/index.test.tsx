import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import ForgotPassword from '.'
import { requestPasswordReset } from '../../api/auth'
import { ApiError, NETWORK_ERROR_STATUS } from '../../api/client/errors'
import { NETWORK_ERROR_MESSAGE, UNKNOWN_ERROR_MESSAGE } from '../Login/errors'
import { EMAIL_FORMAT_MESSAGE, EMAIL_REQUIRED_MESSAGE } from '../Login/validation'
import { TOO_MANY_REQUESTS_MESSAGE } from './errors'

vi.mock('../../api/auth', () => ({
  requestPasswordReset: vi.fn(),
}))

const EMAIL = 'founder@example.com'
const SUCCESS_TITLE = 'Відновлення пароля майже завершено'
const SUCCESS_TEXT = 'На вашу електронну адресу були надіслані інструкції для зміни пароля.'

function renderForgotPassword(url = '/forgot-password') {
  const user = userEvent.setup()
  render(
    <MemoryRouter initialEntries={[url]}>
      <ForgotPassword />
    </MemoryRouter>,
  )
  return user
}

function emailInput() {
  return screen.getByLabelText('Електронна пошта')
}

function submitButton() {
  return screen.getByRole('button', { name: 'Відновити пароль' })
}

// Submits directly: the disabled button can't be clicked, but the handler must still refuse
function submitForm() {
  fireEvent.submit(screen.getByRole('form', { name: 'Забули пароль?' }))
}

describe('ForgotPassword page', () => {
  afterEach(() => {
    vi.mocked(requestPasswordReset).mockReset()
  })

  it('shows an empty form with a disabled button and a link back to login', () => {
    renderForgotPassword()

    expect(screen.getByRole('heading', { name: 'Забули пароль?' })).toBeInTheDocument()
    expect(emailInput()).toHaveValue('')
    expect(emailInput()).toBeRequired()
    expect(submitButton()).toBeDisabled()
    expect(screen.getByRole('alert')).toBeEmptyDOMElement()
    expect(screen.getByText(/Я згадав свій пароль/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Повернутися до входу' })).toHaveAttribute(
      'href',
      '/login',
    )
  })

  it('shows the format error after leaving the field and does not send the request', async () => {
    const user = renderForgotPassword()
    const email = emailInput()

    await user.type(email, 'exgmail.com')
    expect(screen.getByRole('alert')).toBeEmptyDOMElement()

    await user.tab()
    expect(screen.getByRole('alert')).toHaveTextContent(EMAIL_FORMAT_MESSAGE)
    expect(email).toHaveAttribute('aria-invalid', 'true')
    expect(email).toHaveAccessibleDescription(EMAIL_FORMAT_MESSAGE)
    expect(submitButton()).toBeDisabled()

    submitForm()
    expect(requestPasswordReset).not.toHaveBeenCalled()
  })

  it('asks for an email when the form is submitted empty', () => {
    renderForgotPassword()

    submitForm()

    expect(screen.getByRole('alert')).toHaveTextContent(EMAIL_REQUIRED_MESSAGE)
    expect(requestPasswordReset).not.toHaveBeenCalled()
  })

  it('sends the email and shows the success message', async () => {
    vi.mocked(requestPasswordReset).mockResolvedValue({ detail: 'Sent' })
    const user = renderForgotPassword()

    await user.type(emailInput(), EMAIL)
    await user.click(submitButton())

    expect(requestPasswordReset).toHaveBeenCalledExactlyOnceWith({ email: EMAIL })
    expect(await screen.findByRole('heading', { name: SUCCESS_TITLE })).toHaveFocus()
    expect(screen.getByRole('status')).toHaveTextContent(SUCCESS_TEXT)
    expect(screen.queryByLabelText('Електронна пошта')).not.toBeInTheDocument()
    expect(screen.queryByText(/Я згадав свій пароль/)).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Повернутися до входу' })).toHaveAttribute(
      'href',
      '/login',
    )
  })

  it('sends only one request while the first is pending', async () => {
    vi.mocked(requestPasswordReset).mockReturnValue(new Promise(() => {}))
    const user = renderForgotPassword()

    await user.type(emailInput(), EMAIL)
    await user.click(submitButton())

    expect(screen.getByRole('button', { name: 'Надсилання…' })).toBeDisabled()
    expect(emailInput()).toHaveAttribute('readonly')

    submitForm()
    expect(requestPasswordReset).toHaveBeenCalledTimes(1)
  })

  it.each([
    ['too many requests', new ApiError(429, 'Throttled', {}, 900), TOO_MANY_REQUESTS_MESSAGE],
    ['no connection', new ApiError(NETWORK_ERROR_STATUS, 'Network error'), NETWORK_ERROR_MESSAGE],
    ['a server error', new ApiError(500, 'Server error'), UNKNOWN_ERROR_MESSAGE],
  ])('keeps the form and shows a message for %s', async (_, error, message) => {
    vi.mocked(requestPasswordReset).mockRejectedValue(error)
    const user = renderForgotPassword()

    await user.type(emailInput(), EMAIL)
    await user.click(submitButton())

    expect(await screen.findByText(message)).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent(message)
    // The address itself is fine, so the field isn't marked invalid
    expect(emailInput()).toHaveAttribute('aria-invalid', 'false')
    expect(submitButton()).toBeEnabled()
  })

  it('marks the field invalid when the backend rejects the address, until it is edited', async () => {
    vi.mocked(requestPasswordReset).mockRejectedValue(
      new ApiError(400, 'Request failed with status 400', {
        email: ['Enter a valid email address.'],
      }),
    )
    const user = renderForgotPassword()
    const email = emailInput()

    // Passes our pattern, but Django wants at least two letters after the last dot
    await user.type(email, 'founder@example.c')
    await user.click(submitButton())

    expect(await screen.findByText(EMAIL_FORMAT_MESSAGE)).toBeInTheDocument()
    expect(email).toHaveAttribute('aria-invalid', 'true')

    await user.type(email, 'om')
    expect(screen.getByRole('alert')).toBeEmptyDOMElement()
    expect(email).toHaveAttribute('aria-invalid', 'false')
  })

  it('fills in the email from the link without sending it', () => {
    renderForgotPassword(`/forgot-password?email=${encodeURIComponent(EMAIL)}`)

    expect(emailInput()).toHaveValue(EMAIL)
    expect(submitButton()).toBeEnabled()
    expect(requestPasswordReset).not.toHaveBeenCalled()
  })

  it('shows the error at once when the email in the link is malformed', () => {
    renderForgotPassword('/forgot-password?email=founder')

    expect(emailInput()).toHaveValue('founder')
    expect(screen.getByRole('alert')).toHaveTextContent(EMAIL_FORMAT_MESSAGE)
  })
})
