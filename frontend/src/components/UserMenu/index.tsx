import { faCircleUser } from '@fortawesome/free-solid-svg-icons'
import { useEffect, useId, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import Icon from '../Icon'
import styles from './styles.module.css'

// "Мій профіль" button in the header with a dropdown for a signed-in user
export default function UserMenu() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const dropdownId = useId()
  const rootRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  // Close on a click outside the menu or on Escape
  useEffect(() => {
    if (!isOpen) {
      return
    }

    function handleClick(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false)
        buttonRef.current?.focus()
      }
    }

    document.addEventListener('mousedown', handleClick)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handleClick)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen])

  async function handleLogout() {
    setIsLoggingOut(true)
    // Leave the page before the session ends: on a protected page ProtectedRoute
    // would otherwise send the signed-out user to the login page
    navigate('/', { replace: true })
    try {
      await logout()
    } catch {
      // The session is cleared locally even if the request failed
    }
  }

  return (
    <div ref={rootRef} className={styles.menu}>
      <button
        ref={buttonRef}
        type="button"
        className={styles.trigger}
        aria-expanded={isOpen}
        aria-controls={dropdownId}
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <Icon icon={faCircleUser} className={styles.avatar} />
        Мій профіль
      </button>

      <ul id={dropdownId} className={styles.dropdown} hidden={!isOpen}>
        <li>
          <Link to="/profile" className={styles.item} onClick={() => setIsOpen(false)}>
            Профіль
          </Link>
        </li>
        <li>
          <button
            type="button"
            className={`${styles.item} ${styles.logout}`}
            onClick={handleLogout}
            disabled={isLoggingOut}
          >
            Вийти
          </button>
        </li>
      </ul>
    </div>
  )
}
