import { Link } from 'react-router-dom'

import styles from './BannerSection.module.css'
import type { BannerSectionData } from './types'

interface BannerSectionProps {
  data: BannerSectionData | null
}

export default function BannerSection({ data }: BannerSectionProps) {
  if (!data) {
    return null
  }

  const { title, cta_text, cta_url } = data

  return (
    <section aria-labelledby="banner-title" className={styles.section}>
      <div className={`container ${styles.inner}`}>
        <h2 id="banner-title" className={styles.title}>
          {title}
        </h2>
        {/* The button is optional: both fields are blank-able in the admin */}
        {cta_text && cta_url && (
          <Link to={cta_url} className="button">
            {cta_text}
          </Link>
        )}
      </div>
    </section>
  )
}
