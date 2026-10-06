import Icon from '../../../components/Icon'

import styles from './ForWhomSection.module.css'
import { getForWhomIcon } from './icons'
import type { ForWhomItemData, ForWhomSectionData } from './types'

interface ForWhomSectionProps {
  data: ForWhomSectionData | null
}

interface ForWhomItemProps {
  data: ForWhomItemData
}

export default function ForWhomSection({ data }: ForWhomSectionProps) {
  if (!data) {
    return null
  }

  return (
    <section aria-labelledby="for-whom-title" className={styles.section}>
      <div className="container">
        <h2 id="for-whom-title" className={styles.title}>
          {data.title}
        </h2>
        <ul className={styles.grid}>
          {data.items.map((item) => (
            <li key={item.title}>
              <ForWhomItem data={item} />
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

function ForWhomItem({ data }: ForWhomItemProps) {
  const { icon, title, desc } = data

  return (
    <article className={styles.card}>
      <Icon icon={getForWhomIcon(icon)} className={styles.icon} />
      <div>
        <h3 className={styles.cardTitle}>{title}</h3>
        {desc && <p className={styles.cardDesc}>{desc}</p>}
      </div>
    </article>
  )
}
