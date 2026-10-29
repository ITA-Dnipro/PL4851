import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons'
import { useState } from 'react'
import type { SubmitEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'

import { confirmPasswordReset } from '../../api/auth'
import { ApiError } from '../../api/client/errors'
import Icon from '../../components/Icon'
import styles from './styles.module.css'
import {
  validateNewPassword,
  validateConfirmPassword,
} from './validation'

function inputClassName(error: string | null, isChecked: boolean) {
  if (error) {
    return `${styles.input} ${styles.inputError}`
  }
  return isChecked ? `${styles.input} ${styles.inputValid}` : styles.input
}

function RestorePassword() {
  const location = useLocation()

  const params = new URLSearchParams(location.search)
  const hashParams = new URLSearchParams(location.hash.replace(/^#\??/, ''))

  const uid = params.get('uid') || hashParams.get('uid') || ''
  const token = params.get('token') || hashParams.get('token') || ''

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [touched, setTouched] = useState({
    password: false,
    confirmPassword: false,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  const [isSuccess, setIsSuccess] = useState(false)
  const [invalidToken, setInvalidToken] = useState(false)

  const passwordError = validateNewPassword(password)
  const confirmationError = validateConfirmPassword(password, confirmPassword)
  const isFormValid = !passwordError && !confirmationError && Boolean(uid && token)

  const shownPasswordError = touched.password ? passwordError : null
  const shownConfirmationError = touched.confirmPassword ? confirmationError : null

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setTouched({ password: true, confirmPassword: true })

    if (!isFormValid || isSubmitting) {
      return
    }

    setIsSubmitting(true)
    setServerError(null)

    try {
      await confirmPasswordReset({ uid, token, password })
      setIsSuccess(true)
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.fieldErrors.password?.length) {
          setServerError(error.fieldErrors.password.join(' '))
        } else if (
          error.status === 400 &&
          error.message === 'Invalid or expired token.'
        ) {
          setInvalidToken(true)
          setServerError('Посилання недійсне або термін його дії минув.')
        } else {
          setServerError(error.message)
        }
      } else {
        setServerError('Не вдалося змінити пароль. Спробуйте ще раз.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className={styles.page}>
      <div className={styles.card}>
        <h1 id="restore-password-title" className={styles.title}>
          Встановлення нового пароля
        </h1>

        {isSuccess ? (
          <>
            <p
              className={`${styles.message} ${styles.messageSuccess}`}
              role="status"
              aria-live="polite"
            >
              Пароль успішно змінено.
            </p>
            <div className={styles.actions}>
              <Link to="/login" className="button">
                Перейти до входу
              </Link>
            </div>
          </>
        ) : !uid || !token || invalidToken ? (
          <div className={styles.fields}>
            <p
              className={`${styles.messageError}`}
              role="alert"
              aria-live="assertive"
            >
              Посилання для відновлення пароля відсутнє або недійсне.
            </p>
            <Link to="/forgot-password" className={styles.footerLink}>
              Запросити нове посилання
            </Link>
          </div>
        ) : (
          <form
            aria-labelledby="restore-password-title"
            noValidate
            onSubmit={handleSubmit}
          >
            <div className={styles.fields}>
              <div className={styles.field}>
                <label htmlFor="restore-password" className={styles.label}>
                  Новий пароль
                </label>
                <div className={styles.passwordWrapper}>
                  <input
                    id="restore-password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    className={`${inputClassName(shownPasswordError, touched.password)} ${styles.passwordInput}`}
                    value={password}
                    onChange={(event) => {
                      setPassword(event.target.value)
                      setServerError(null)
                    }}
                    onBlur={() => {
                        if (password.length > 0) {
                            setTouched((prev) => ({ ...prev, password: true }))
                        }
                    }}
                    aria-invalid={Boolean(shownPasswordError)}
                    aria-describedby={
                      shownPasswordError
                        ? 'restore-password-error'
                        : 'restore-password-hint'
                    }

                  />
                  <button
                    type="button"
                    className={styles.toggle}
                    aria-label={showPassword ? 'Приховати пароль' : 'Показати пароль'}
                    onClick={() => setShowPassword((prev) => !prev)}
                  >
                    <Icon
                      icon={showPassword ? faEye : faEyeSlash}
                      className={styles.toggleIcon}
                    />
                  </button>
                </div>
                {shownPasswordError ? (
                  <p id="restore-password-error" className={styles.error}>
                    {shownPasswordError}
                  </p>
                ) : (
                  <p id="restore-password-hint" className={styles.hint}>
                    Щонайменше 8 символів. Не використовуйте поширені паролі.
                  </p>
                )}
              </div>

              <div className={styles.field}>
                <label htmlFor="restore-confirm-password" className={styles.label}>
                  Підтвердження пароля
                </label>
                <div className={styles.passwordWrapper}>
                  <input
                    id="restore-confirm-password"
                    type={showConfirmation ? 'text' : 'password'}
                    autoComplete="new-password"
                    className={`${inputClassName(shownConfirmationError, touched.confirmPassword)} ${styles.passwordInput}`}
                    value={confirmPassword}
                    onChange={(event) => {
                      setConfirmPassword(event.target.value)
                      setServerError(null)
                    }}
                    onBlur={() =>
                      setTouched((prev) => ({ ...prev, confirmPassword: true }))
                    }
                    aria-invalid={Boolean(shownConfirmationError)}
                    aria-describedby={
                      shownConfirmationError
                        ? 'restore-confirm-password-error'
                        : undefined
                    }
                  />
                  <button
                    type="button"
                    className={styles.toggle}
                    aria-label={
                      showConfirmation ? 'Приховати підтвердження' : 'Показати підтвердження'
                    }
                    onClick={() => setShowConfirmation((prev) => !prev)}
                  >
                    <Icon
                      icon={showConfirmation ? faEye : faEyeSlash}
                      className={styles.toggleIcon}
                    />
                  </button>
                </div>
                {shownConfirmationError && (
                  <p
                    id="restore-confirm-password-error"
                    className={styles.error}
                  >
                    {shownConfirmationError}
                  </p>
                )}
              </div>
            </div>

            {serverError && (
              <p
                className={`${styles.message} ${styles.messageError}`}
                role="alert"
                aria-live="assertive"
              >
                {serverError}
              </p>
            )}

            <div className={styles.actions}>
              <button
                type="submit"
                className={`button ${styles.submit}`}
                disabled={!isFormValid || isSubmitting}
              >
                {isSubmitting ? 'Збереження…' : 'Змінити пароль'}
              </button>
            </div>
          </form>
        )}
      </div>

      <p className={styles.footer}>
        <Link to="/login" className={styles.footerLink}>
          Повернутися до входу
        </Link>
      </p>
    </section>
  )
}

export default RestorePassword
