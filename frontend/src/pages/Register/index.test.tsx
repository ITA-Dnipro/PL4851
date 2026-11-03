import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import Register from '.'
import { register } from '../../api/auth'
import { ApiError, NETWORK_ERROR_STATUS } from '../../api/client/errors'
import { NETWORK_ERROR_MESSAGE } from '../../utils/apiMessages'
import { EMAIL_TAKEN_MESSAGE, WEAK_PASSWORD_MESSAGE } from './errors'
import {
  PASSWORD_HINT,
  PASSWORD_RULES_MESSAGE,
  PASSWORDS_MISMATCH_MESSAGE,
  REQUIRED_MESSAGES,
} from './validation'

vi.mock('../../api/auth', () => ({ register: vi.fn() }))

type User = ReturnType<typeof userEvent.setup>

// Shows the email passed to the resend page
function ResendPage() {
  const location = useLocation()
  return <p>Resend for {(location.state as { email: string }).email}</p>
}

function renderRegister() {
  const user = userEvent.setup()
  render(
    <MemoryRouter initialEntries={['/register']}>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<p>Login page</p>} />
        <Route path="/resend-verification" element={<ResendPage />} />
      </Routes>
    </MemoryRouter>,
  )
  return user
}

async function fillForm(user: User) {
  await user.type(screen.getByRole('textbox', { name: 'Назва компанії' }), '  Handmade Co ')
  await user.type(screen.getByRole('textbox', { name: 'Електронна пошта' }), 'founder@example.com')
  await user.type(screen.getByLabelText('Пароль'), 'Craft-2026')
  await user.type(screen.getByLabelText('Повторіть пароль'), 'Craft-2026')
  await user.type(screen.getByRole('textbox', { name: 'Прізвище' }), 'Test')
  await user.type(screen.getByRole('textbox', { name: 'Ім’я' }), 'Andrii')
  await user.click(screen.getByRole('radio', { name: 'Стартап проєкт, який шукає інвестиції' }))
  await user.click(screen.getByRole('radio', { name: 'Фізична особа-підприємець' }))
}

const CREATED = { id: 12, email: 'founder@example.com', detail: 'Verification email sent.' }

function submit(user: User) {
  return user.click(screen.getByRole('button', { name: 'Зареєструватися' }))
}

function passwordInput() {
  return screen.getByLabelText('Пароль')
}

function confirmInput() {
  return screen.getByLabelText('Повторіть пароль')
}

