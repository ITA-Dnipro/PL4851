import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_URL } from '../config'
import { jsonResponse, mockFetch } from '../test/http'
import { ApiError } from './client/errors'
import { fetchStartupProjects } from './startups'
import type { BackendProject, PaginatedResponse, StartupProject } from './startups'

const projects: BackendProject[] = Array.from({ length: 8 }, (_, index) => ({
  project_id: index + 1,
  project_title: `Project ${index + 1}`,
  status: 'active',
  logo: null,
  short_description: `Description ${index + 1}`,
}))

const startupProjects: StartupProject[] = projects.map((project) => ({
  id: project.project_id,
  label: project.project_title,
  description: project.short_description,
}))

function page(results: BackendProject[], next: string | null): PaginatedResponse<BackendProject> {
  return { count: projects.length, previous: null, next, results }
}

describe('fetchStartupProjects', () => {
  afterEach(() => vi.restoreAllMocks())

  it('returns every page and preserves the pagination query supplied by the backend', async () => {
    const next = `${API_URL}/startups/11/projects/?page=2&page_size=6`
    const fetchMock = mockFetch(jsonResponse(page(projects.slice(0, 6), next)))
      .mockResolvedValueOnce(jsonResponse(page(projects.slice(0, 6), next)))
      .mockResolvedValueOnce(jsonResponse(page(projects.slice(6), null)))
    const controller = new AbortController()

    await expect(fetchStartupProjects(11, controller.signal)).resolves.toEqual(startupProjects)

    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock).toHaveBeenNthCalledWith(1, `${API_URL}/startups/11/projects/`,
      expect.objectContaining({ signal: controller.signal }))
    expect(fetchMock).toHaveBeenNthCalledWith(2, next,
      expect.objectContaining({ signal: controller.signal }))
  })

  it('returns an empty list when there are no projects', async () => {
    const fetchMock = mockFetch(jsonResponse(page([], null)))

    await expect(fetchStartupProjects(11)).resolves.toEqual([])
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('follows next even if an intermediate page has no results', async () => {
    const next = `${API_URL}/startups/11/projects/?page=3`
    const fetchMock = mockFetch(jsonResponse(page([], next)))
      .mockResolvedValueOnce(jsonResponse(page([], next)))
      .mockResolvedValueOnce(jsonResponse(page(projects, null)))

    await expect(fetchStartupProjects(11)).resolves.toEqual(startupProjects)
    expect(fetchMock).toHaveBeenLastCalledWith(next, expect.any(Object))
  })

  it('rejects if a later page fails instead of returning a partial list', async () => {
    const next = `${API_URL}/startups/11/projects/?page=2`
    mockFetch(jsonResponse(page(projects.slice(0, 6), next)))
      .mockResolvedValueOnce(jsonResponse(page(projects.slice(0, 6), next)))
      .mockResolvedValueOnce(jsonResponse({ detail: 'Unavailable' }, { status: 503 }))

    await expect(fetchStartupProjects(11)).rejects.toBeInstanceOf(ApiError)
  })
})
