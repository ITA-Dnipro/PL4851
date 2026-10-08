import type { WhyWorthSectionData, WhyWorthItemData } from './types'
import styles from './styles.module.css'

interface WhyWorthSectionProps {
  data: WhyWorthSectionData | null
}

interface WhyWorthItemProps {
  data: WhyWorthItemData
}

export default function WhyWorthSection({ data }: WhyWorthSectionProps) {
  if (!data) {
    return null
  }

  return (
    <section aria-labelledby="why-worth-title" className={styles.section}>
      <div className="container">
        <h2 id="why-worth-title" className={styles.title}>
          {data.title}
        </h2>
        <ul className={styles.grid}>
          {data.items.map((item) => (
            <li key={item.title}>
              <WhyWorthItem data={item} />
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

function WhyWorthItem({ data }: WhyWorthItemProps) {
  const { title, desc } = data

  return (
    <article tabIndex={0} className={styles.card}>
      <h3 className={styles.cardTitle}>{title}</h3>
      <p className={styles.cardDesc}>{desc}</p>
    </article>
  )
}