describe('Register page', () => {
  it('shows the fields from the mockup', () => {
    renderRegister()

    for (const name of ['Назва компанії', 'Електронна пошта', 'Прізвище', 'Ім’я']) {
      expect(screen.getByRole('textbox', { name })).toBeRequired()
    }
    expect(passwordInput()).toHaveAttribute('type', 'password')
    expect(confirmInput()).toHaveAttribute('type', 'password')
    expect(passwordInput()).toHaveAccessibleDescription(PASSWORD_HINT)

    const role = screen.getByRole('group', { name: 'Кого ви представляєте?' })
    expect(within(role).getAllByRole('radio').map((radio) => radio.closest('label')?.textContent))
      .toEqual(['Зареєстрована компанія', 'Стартап проєкт, який шукає інвестиції'])
    const legalForm = screen.getByRole('group', {
      name: 'Який суб’єкт господарювання ви представляєте?',
    })
    expect(within(legalForm).getAllByRole('radio')).toHaveLength(2)

    expect(screen.getByRole('link', { name: 'правилами використання' })).toHaveAttribute(
      'href',
      '/terms',
    )
  })

  it('shows every required message and focuses the first field on submit', async () => {
    const user = renderRegister()

    await submit(user)

    for (const message of Object.values(REQUIRED_MESSAGES)) {
      expect(screen.getByText(message)).toBeInTheDocument()
    }
    expect(screen.getByRole('textbox', { name: 'Назва компанії' })).toHaveFocus()
  })

  it('focuses the first invalid field, not the first field', async () => {
    const user = renderRegister()
    await user.type(screen.getByRole('textbox', { name: 'Назва компанії' }), 'Handmade Co')

    await submit(user)

    expect(screen.getByRole('textbox', { name: 'Електронна пошта' })).toHaveFocus()
  })

  it('shows a field error only after leaving the field', async () => {
    const user = renderRegister()
    const companyName = screen.getByRole('textbox', { name: 'Назва компанії' })

    await user.click(companyName)
    expect(screen.queryByText(REQUIRED_MESSAGES.company_name)).not.toBeInTheDocument()

    await user.tab()

    expect(screen.getByText(REQUIRED_MESSAGES.company_name)).toBeInTheDocument()
    expect(companyName).toHaveAttribute('aria-invalid', 'true')
    expect(companyName).toHaveAccessibleDescription(REQUIRED_MESSAGES.company_name)
    expect(screen.queryByText(REQUIRED_MESSAGES.email)).not.toBeInTheDocument()
  })

  it('reports a password that breaks the rules', async () => {
    const user = renderRegister()

    await user.type(passwordInput(), 'craft-2026')
    await user.tab()

    expect(screen.getByText(PASSWORD_RULES_MESSAGE)).toBeInTheDocument()
  })

  it('updates the mismatch error when the first password changes', async () => {
    const user = renderRegister()
    await user.type(passwordInput(), 'Craft-2026')
    await user.type(confirmInput(), 'Craft-2027')
    await user.tab()
    expect(screen.getByText(PASSWORDS_MISMATCH_MESSAGE)).toBeInTheDocument()

    await user.clear(passwordInput())
    await user.type(passwordInput(), 'Craft-2027')

    expect(screen.queryByText(PASSWORDS_MISMATCH_MESSAGE)).not.toBeInTheDocument()
  })

  it('shows and hides each password separately', async () => {
    const user = renderRegister()
    const [showPassword, showConfirm] = screen.getAllByRole('button', { name: 'Показати пароль' })

    await user.click(showPassword)

    expect(passwordInput()).toHaveAttribute('type', 'text')
    expect(confirmInput()).toHaveAttribute('type', 'password')

    await user.click(screen.getByRole('button', { name: 'Приховати пароль' }))
    await user.click(showConfirm)

    expect(passwordInput()).toHaveAttribute('type', 'password')
    expect(confirmInput()).toHaveAttribute('type', 'text')
  })

  it('picks one option in each group', async () => {
    const user = renderRegister()
    const company = screen.getByRole('radio', { name: 'Зареєстрована компанія' })
    const startup = screen.getByRole('radio', { name: 'Стартап проєкт, який шукає інвестиції' })

    await user.click(company)
    await user.click(startup)

    expect(startup).toBeChecked()
    expect(company).not.toBeChecked()

    await user.click(screen.getByRole('radio', { name: 'Юридична особа' }))

    expect(screen.getByRole('radio', { name: 'Юридична особа' })).toBeChecked()
    expect(startup).toBeChecked()
  })

  it('clears a choice error once an option is picked', async () => {
    const user = renderRegister()
    await submit(user)
    expect(screen.getByText(REQUIRED_MESSAGES.role)).toBeInTheDocument()

    await user.click(screen.getByRole('radio', { name: 'Зареєстрована компанія' }))

    expect(screen.queryByText(REQUIRED_MESSAGES.role)).not.toBeInTheDocument()
    expect(screen.getByText(REQUIRED_MESSAGES.legal_form)).toBeInTheDocument()
  })

  it('limits the text length to what the backend stores', () => {
    renderRegister()

    expect(screen.getByRole('textbox', { name: 'Назва компанії' })).toHaveAttribute(
      'maxLength',
      '255',
    )
    expect(screen.getByRole('textbox', { name: 'Прізвище' })).toHaveAttribute('maxLength', '150')
  })

  describe('submitting', () => {
    afterEach(() => {
      vi.mocked(register).mockReset()
    })

    it('does not send an invalid form', async () => {
      const user = renderRegister()

      await submit(user)

      expect(register).not.toHaveBeenCalled()
    })

    it('sends the trimmed form and shows the next step', async () => {
      vi.mocked(register).mockResolvedValue(CREATED)
      const user = renderRegister()
      await fillForm(user)

      await submit(user)

      expect(register).toHaveBeenCalledWith({
        company_name: 'Handmade Co',
        email: 'founder@example.com',
        password: 'Craft-2026',
        password_confirm: 'Craft-2026',
        last_name: 'Test',
        first_name: 'Andrii',
        role: 'startup',
        legal_form: 'sole_proprietor',
      })
      expect(
        screen.getByRole('heading', { name: 'Реєстрація майже завершена' }),
      ).toBeInTheDocument()
      expect(screen.queryByRole('button', { name: 'Зареєструватися' })).not.toBeInTheDocument()
    })

    it('links from the next step to login and to resending the email', async () => {
      vi.mocked(register).mockResolvedValue(CREATED)
      const user = renderRegister()
      await fillForm(user)
      await submit(user)

      expect(screen.getByRole('link', { name: 'Повернутися до входу' })).toHaveAttribute(
        'href',
        '/login',
      )

      await user.click(screen.getByRole('link', { name: 'Надіслати ще раз' }))

      expect(screen.getByText('Resend for founder@example.com')).toBeInTheDocument()
    })

    it('disables the button while the request is in flight', async () => {
      let finish: (value: typeof CREATED) => void = () => {}
      vi.mocked(register).mockReturnValue(new Promise((resolve) => (finish = resolve)))
      const user = renderRegister()
      await fillForm(user)

      await submit(user)

      expect(screen.getByRole('button', { name: 'Реєстрація…' })).toBeDisabled()
      finish(CREATED)
      expect(
        await screen.findByRole('heading', { name: 'Реєстрація майже завершена' }),
      ).toBeInTheDocument()
    })

    it('shows a taken email under the field and focuses it', async () => {
      vi.mocked(register).mockRejectedValue(new ApiError(409, 'Conflict'))
      const user = renderRegister()
      await fillForm(user)

      await submit(user)

      const email = screen.getByRole('textbox', { name: 'Електронна пошта' })
      expect(screen.getByText(EMAIL_TAKEN_MESSAGE)).toBeInTheDocument()
      expect(email).toHaveFocus()
      expect(email).toHaveAttribute('aria-invalid', 'true')
    })

    it('hides the server error once the field changes', async () => {
      vi.mocked(register).mockRejectedValue(new ApiError(409, 'Conflict'))
      const user = renderRegister()
      await fillForm(user)
      await submit(user)

      await user.type(screen.getByRole('textbox', { name: 'Електронна пошта' }), 'x')

      expect(screen.queryByText(EMAIL_TAKEN_MESSAGE)).not.toBeInTheDocument()
    })

    it('shows backend field errors under the fields', async () => {
      vi.mocked(register).mockRejectedValue(
        new ApiError(400, 'Bad Request', { password: ['This password is too common.'] }),
      )
      const user = renderRegister()
      await fillForm(user)

      await submit(user)

      expect(screen.getByText(WEAK_PASSWORD_MESSAGE)).toBeInTheDocument()
      expect(screen.getByLabelText('Пароль')).toHaveFocus()
    })

    it('shows a lost connection above the button and keeps the form', async () => {
      vi.mocked(register).mockRejectedValue(new ApiError(NETWORK_ERROR_STATUS, 'Failed to fetch'))
      const user = renderRegister()
      await fillForm(user)

      await submit(user)

      expect(screen.getByRole('alert')).toHaveTextContent(NETWORK_ERROR_MESSAGE)
      expect(screen.getByRole('textbox', { name: 'Назва компанії' })).toHaveValue('  Handmade Co ')
      expect(screen.getByRole('button', { name: 'Зареєструватися' })).toBeEnabled()
    })
  })
})
