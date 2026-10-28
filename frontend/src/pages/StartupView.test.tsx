import { act, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Link, MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import StartupView from './StartupView'
import type { StartupProfile } from '../api/startups'
import { API_URL, BACKEND_ORIGIN } from '../config'

// Profile from the mockup, as GET /api/startups/{id}/ sends it
const profile: StartupProfile = {
  startup_id: 11,
  startup_name: 'Асоціація рітейлерів України',
  slug: 'asotsiatsiia-riteileriv-ukrainy',
  hero_image: '/media/thumbs/hero.placeholder.jpg',
  logo: '/media/startups/logos/rau.png',
  short_description: 'Створювати майбутнє, де інновації сприяють розвитку бізнесу',
  about_html: '<p>Компанія є провідним гравцем у галузі інноваційних технологій.</p>',
  contact: { email: 'abc@gmail.com', phone: '+380505810169' },
  website: 'https://stakhovskywines.com',
  industries: ['Виноробство', 'Їжа', 'Напої'],
  followers_count: 42,
  projects_count: 3,
  created_at: '2026-10-05T09:00:00Z',
}

function mockFetch() {
  return vi.spyOn(globalThis, 'fetch')
}

function jsonResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), { status })
}

// Shows the current link, to check where the page moved to
function LocationDisplay() {
  return <p data-testid="location">{useLocation().pathname}</p>
}

function renderPage(path = `/startups/${profile.slug}`) {
  const user = userEvent.setup()
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/startups/:slug" element={<StartupView />} />
      </Routes>
      <LocationDisplay />
      {/* Opens another startup without reloading, like a link on the site */}
      <Link to="/startups/123">Стартап 123</Link>
    </MemoryRouter>,
  )
  return user
}

describe('StartupView', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows the loader while the profile is loading', () => {
    // Never resolves, so the page stays in the loading state
    mockFetch().mockReturnValue(new Promise(() => {}))
    renderPage()

    expect(screen.getByRole('status')).toHaveTextContent('Завантаження профілю…')
    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
  })

  it('renders the header with the profile from the API', async () => {
    const fetchMock = mockFetch().mockResolvedValue(jsonResponse(profile))
    renderPage()

    expect(
      await screen.findByRole('heading', { level: 1, name: profile.startup_name }),
    ).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith(
      `${API_URL}/startups/${profile.slug}/`,
      expect.any(Object),
    )
    // Media paths from the backend become backend URLs
    expect(screen.getByRole('img', { name: `Логотип ${profile.startup_name}` })).toHaveAttribute(
      'src',
      `${BACKEND_ORIGIN}${profile.logo}`,
    )

    const tags = within(screen.getByRole('list', { name: 'Галузі' })).getAllByRole('listitem')
    expect(tags.map((tag) => tag.textContent)).toEqual(profile.industries)
    for (const label of ['Стежити', 'Написати', 'Додати в збережені']) {
      expect(screen.getByRole('button', { name: label })).toBeEnabled()
    }
  })

  it('renders the main content and the sidebar with contacts', async () => {
    mockFetch().mockResolvedValue(jsonResponse(profile))
    renderPage()

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Про Компанію' }),
    ).toBeInTheDocument()
    expect(screen.getByText(profile.short_description)).toBeInTheDocument()

    const sidebar = screen.getByRole('complementary', { name: 'Інформація про компанію' })
    expect(within(sidebar).getByText('Підписники').nextSibling).toHaveTextContent('42')
    expect(within(sidebar).getByRole('link', { name: 'stakhovskywines.com' })).toHaveAttribute(
      'href',
      profile.website,
    )
    expect(within(sidebar).getByRole('link', { name: profile.contact.phone })).toHaveAttribute(
      'href',
      'tel:+380505810169',
    )
    expect(within(sidebar).getByRole('link', { name: profile.contact.email })).toHaveAttribute(
      'href',
      'mailto:abc@gmail.com',
    )
  })

  it('moves a profile opened by id to its slug link without loading it again', async () => {
    const fetchMock = mockFetch().mockResolvedValue(jsonResponse(profile))
    renderPage('/startups/11')

    await waitFor(() =>
      expect(screen.getByTestId('location')).toHaveTextContent(`/startups/${profile.slug}`),
    )
    expect(screen.getByRole('heading', { level: 1, name: profile.startup_name })).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/startups/11/`, expect.any(Object))
  })

  it('stays on the id link when the slug is only digits', async () => {
    // The backend reads /startups/123/ as id 123, so that link would open another startup
    const fetchMock = mockFetch().mockResolvedValue(jsonResponse({ ...profile, slug: '123' }))
    renderPage('/startups/11')

    expect(
      await screen.findByRole('heading', { level: 1, name: profile.startup_name }),
    ).toBeInTheDocument()
    // Let a link change, if the page started one, finish before checking the link
    await act(() => new Promise((resolve) => setTimeout(resolve, 0)))
    expect(screen.getByTestId('location')).toHaveTextContent('/startups/11')
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('opens /startups/123 as id 123, not as the shown startup whose slug is "123"', async () => {
    const otherStartup = { ...profile, startup_id: 123, startup_name: 'Інший стартап' }
    const fetchMock = mockFetch()
      .mockResolvedValueOnce(jsonResponse({ ...profile, slug: '123' }))
      .mockResolvedValueOnce(jsonResponse({ results: [] }))
      .mockResolvedValueOnce(jsonResponse(otherStartup))
      .mockResolvedValueOnce(jsonResponse({ results: [] }))
    const user = renderPage('/startups/11')

    await screen.findByRole('heading', { level: 1, name: profile.startup_name })
    await user.click(screen.getByRole('link', { name: 'Стартап 123' }))

    expect(
      await screen.findByRole('heading', { level: 1, name: otherStartup.startup_name }),
    ).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/startups/123/`, expect.any(Object))
  })

  it('shows the not found page for an unknown startup', async () => {
    mockFetch().mockResolvedValue(jsonResponse({ detail: 'Not found.' }, 404))
    renderPage('/startups/99999')

    expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
  })

  it('shows the not found page without a request for a link that is not an id or slug', () => {
    const fetchMock = mockFetch()
    renderPage('/startups/bad.link')

    expect(screen.getByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it.each([
    ['no connection', () => Promise.reject(new TypeError('Failed to fetch'))],
    ['server error', () => Promise.resolve(jsonResponse({}, 500))],
  ])('shows an error and loads again on retry: %s', async (_, failedResponse) => {
    const fetchMock = mockFetch()
      .mockImplementationOnce(failedResponse)
      .mockResolvedValueOnce(jsonResponse(profile))
    const user = renderPage()

    expect(await screen.findByRole('alert')).toHaveTextContent('Не вдалося завантажити профіль')

    await user.click(screen.getByRole('button', { name: 'Спробувати ще раз' }))

    expect(
      await screen.findByRole('heading', { level: 1, name: profile.startup_name }),
    ).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/startups/${profile.slug}/`, expect.any(Object))
  })
})
