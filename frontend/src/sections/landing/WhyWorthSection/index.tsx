import type { CSSProperties } from 'react'

import type { WhyWorthSectionData, WhyWorthItemData } from './types'

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
    <section aria-labelledby="why-worth-title" style={styles.section}>
      <div style={styles.container}>
        <h2 id="why-worth-title" style={styles.title}>
          {data.title}
        </h2>
        <ul style={styles.grid}>
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
    <article tabIndex={0} style={styles.card}>
      <h3 style={styles.cardTitle}>{title}</h3>
      <p style={styles.cardDesc}>{desc}</p>
    </article>
  )
}

// Temporary inline styles approximating the mockup, until the styling approach is chosen
const styles: Record<string, CSSProperties> = {
  section: {
    padding: '80px 0',
    background: '#ffffff',
  },
  container: {
    maxWidth: 1352,
    margin: '0 auto',
    padding: '0 24px',
  },
  title: {
    margin: '0 0 48px',
    fontSize: 40,
    fontWeight: 700,
    lineHeight: 1.2,
    textAlign: 'center',
    color: '#232424',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 24,
    margin: 0,
    padding: 0,
    listStyle: 'none',
  },
  card: {
    height: '100%',
    minHeight: 160,
    padding: '32px 24px',
    borderRadius: 4,
    background: '#F9F5EC',
  },
  cardTitle: {
    margin: '0 0 16px',
    fontSize: 20,
    fontWeight: 700,
    lineHeight: 1.3,
    color: '#232424',
  },
  cardDesc: {
    margin: 0,
    fontSize: 15,
    lineHeight: 1.4,
    color: '#232424',
  },
}
