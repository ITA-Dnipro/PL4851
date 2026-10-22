import { BACKEND_ORIGIN } from '../config'
import { apiRequest } from './client'

// Public profile from GET /api/startups/{id}/
export interface StartupProfile {
  startup_id: number
  startup_name: string
  slug: string
  hero_image: string
  logo: string
  short_description: string
  about_html: string
  contact: { email: string; phone: string }
  website: string
  industries: string[]
  followers_count: number
  projects_count: number
  created_at: string
  // Not sent by the backend yet; shown once it is
  location?: string
}

// The backend sends uploaded files as paths ("/media/thumbs/placeholder.jpg")
function toMediaUrl(path: string) {
  return /^https?:\/\//.test(path) ? path : `${BACKEND_ORIGIN}${path}`
}

// Takes the last part of the page link: the backend finds the profile by id or by slug
export async function fetchStartupProfile(idOrSlug: string, signal?: AbortSignal) {
  const profile = await apiRequest<StartupProfile>(`/startups/${idOrSlug}/`, { signal })
  return {
    ...profile,
    hero_image: toMediaUrl(profile.hero_image),
    logo: toMediaUrl(profile.logo),
  }
}
