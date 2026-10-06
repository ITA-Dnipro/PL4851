import { useEffect, useState } from 'react'
import { API_URL } from '../config'
import { heroMock } from '../data/heroMock'
import type { HeroContent } from '../types/content'

export function useHeroContent(): HeroContent {
  const [content, setContent] = useState<HeroContent>(heroMock)

  useEffect(() => {
    const controller = new AbortController()

    fetch(`${API_URL}/api/content/landing/`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        if (data?.hero) setContent(data.hero as HeroContent)
      })
      .catch(() => {

      })

    return () => controller.abort()
  }, [])

  return content
}