import { Link } from 'react-router-dom'
import styles from './styles.module.css'
import type { StartupItem } from '../../sections/landing/NewParticipantsSection/types'

interface StartupCardProps {
  startup: StartupItem
}

export default function StartupCard({ startup }: StartupCardProps) {
  const { id, company_name, short_description, thumbnail_url, logoUrl, location, tags } = startup

  return (
      <article className={styles.card}>
      <Link to={`/startups/${id}`} className={styles.link}>
      <div className={styles.media}>
        {thumbnail_url &&
            <img src={thumbnail_url} alt={company_name} className={styles.image} loading="lazy" />
         }
        {logoUrl && (
            <span className={styles.logo}>
              <img src={logoUrl} alt="" />
            </span>
          )}
      </div>
        <div className={styles.body}>
          <p className={styles.description}>{short_description}</p>
          <h3 className={styles.name}>{company_name}</h3>
          <p className={styles.location}>{location}</p>
          <ul className={styles.tags}>
            {tags.map((tag) => (
              <li key={tag} className={styles.tag}>{tag}</li>
            ))}
          </ul>
        </div>
      </Link>
    </article>
  )
}
