import styles from './Hero.module.css';
import { useHeroContent } from '../../hooks/useHeroContent'

export default function Hero() {

  const { title, subtitle, buttonLabel, collage } = useHeroContent()

  return (
    <section className={styles.hero}>
      <div className={`container ${styles.inner}`}>
        <div className={styles.text}>
          <h1 className={styles.title}>{title}</h1>
          <p className={styles.subtitle}>{subtitle}</p>
          <a href="/register" className={`button ${styles.button}`}>
            {buttonLabel}
          </a>
        </div>

        <div className={styles.collage}>
          {collage.map((item) => (
            <figure key={item.key} className={`${styles.card} ${styles[item.key]}`}>
              <img src={item.imageUrl} alt={item.alt ?? item.label} loading="lazy" />
              <figcaption className={styles.label}>{item.label}</figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}