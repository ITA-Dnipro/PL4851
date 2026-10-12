import { Link } from 'react-router-dom'
  import StartupCard from '../../../components/StartupCard'
  import styles from './styles.module.css'
  import type { StartupsListData } from './types'
  import arrow from '../../../assets/arrow-right.svg'

  interface NewParticipantsSectionProps {
    data: StartupsListData | null
    isLoading: boolean
    onLoadMore: () => void
    isLoadingMore: boolean
  }

  export default function NewParticipantsSection({
      data,
      isLoading,
      onLoadMore,
      isLoadingMore
  }: NewParticipantsSectionProps) {

    if (isLoading) {
      return (
        <section className={styles.section}>
          <div className="container">
            <p className={styles.status}>Завантаження...</p>
          </div>
        </section>
      )
    }
    if (!data || data.results.length === 0) {
        return (
          <section className={styles.section}>
            <div className="container">
              <p className={styles.status}>Стартапів ще немає.</p>
            </div>
          </section>
        )
    }

    return (
      <section className={styles.section}>
        <div className="container">
          <div className={styles.head}>
            <h2 className={styles.title}>Нові учасники</h2>
            <Link to="/startups" className={styles.all}>
              Всі підприємства
              <img src={arrow} alt="" />
            </Link>
          </div>
          <ul className={styles.grid}>
            {data.results.map((startup) => (
              <li key={startup.id}>
                <StartupCard startup={startup} />
              </li>
            ))}
          </ul>
          {data.next && (
              <button type="button" className={styles.loadMore} onClick={onLoadMore} disabled={isLoadingMore}>
                {isLoadingMore ? 'Завантаження...' : 'Показати ще'}
              </button>
            )}
        </div>
      </section>
    )
  }
