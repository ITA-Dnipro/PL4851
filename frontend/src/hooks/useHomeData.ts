  import { useEffect, useState } from 'react'
  import { fetchStartups } from '../sections/landing/NewParticipantsSection/api'
  import type { StartupsListData } from '../sections/landing/NewParticipantsSection/types'

  const PAGE_SIZE = 8

  interface HomeData {
      startups: StartupsListData | null
      isLoading: boolean
      isLoadingMore: boolean
      error: string | null
      loadMore: () => void
}

export function useHomeData(): HomeData {

  const [startups, setStartups] = useState<StartupsListData | null>(null)
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)

    useEffect(() => {
    let isMounted = true

    fetchStartups(1, PAGE_SIZE)
      .then((data) => { if (isMounted) setStartups(data) })
      .catch((err) => { if (isMounted) setError(err instanceof Error ? err.message : 'Unknown error') })
      .finally(() => { if (isMounted) setIsLoading(false) })

    return () => { isMounted = false }
  }, [])

      function loadMore() {
      if (!startups?.next || isLoadingMore) return

      const nextPage = page + 1
      setIsLoadingMore(true)

      fetchStartups(nextPage, PAGE_SIZE)
        .then((data) => {
          setStartups((prev) =>
            prev ? { ...data, results: [...prev.results, ...data.results] } : data,
          )
          setPage(nextPage)
        })
        .catch((err) => setError(err instanceof Error ? err.message : 'Unknown error'))
        .finally(() => setIsLoadingMore(false))
    }

    return { startups, isLoading, isLoadingMore, error, loadMore }
  }
