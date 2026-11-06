import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons'
import { useState } from 'react'
import type { SubmitEvent } from 'react'
import { Link } from 'react-router-dom'

import { register } from '../../api/auth'
import type { LegalForm, UserRole } from '../../api/auth'
import Icon from '../../components/Icon'
import styles from './styles.module.css'
import { getRegisterErrors } from './errors'
import { PASSWORD_HINT, REGISTER_FIELDS, validateRegisterForm } from './validation'
import type { RegisterErrors, RegisterField, RegisterFormValues } from './validation'

interface Option<T> {
  value: T
  label: string
}

const ROLE_OPTIONS: Option<UserRole>[] = [
  { value: 'investor', label: 'Зареєстрована компанія' },
  { value: 'startup', label: 'Стартап проєкт, який шукає інвестиції' },
]

const LEGAL_FORM_OPTIONS: Option<LegalForm>[] = [
  { value: 'sole_proprietor', label: 'Фізична особа-підприємець' },
  { value: 'legal_entity', label: 'Юридична особа' },
]

const INITIAL_VALUES: RegisterFormValues = {
  company_name: '',
  email: '',
  password: '',
  password_confirm: '',
  last_name: '',
  first_name: '',
  role: '',
  legal_form: '',
}

const NOTHING_TOUCHED = Object.fromEntries(
  REGISTER_FIELDS.map((field) => [field, false]),
) as Record<RegisterField, boolean>
const ALL_TOUCHED = Object.fromEntries(REGISTER_FIELDS.map((field) => [field, true])) as Record<
  RegisterField,
  boolean
>

function inputId(field: RegisterField) {
  return `register-${field}`
}

// A choice group gets the focus on its first option
function focusTargetId(field: RegisterField) {
  if (field === 'role') {
    return optionId(field, ROLE_OPTIONS[0].value)
  }
  if (field === 'legal_form') {
    return optionId(field, LEGAL_FORM_OPTIONS[0].value)
  }
  return inputId(field)
}

function optionId(field: RegisterField, value: string) {
  return `register-${field}-${value}`
}

interface TextFieldProps {
  field: RegisterField
  label: string
  placeholder: string
  value: string
  error?: string
  type?: 'text' | 'email' | 'password'
  autoComplete: string
  maxLength?: number
  hint?: string
  onChange: (value: string) => void
  onBlur: () => void
}

function TextField({
  field,
  label,
  placeholder,
  value,
  error,
  type = 'text',
  autoComplete,
  maxLength,
  hint,
  onChange,
  onBlur,
}: TextFieldProps) {
  const [showPassword, setShowPassword] = useState(false)
  const id = inputId(field)
  const hintId = `${id}-hint`
  const errorId = `${id}-error`
  const isPassword = type === 'password'
  const describedBy = [hint && hintId, error && errorId].filter(Boolean).join(' ')
  const className = [
    styles.input,
    error && styles.inputError,
    isPassword && styles.passwordInput,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={styles.field}>
      <label htmlFor={id} className={`${styles.label} ${styles.required}`}>
        {label}
      </label>
      {hint && (
        <p id={hintId} className={styles.hint}>
          {hint}
        </p>
      )}
      <div className={styles.inputWrapper}>
        <input
          id={id}
          name={field}
          type={isPassword && showPassword ? 'text' : type}
          required
          autoComplete={autoComplete}
          placeholder={placeholder}
          maxLength={maxLength}
          className={className}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onBlur={onBlur}
          aria-invalid={Boolean(error)}
          aria-describedby={describedBy || undefined}
        />
        {isPassword && (
          <button
            type="button"
            className={styles.toggle}
            aria-label={showPassword ? 'Приховати пароль' : 'Показати пароль'}
            onClick={() => setShowPassword((prev) => !prev)}
          >
            <Icon icon={showPassword ? faEye : faEyeSlash} className={styles.toggleIcon} />
          </button>
        )}
      </div>
      {error && (
        <p id={errorId} className={styles.error}>
          {error}
        </p>
      )}
    </div>
  )
}

interface ChoiceGroupProps<T extends string> {
  field: RegisterField
  legend: string
  options: Option<T>[]
  value: T | ''
  error?: string
  onChange: (value: T) => void
}

// One option of several; radio buttons drawn as the square boxes from the mockup
function ChoiceGroup<T extends string>({
  field,
  legend,
  options,
  value,
  error,
  onChange,
}: ChoiceGroupProps<T>) {
  const errorId = `register-${field}-error`

  return (
    <fieldset className={styles.choiceGroup} aria-describedby={error ? errorId : undefined}>
      <legend className={`${styles.legend} ${styles.required}`}>{legend}</legend>
      <div className={styles.choices}>
        {options.map((option) => (
          <label key={option.value} className={styles.choice}>
            <input
              id={optionId(field, option.value)}
              type="radio"
              name={field}
              required
              className={error ? `${styles.choiceInput} ${styles.choiceInputError}` : styles.choiceInput}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              aria-invalid={Boolean(error)}
            />
            {option.label}
          </label>
        ))}
      </div>
      {error && (
        <p id={errorId} className={styles.choiceError}>
          {error}
        </p>
      )}
    </fieldset>
  )
}

function focusField(field: RegisterField) {
  document.getElementById(focusTargetId(field))?.focus()
}

