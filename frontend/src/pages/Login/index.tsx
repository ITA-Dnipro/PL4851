import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons'
import { useState } from 'react'
import type { SubmitEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import type { Location, To } from 'react-router-dom'

import Icon from '../../components/Icon'
import { useAuth } from '../../hooks/useAuth'
import styles from './styles.module.css'
import { getLoginErrorMessage } from './errors'
import { validateEmail, validatePassword } from './validation'

// Red border for an error, green once the field is checked and valid
function inputClassName(error: string | null, isChecked: boolean) {
  if (error) {
    return `${styles.input} ${styles.inputError}`
  }
  return isChecked ? `${styles.input} ${styles.inputValid}` : styles.input
}

function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  // ProtectedRoute passes the page the user tried to open
  const from = (location.state as { from?: Location } | null)?.from
  // The whole address, so query parameters and the hash survive the login
  const redirectTo: To = from
    ? { pathname: from.pathname, search: from.search, hash: from.hash }
    : '/'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  // A field shows its error only after the user has left it once
  const [touched, setTouched] = useState({ email: false, password: false })
  const [isSubmitting, setIsSubmitting] = useState(false)
  // A rejected login (wrong password, lockout, no connection), shown under the password
  const [serverError, setServerError] = useState<string | null>(null)

  const emailError = validateEmail(email)
  const passwordError = validatePassword(password)
  const isFormValid = !emailError && !passwordError

  const shownEmailError = touched.email ? emailError : null
  const shownPasswordError = touched.password ? passwordError : null
  const passwordMessage = shownPasswordError ?? serverError

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setTouched({ email: true, password: true })
    if (!isFormValid || isSubmitting) {
      return
    }

    setIsSubmitting(true)
    setServerError(null)
    try {
      await login({ email: email.trim(), password, remember })
      navigate(redirectTo, { replace: true })
    } catch (error) {
      setServerError(getLoginErrorMessage(error))
      setIsSubmitting(false)
    }
  }

  return (
    <section className={styles.page}>
      <div className={styles.card}>
        <h1 id="login-title" className={styles.title}>
          Вхід на платформу
        </h1>

        <form
          className={styles.form}
          aria-labelledby="login-title"
          noValidate
          onSubmit={handleSubmit}
        >
          <div className={styles.fields}>
            <div className={styles.field}>
              <label htmlFor="login-email" className={styles.label}>
                Електронна пошта
              </label>
              <input
                id="login-email"
                type="email"
                name="email"
                autoComplete="email"
                placeholder="Введіть свою електронну пошту"
                className={inputClassName(shownEmailError, touched.email)}
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value)
                  setServerError(null)
                }}
                onBlur={() => setTouched((prev) => ({ ...prev, email: true }))}
                aria-invalid={Boolean(shownEmailError)}
                aria-describedby={shownEmailError ? 'login-email-error' : undefined}
              />
              {shownEmailError && (
                <p id="login-email-error" className={styles.error}>
                  {shownEmailError}
                </p>
              )}
            </div>

            <div className={styles.field}>
              <label htmlFor="login-password" className={styles.label}>
                Пароль
              </label>
              <div className={styles.passwordWrapper}>
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  autoComplete="current-password"
                  placeholder="Введіть пароль"
                  className={`${inputClassName(shownPasswordError, touched.password)} ${styles.passwordInput}`}
                  value={password}
                  onChange={(event) => {
                    setPassword(event.target.value)
                    setServerError(null)
                  }}
                  onBlur={() => setTouched((prev) => ({ ...prev, password: true }))}
                  aria-invalid={Boolean(passwordMessage)}
                  aria-describedby={passwordMessage ? 'login-password-error' : undefined}
                />
                <button
                  type="button"
                  className={styles.toggle}
                  aria-label={showPassword ? 'Приховати пароль' : 'Показати пароль'}
                  onClick={() => setShowPassword((prev) => !prev)}
                >
                  <Icon icon={showPassword ? faEye : faEyeSlash} className={styles.toggleIcon} />
                </button>
              </div>
              {passwordMessage && (
                <p id="login-password-error" className={styles.error}>
                  {passwordMessage}
                </p>
              )}
            </div>

            <div className={styles.options}>
              <label className={styles.remember}>
                <input
                  type="checkbox"
                  name="remember"
                  checked={remember}
                  onChange={(event) => setRemember(event.target.checked)}
                />
                Запам’ятати мене
              </label>
              <Link to="/forgot-password" className={styles.forgot}>
                Забули пароль?
              </Link>
            </div>
          </div>

          <div className={styles.actions}>
            <button
              type="submit"
              className={`button ${styles.submit}`}
              disabled={!isFormValid || isSubmitting}
            >
              {isSubmitting ? 'Вхід…' : 'Увійти'}
            </button>
          </div>
        </form>
      </div>

      <p className={styles.register}>
        Вперше на нашому сайті?{' '}
        <Link to="/register" className={styles.registerLink}>
          Зареєструйтесь
        </Link>
      </p>
    </section>
  )
}

export default Login
