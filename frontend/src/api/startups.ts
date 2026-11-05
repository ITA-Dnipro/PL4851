import { API_URL, BACKEND_ORIGIN } from '../config'
import { request } from './client/request'

export interface StartupStorySection {
  id: string
  title: string
  text: string
}

// Public profile from GET /api/startups/{id}/
export interface StartupProfile {
  startup_id: number
  startup_name: string
  slug: string
  hero_image: string
  logo: string
  short_description: string
  about_html?: string
  story_section?: StartupStorySection[]
  contact: { email: string; phone: string }
  website: string
  industries: string[]
  followers_count: number
  projects_count: number
  created_at: string
  // Not sent by the backend yet; shown once it is
  location?: string
}

export interface BackendProject {
  project_id: number
  project_title: string
  status: string
  logo: string | null
  short_description: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface StartupProject {
  id: number
  label: string
  description: string
}

export interface StartupFollowResponse {
  startup_id: number
  is_following: boolean
}

export interface StartupSaveResponse {
  startup_id: number
  is_saved: boolean
}

// Local mock for /api/startups/{id}/follow/ until the backend endpoint is available.
async function mockStartupAction<T>(
  createResponse: () => T,
): Promise<T> {
  return createResponse()
}

export async function updateStartupFollow(
  startupId: number,
  shouldFollow: boolean,
): Promise<StartupFollowResponse> {
  return mockStartupAction(() => ({ startup_id: startupId, is_following: shouldFollow }))
}

export async function updateStartupSave(
  startupId: number,
  shouldSave: boolean,
): Promise<StartupSaveResponse> {
  return mockStartupAction(() => ({ startup_id: startupId, is_saved: shouldSave }))
}

// The backend sends uploaded files as paths ("/media/thumbs/placeholder.jpg")
function toMediaUrl(path: string) {
  return /^https?:\/\//.test(path) ? path : `${BACKEND_ORIGIN}${path}`
}

// Takes the last part of the page link: the backend finds the profile by id or by slug
export async function fetchStartupProfile(idOrSlug: string, signal?: AbortSignal) {
  const profile = await request<StartupProfile>(`/startups/${idOrSlug}/`, { signal })
  return {
    ...profile,
    hero_image: toMediaUrl(profile.hero_image),
    logo: toMediaUrl(profile.logo),
  }
}

export async function fetchStartupProjects(
  startupId: number,
  signal?: AbortSignal,
): Promise<StartupProject[]> {
  const allProjects: BackendProject[] = []
  const endpoint = `/startups/${startupId}/projects/`
  let path: string | null = endpoint

  while (path) {
    const data: PaginatedResponse<BackendProject> | BackendProject[] =
      await request<PaginatedResponse<BackendProject> | BackendProject[]>(path, { signal })
    if (Array.isArray(data)) {
      allProjects.push(...data)
      break
    }

    allProjects.push(...data.results)
    path = data.next ? getApiPath(data.next) : null
  }

  return allProjects.map((project) => ({
    id: project.project_id,
    label: project.project_title,
    description: project.short_description,
  }))
}

function getApiPath(url: string): string {
  const apiUrl = new URL(API_URL)
  const nextUrl = new URL(url, apiUrl)
  const apiPath = apiUrl.pathname.replace(/\/$/, '')

  if (nextUrl.origin !== apiUrl.origin || !nextUrl.pathname.startsWith(`${apiPath}/`)) {
    throw new Error('The projects pagination URL is outside the configured API')
  }

  return `${nextUrl.pathname.slice(apiPath.length)}${nextUrl.search}`
}
