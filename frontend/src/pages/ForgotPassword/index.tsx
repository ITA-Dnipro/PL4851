import { useEffect, useRef, useState } from 'react'
import type { SubmitEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { requestPasswordReset } from '../../api/auth'
import { validateEmail } from '../Login/validation'
import styles from './styles.module.css'
import { getResetRequestFailure } from './errors'
import type { ResetRequestFailure } from './errors'

type Status = 'idle' | 'submitting' | 'success'

// Red border for an invalid email, green once the field is checked and valid
function inputClassName(isInvalid: boolean, isChecked: boolean) {
  if (isInvalid) {
    return `${styles.input} ${styles.inputError}`
  }
  return isChecked ? `${styles.input} ${styles.inputValid}` : styles.input
}

function ForgotPassword() {
  // ?email=... fills in the address, so other pages can link here with it
  const [searchParams] = useSearchParams()
  const prefill = searchParams.get('email')?.trim() ?? ''
  const [email, setEmail] = useState(prefill)
  // The field shows its error only after the user has left it once; a prefilled one at once
  const [touched, setTouched] = useState(prefill !== '')
  const [status, setStatus] = useState<Status>('idle')
  // A failed request (rejected address, too many requests, no connection)
  const [serverError, setServerError] = useState<ResetRequestFailure | null>(null)
  const titleRef = useRef<HTMLHeadingElement>(null)

  const emailError = validateEmail(email)
  const isSubmitting = status === 'submitting'
  const isSuccess = status === 'success'

  const shownEmailError = touched ? emailError : null
  // Only a wrong address turns the field red; other failures just show their text
  const isEmailInvalid = Boolean(shownEmailError || serverError?.invalidEmail)
  const message = shownEmailError ?? serverError?.message ?? ''

  // The form is replaced by the success text: focus the new title so it gets read out
  useEffect(() => {
    if (isSuccess) {
      titleRef.current?.focus()
    }
  }, [isSuccess])

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setTouched(true)
    if (emailError || isSubmitting) {
      return
    }

    setStatus('submitting')
    setServerError(null)
    try {
      await requestPasswordReset({ email: email.trim() })
      setStatus('success')
    } catch (error) {
      setServerError(getResetRequestFailure(error))
      setStatus('idle')
    }
  }

  return (
    <section className={styles.page}>
      <div className={styles.card}>
        <h1 id="forgot-password-title" ref={titleRef} tabIndex={-1} className={styles.title}>
          {isSuccess ? 'Відновлення пароля майже завершено' : 'Забули пароль?'}
        </h1>

        {isSuccess ? (
          <>
            <div className={styles.fields}>
              <p className={styles.text}>
                На вашу електронну адресу були надіслані інструкції для зміни пароля.
              </p>
            </div>
            <div className={styles.actions}>
              <Link to="/login" className="button">
                Повернутися до входу
              </Link>
            </div>
          </>
        ) : (
          <form aria-labelledby="forgot-password-title" noValidate onSubmit={handleSubmit}>
            <div className={styles.fields}>
              <p className={`${styles.text} ${styles.intro}`}>
                Введіть електронну адресу, вказану при реєстрації, для відновлення пароля.
                <br />
                На зазначену вами електронну пошту буде відправлено листа з посиланням для
                відновлення пароля.
              </p>

              <div className={styles.field}>
                <label htmlFor="forgot-password-email" className={styles.label}>
                  Електронна пошта
                </label>
                <input
                  id="forgot-password-email"
                  type="email"
                  name="email"
                  autoComplete="email"
                  placeholder="Введіть свою електронну пошту"
                  className={inputClassName(isEmailInvalid, touched && !serverError)}
                  value={email}
                  // A late answer would otherwise be shown against an edited address
                  readOnly={isSubmitting}
                  onChange={(event) => {
                    setEmail(event.target.value)
                    setServerError(null)
                  }}
                  onBlur={() => setTouched(true)}
                  aria-invalid={isEmailInvalid}
                  aria-describedby={message ? 'forgot-password-email-message' : undefined}
                />
                {/* Always rendered, so screen readers announce the text when it appears */}
                <p id="forgot-password-email-message" role="alert" className={styles.error}>
                  {message}
                </p>
              </div>
            </div>

            <div className={styles.actions}>
              <button
                type="submit"
                className={`button ${styles.submit}`}
                disabled={Boolean(emailError) || isSubmitting}
              >
                {isSubmitting ? 'Надсилання…' : 'Відновити пароль'}
              </button>
            </div>
          </form>
        )}
      </div>

      {!isSuccess && (
        <p className={styles.footer}>
          Я згадав свій пароль.{' '}
          <Link to="/login" className={styles.footerLink}>
            Повернутися до входу
          </Link>
        </p>
      )}
    </section>
  )
}

export default ForgotPassword
