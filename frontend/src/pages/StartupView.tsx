import { faEnvelope, faStar, faUserPlus } from '@fortawesome/free-solid-svg-icons'
import type { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { ApiError } from '../api/client/errors'
import {
  fetchStartupProfile,
  fetchStartupProjects,
  updateStartupFollow,
  updateStartupSave,
  type StartupProfile,
  type StartupProject, } from '../api/startups'
import Icon from '../components/Icon'
import NotFound from './NotFound'
import styles from './StartupView.module.css'
import { About } from '../components/About'
import { ProductsList } from '../components/ProductsList'
// import { Story } from '../components/Story'

type ProfileState =
  | { status: 'loading' }
  | { status: 'success'; profile: StartupProfile }
  | { status: 'not-found' }
  | { status: 'error' }

// Same characters as an id or a Django slug: any other link can't be a profile
const LINK_PATTERN = /^[\w-]+$/
// The backend reads a link made only of digits as an id
const ID_PATTERN = /^\d+$/

function StartupView() {
  const { slug = '' } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const { state, retry } = useProfile(slug)

  const [projectResult, setProjectResult] = useState<{
    startupId: number
    projects: StartupProject[]
  } | null>(null)
  const requestIdRef = useRef(0)

  const startupStatus = state.status
  const startupId = startupStatus === 'success' ? state.profile.startup_id : undefined
  const projects =
    startupId !== undefined && projectResult?.startupId === startupId
      ? projectResult.projects
      : []

  useEffect(() => {
    if (startupStatus !== 'success' || startupId == null) {
      return
    }

    const requestId = ++requestIdRef.current
    const controller = new AbortController()

    fetchStartupProjects(startupId, controller.signal)
      .then((data) => {
        if (requestId !== requestIdRef.current) {
          return
        }

        setProjectResult({ startupId, projects: data ?? [] })
      })
      .catch((error) => {
        if (requestId !== requestIdRef.current) {
          return
        }

        if (!controller.signal.aborted) {
          console.error('Помилка завантаження проєктів:', error)
        }
      })

  return () => {
    controller.abort()
  }
}, [startupId, startupStatus])

  const loadedSlug = state.status === 'success' ? state.profile.slug : null

  // A profile opened by id (/startups/11) moves to its slug link (/startups/handmade-co).
  // "replace" keeps the id link out of the history, so "Back" leaves the profile.
  // A slug of digits ("123") isn't used: /startups/123 would open the startup with id 123
  useEffect(() => {
    if (loadedSlug && loadedSlug !== slug && !ID_PATTERN.test(loadedSlug)) {
      navigate(`/startups/${loadedSlug}`, { replace: true })
    }
  }, [loadedSlug, slug, navigate])

  if (state.status === 'loading') {
    return <ProfileSkeleton />
  }

  if (state.status === 'not-found') {
    return <NotFound />
  }

  if (state.status === 'error') {
    return (
      <section className={`container ${styles.error}`} role="alert">
        <p>Не вдалося завантажити профіль. Спробуйте ще раз</p>
        <button type="button" className={`button ${styles.retry}`} onClick={retry}>
          Спробувати ще раз
        </button>
      </section>
    )
  }

  const { profile } = state

  // backend doesn`t return story section yet
  //const storySections =
  //  Array.isArray(profile.story_section) && profile.story_section.length > 0
  //    ? profile.story_section
  //    : []

  return (
    <>
      <ProfileHeader key={profile.startup_id} profile={profile} />

      <div className={`container ${styles.layout}`}>
        <div>
          {profile.short_description && <p className={styles.lead}>{profile.short_description}</p>}

          {profile.about_html && <About aboutHtml={profile.about_html} />}
          {projects.length > 0 && <ProductsList products={projects} />}
          {/* {storySections.length > 0 && <Story sections={storySections} />} */}

          {/* This keeps original main structure intact, but feature blocks are mounted conditionally */}
        </div>

        <ProfileSidebar profile={profile} />
      </div>
    </>
  )
}

// The result remembers which link and attempt it belongs to: until they match,
// the page shows the loader instead of a stale profile
interface ProfileResult {
  slug: string
  attempt: number
  state: ProfileState
}

function useProfile(slug: string) {
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState<ProfileResult | null>(null)
  const isValidLink = LINK_PATTERN.test(slug)
  // After the move from the id link to the slug link the loaded profile still fits,
  // so it isn't requested again. A link of digits is always an id, never a slug
  const isCurrent =
    result !== null &&
    result.attempt === attempt &&
    (result.slug === slug ||
      (result.state.status === 'success' &&
        !ID_PATTERN.test(slug) &&
        result.state.profile.slug === slug))

  useEffect(() => {
    if (!isValidLink || isCurrent) {
      return
    }

    const controller = new AbortController()
    fetchStartupProfile(slug, controller.signal)
      .then((profile) => setResult({ slug, attempt, state: { status: 'success', profile } }))
      .catch((error: unknown) => {
        // Aborted when the page is left or another profile is opened
        if (controller.signal.aborted) {
          return
        }
        const isNotFound = error instanceof ApiError && error.status === 404
        setResult({ slug, attempt, state: { status: isNotFound ? 'not-found' : 'error' } })
      })

    return () => controller.abort()
  }, [slug, attempt, isValidLink, isCurrent])

  let state: ProfileState = { status: 'loading' }
  if (!isValidLink) {
    state = { status: 'not-found' }
  } else if (isCurrent && result) {
    state = result.state
  }

  return { state, retry: () => setAttempt((prev) => prev + 1) }
}

function ProfileHeader({ profile }: { profile: StartupProfile }) {
  const { startup_name, hero_image, logo, location, industries } = profile
  const [isFollowing, setIsFollowing] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [isFollowPending, setIsFollowPending] = useState(false)
  const [isSavePending, setIsSavePending] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([])

  const toggleFollow = async () => {
    const nextFollowingState = !isFollowing
    setIsFollowPending(true)
    setActionError(null)

    try {
      const result = await updateStartupFollow(profile.startup_id, nextFollowingState)
      setIsFollowing(result.is_following)
    } catch {
      setActionError('Не вдалося змінити підписку. Спробуйте ще раз.')
    } finally {
      setIsFollowPending(false)
    }
  }

  const toggleSave = async () => {
    const nextSavedState = !isSaved
    setIsSavePending(true)
    setActionError(null)

    try {
      const result = await updateStartupSave(profile.startup_id, nextSavedState)
      setIsSaved(result.is_saved)
    } catch {
      setActionError('Не вдалося змінити збереження. Спробуйте ще раз.')
    } finally {
      setIsSavePending(false)
    }
  }

  const toggleIndustry = (industry: string) => {
    setSelectedIndustries((selected) =>
      selected.includes(industry)
        ? selected.filter((item) => item !== industry)
        : [...selected, industry],
    )
  }

  return (
    <section aria-labelledby="profile-name">
      <div className={styles.hero}>
        <img src={hero_image} alt="" className={styles.heroImage} />
      </div>

      <div className={styles.band}>
        <div className={`container ${styles.bandInner}`}>
          <div className={styles.logo}>
            <img src={logo} alt={`Логотип ${startup_name}`} />
          </div>

          <div className={styles.info}>
            <h1 id="profile-name" className={styles.name}>
              {startup_name}
            </h1>
            {location && <p className={styles.location}>{location}</p>}
            {industries?.length && industries.length > 0 && (
              <ul className={styles.tags} aria-label="Галузі">
                {industries.map((industry) => (
                  <li key={industry}>
                    <button
                      type="button"
                      className={`${styles.tag} ${styles.tagButton} ${
                        selectedIndustries.includes(industry) ? styles.tagSelected : ''
                      }`}
                      aria-pressed={selectedIndustries.includes(industry)}
                      onClick={() => toggleIndustry(industry)}
                    >
                      {industry}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className={styles.actionGroup}>
            <div className={styles.actions}>
              <ActionButton
                label={isFollowing ? 'Ви стежите' : 'Стежити'}
                icon={faUserPlus}
                pressed={isFollowing}
                disabled={isFollowPending}
                onClick={toggleFollow}
              />
              {profile.contact.email ? (
                <a className={styles.action} href={`mailto:${profile.contact.email}`}>
                  Написати
                  <Icon icon={faEnvelope} className={styles.actionIcon} />
                </a>
              ) : (
                <ActionButton label="Написати" icon={faEnvelope} disabled />
              )}
              <ActionButton
                label={isSaved ? 'Збережено' : 'Додати в збережені'}
                icon={faStar}
                pressed={isSaved}
                disabled={isSavePending}
                onClick={toggleSave}
              />
            </div>
            {actionError && (
              <p className={styles.followError} role="alert">
                {actionError}
              </p>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

function ActionButton({
  label,
  icon,
  pressed,
  disabled = false,
  onClick,
}: {
  label: string
  icon: IconDefinition
  pressed?: boolean
  disabled?: boolean
  onClick?: () => void
}) {
  return (
    <button
      type="button"
      className={`${styles.action} ${pressed ? styles.actionActive : ''}`}
      aria-pressed={pressed}
      disabled={disabled}
      onClick={onClick}
    >
      {label}
      <Icon icon={icon} className={styles.actionIcon} />
    </button>
  )
}

// Basic info card; copy buttons, tags and follow state come with #62
function ProfileSidebar({ profile }: { profile: StartupProfile }) {
  const { startup_name, website, contact, followers_count, projects_count } = profile
  const hasContacts = Boolean(website || contact.phone || contact.email)

  return (
    <aside className={styles.sidebar} aria-label="Інформація про компанію">
      <dl className={styles.group}>
        <InfoRow label="Повна назва">{startup_name}</InfoRow>
        <InfoRow label="Підписники">{followers_count}</InfoRow>
        <InfoRow label="Проєкти">{projects_count}</InfoRow>
      </dl>

      {hasContacts && (
        <dl className={styles.group}>
          {website && (
            <InfoRow label="Сайт">
              <a href={website} target="_blank" rel="noopener noreferrer" className={styles.website}>
                {/* "https://www.example.com/" is shown as "example.com", like in the mockup */}
                {website.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')}
              </a>
            </InfoRow>
          )}
          {contact.phone && (
            <InfoRow label="Телефон">
              <a href={`tel:${contact.phone}`}>{contact.phone}</a>
            </InfoRow>
          )}
          {contact.email && (
            <InfoRow label="Електронна пошта">
              <a href={`mailto:${contact.email}`}>{contact.email}</a>
            </InfoRow>
          )}
        </dl>
      )}
    </aside>
  )
}

function InfoRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className={styles.row}>
      <dt>{label}</dt>
      <dd className={styles.value}>{children}</dd>
    </div>
  )
}

// Gray blocks in the shape of the page, so nothing jumps when the profile arrives
function ProfileSkeleton() {
  return (
    <div role="status">
      <span className={styles.hiddenText}>Завантаження профілю…</span>
      <div className={`${styles.hero} ${styles.placeholder}`} />

      <div className={styles.band}>
        <div className={`container ${styles.bandInner}`}>
          <div className={`${styles.logo} ${styles.placeholder}`} />
          <div className={styles.info}>
            <div className={`${styles.placeholder} ${styles.placeholderName}`} />
            <div className={`${styles.placeholder} ${styles.placeholderTags}`} />
          </div>
        </div>
      </div>

      <div className={`container ${styles.layout}`}>
        <div className={`${styles.placeholder} ${styles.placeholderText}`} />
        <div className={`${styles.placeholder} ${styles.placeholderCard}`} />
      </div>
    </div>
  )
}

export default StartupView
