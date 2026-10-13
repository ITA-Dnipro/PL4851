import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import NewParticipantsSection from './index'
import type { StartupsListData } from './types'

const data: StartupsListData = {
  count: 12,
  next: '/api/startups/?page=2',
  previous: null,
  results: [
    {
      id: 1,
      company_name: 'Handmade Co',
      short_description: 'Woodwork and ceramics',
      thumbnail_url: '/media/thumbs/1.jpg',
      logoUrl: '/media/thumbs/1.jpg',
      location: 'Chernivtsi',
      tags: ['craft'],
    },
  ],
}

function renderSection(overrides: Partial<React.ComponentProps<typeof NewParticipantsSection>> = {}) {
  return render(
    <MemoryRouter>
      <NewParticipantsSection
        data={data}
        isLoading={false}
        isLoadingMore={false}
        onLoadMore={() => {}}
        {...overrides}
      />
    </MemoryRouter>,
  )
}

describe('NewParticipantsSection', () => {
  it('shows a loading message while isLoading is true', () => {
    renderSection({ isLoading: true, data: null })

    expect(screen.getByText('Завантаження...')).toBeInTheDocument()
    expect(screen.queryByText('Handmade Co')).not.toBeInTheDocument()
  })

  it('shows an empty state when there is no data and loading is finished', () => {
    renderSection({ data: null, isLoading: false })

    expect(screen.getByText('Стартапів ще немає.')).toBeInTheDocument()
  })

  it('shows an empty state when results are empty', () => {
    renderSection({ data: { ...data, count: 0, results: [] } })

    expect(screen.getByText('Стартапів ще немає.')).toBeInTheDocument()
  })

  it('renders startups from the passed data', () => {
    renderSection()

    expect(screen.getByText('Handmade Co')).toBeInTheDocument()
  })

  it('links a card to /startups/:id', () => {
    renderSection()

    const link = screen.getByRole('link', { name: /Handmade Co/ })
    expect(link).toHaveAttribute('href', '/startups/1')
  })

  it('shows the "load more" button when there is a next page, and calls onLoadMore on click', () => {
    const onLoadMore = vi.fn()
    renderSection({ onLoadMore })

    const button = screen.getByRole('button', { name: 'Показати ще' })
    fireEvent.click(button)

    expect(onLoadMore).toHaveBeenCalledTimes(1)
  })

  it('hides the "load more" button when there is no next page', () => {
    renderSection({ data: { ...data, next: null } })

    expect(screen.queryByRole('button', { name: 'Показати ще' })).not.toBeInTheDocument()
  })

  it('disables the "load more" button while loading more', () => {
    renderSection({ isLoadingMore: true })

    const button = screen.getByRole('button', { name: 'Завантаження...' })
    expect(button).toBeDisabled()
  })
})