// The next step after the form: the user has to confirm the email from the letter
function RegistrationSent({ email }: { email: string }) {
  return (
    <section className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Реєстрація майже завершена</h1>
        <div className={styles.message} role="status">
          <p>
            На зазначену вами електронну пошту відправлено листа.
            <br />
            Будь ласка, перейдіть за посиланням з листа для підтвердження вказаної електронної
            адреси.
          </p>
          <p>
            Не отримали листа?{' '}
            {/* The resend page can fill in the email the user registered with */}
            <Link to="/resend-verification" state={{ email }} className={styles.termsLink}>
              Надіслати ще раз
            </Link>
          </p>
        </div>
        <div className={styles.actions}>
          <Link to="/login" className={`button ${styles.submit}`}>
            Повернутися до входу
          </Link>
        </div>
      </div>
    </section>
  )
}

function Register() {
  const [values, setValues] = useState(INITIAL_VALUES)
  // A field shows its error only after the user has left it or submitted the form
  const [touched, setTouched] = useState(NOTHING_TOUCHED)
  // Errors from the backend; a field's error goes away when the user changes it
  const [serverErrors, setServerErrors] = useState<RegisterErrors>({})
  // A rejected registration that isn't about one field (limit, no connection)
  const [formError, setFormError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  // Set after a successful registration: the form is replaced with the next step
  const [registeredEmail, setRegisteredEmail] = useState<string | null>(null)

  const errors = validateRegisterForm(values)

  function shownError(field: RegisterField) {
    return (touched[field] ? errors[field] : undefined) ?? serverErrors[field]
  }

  function setValue<F extends RegisterField>(field: F, value: RegisterFormValues[F]) {
    setValues((prev) => ({ ...prev, [field]: value }))
    setServerErrors((prev) => ({ ...prev, [field]: undefined }))
    setFormError(null)
  }

  function touch(field: RegisterField) {
    setTouched((prev) => ({ ...prev, [field]: true }))
  }

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setTouched(ALL_TOUCHED)

    const firstInvalid = REGISTER_FIELDS.find((field) => errors[field])
    if (firstInvalid) {
      focusField(firstInvalid)
      return
    }
    // The checks above guarantee both choices are picked
    if (isSubmitting || !values.role || !values.legal_form) {
      return
    }

    setIsSubmitting(true)
    setServerErrors({})
    setFormError(null)
    try {
      const response = await register({
        ...values,
        company_name: values.company_name.trim(),
        email: values.email.trim(),
        last_name: values.last_name.trim(),
        first_name: values.first_name.trim(),
        role: values.role,
        legal_form: values.legal_form,
      })
      setRegisteredEmail(response.email)
    } catch (error) {
      const rejected = getRegisterErrors(error)
      setServerErrors(rejected.fields)
      setFormError(rejected.form)
      const firstRejected = REGISTER_FIELDS.find((field) => rejected.fields[field])
      if (firstRejected) {
        focusField(firstRejected)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  function textFieldProps(field: Exclude<RegisterField, 'role' | 'legal_form'>) {
    return {
      field,
      value: values[field],
      error: shownError(field),
      onChange: (value: string) => setValue(field, value),
      onBlur: () => touch(field),
    }
  }

  if (registeredEmail) {
    return <RegistrationSent email={registeredEmail} />
  }

  return (
    <section className={styles.page}>
      <div className={styles.card}>
        <h1 id="register-title" className={styles.title}>
          Реєстрація
        </h1>

        <form
          className={styles.form}
          aria-labelledby="register-title"
          noValidate
          onSubmit={handleSubmit}
        >
          <div className={styles.fields}>
            <p className={`${styles.notice} ${styles.required}`}>
              Обов’язкові поля позначені зірочкою
            </p>

            <TextField
              {...textFieldProps('company_name')}
              label="Назва компанії"
              placeholder="Введіть назву вашої компанії"
              autoComplete="organization"
              maxLength={255}
            />
            <TextField
              {...textFieldProps('email')}
              label="Електронна пошта"
              placeholder="Введіть свою електронну пошту"
              type="email"
              autoComplete="email"
              maxLength={254}
            />
            <TextField
              {...textFieldProps('password')}
              label="Пароль"
              placeholder="Введіть пароль"
              type="password"
              autoComplete="new-password"
              hint={PASSWORD_HINT}
            />
            <TextField
              {...textFieldProps('password_confirm')}
              label="Повторіть пароль"
              placeholder="Введіть пароль ще раз"
              type="password"
              autoComplete="new-password"
            />
            <TextField
              {...textFieldProps('last_name')}
              label="Прізвище"
              placeholder="Введіть ваше прізвище"
              autoComplete="family-name"
              maxLength={150}
            />
            <TextField
              {...textFieldProps('first_name')}
              label="Ім’я"
              placeholder="Введіть ваше ім’я"
              autoComplete="given-name"
              maxLength={150}
            />

            <ChoiceGroup
              field="role"
              legend="Кого ви представляєте?"
              options={ROLE_OPTIONS}
              value={values.role}
              error={shownError('role')}
              onChange={(value) => {
                setValue('role', value)
                touch('role')
              }}
            />
            <ChoiceGroup
              field="legal_form"
              legend="Який суб’єкт господарювання ви представляєте?"
              options={LEGAL_FORM_OPTIONS}
              value={values.legal_form}
              error={shownError('legal_form')}
              onChange={(value) => {
                setValue('legal_form', value)
                touch('legal_form')
              }}
            />

            <p className={styles.terms}>
              Реєструючись, я погоджуюсь з{' '}
              <Link to="/terms" className={styles.termsLink}>
                правилами використання
              </Link>{' '}
              сайту Craftmerge
            </p>
          </div>

          <div className={styles.actions}>
            {formError && (
              <p className={styles.formError} role="alert">
                {formError}
              </p>
            )}
            <button type="submit" className={`button ${styles.submit}`} disabled={isSubmitting}>
              {isSubmitting ? 'Реєстрація…' : 'Зареєструватися'}
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}

export default Register
