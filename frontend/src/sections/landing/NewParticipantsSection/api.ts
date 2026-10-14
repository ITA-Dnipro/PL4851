import { API_URL, BACKEND_ORIGIN } from '../../../config'
  import type { ApiStartupItem, ApiStartupsListData, StartupItem, StartupsListData } from './types'

  function mapApiStartup(item: ApiStartupItem): StartupItem {
    const imageUrl = item.logo.startsWith('http') ? item.logo : `${BACKEND_ORIGIN}${item.logo}`
    return {
      id: item.startup_id,
      company_name: item.startup_name,
      short_description: item.short_description,
      thumbnail_url: imageUrl,
      logoUrl: imageUrl,
      location: item.location,
      tags: item.industries,
   }
}

 export async function fetchStartups(page: number, pageSize = 8): Promise<StartupsListData> {
    const response = await fetch(`${API_URL}/startups/?page=${page}&page_size=${pageSize}`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data: ApiStartupsListData = await response.json()
    return { ...data, results: data.results.map(mapApiStartup) }
  }
