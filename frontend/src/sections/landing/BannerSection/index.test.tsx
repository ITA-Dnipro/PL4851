import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import BannerSection from '.'
import { bannerSectionMock } from './mocks'
import type { BannerSectionData } from './types'

function renderBanner(data: BannerSectionData | null) {
  return render(
    <MemoryRouter>
      <BannerSection data={data} />
    </MemoryRouter>,
  )
}

describe('BannerSection', () => {
  it('renders the title', () => {
    renderBanner(bannerSectionMock)

    expect(
      screen.getByRole('heading', { level: 2, name: bannerSectionMock.title }),
    ).toBeInTheDocument()
  })

  it('renders the CTA as a link to its route', () => {
    renderBanner(bannerSectionMock)

    expect(screen.getByRole('link', { name: 'Долучитися' })).toHaveAttribute(
      'href',
      '/register',
    )
  })

  it('does not render the CTA without text or url', () => {
    renderBanner({ ...bannerSectionMock, cta_text: '' })

    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })

  it('renders nothing when data is null', () => {
    const { container } = renderBanner(null)

    expect(container).toBeEmptyDOMElement()
  })
})
