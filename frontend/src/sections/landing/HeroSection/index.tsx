import { Link } from 'react-router-dom'
import styles from './styles.module.css'
import type { HeroSectionData } from './types'

interface HeroSectionProps {
  data: HeroSectionData | null
}

const imagePositions = [styles.wine, styles.delivery, styles.cheese, styles.packaging]

export default function HeroSection({ data }: HeroSectionProps) {

  if (!data) return null

  const { title, subtitle, cta_text, cta_url, hero_images } = data

  return (
    <section className={styles.hero}>
      <div className={`container ${styles.inner}`}>
        <div className={styles.text}>
          <h1 className={styles.title}>{title}</h1>
          <p className={styles.subtitle}>{subtitle}</p>
          <Link to={cta_url} className={`button ${styles.button}`}>
            {cta_text}
          </Link>
        </div>

        <div className={styles.collage}>
          {hero_images.map((image, index) => (
            <figure key={image.title} className={`${styles.card} ${imagePositions[index]}`}>
              <img src={image.url} alt={image.title} loading="lazy" />
              <figcaption className={styles.label}>{image.title}</figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  )
}