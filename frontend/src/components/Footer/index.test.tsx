import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import Footer from '.'
import { footerMock } from './mocks'
import type { FooterData } from './types'

function renderFooter(data: FooterData | null) {
  return render(
    <MemoryRouter>
      <Footer data={data} />
    </MemoryRouter>,
  )
}

describe('Footer', () => {
  it('renders every link group with its links', () => {
    renderFooter(footerMock)

    for (const group of footerMock.link_groups) {
      const nav = screen.getByRole('navigation', { name: group.title })

      expect(within(nav).getAllByRole('link')).toHaveLength(group.links.length)
    }
  })

  it('renders the address and contact links', () => {
    renderFooter(footerMock)

    expect(screen.getByText('Львівська Політехніка')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'qwerty@gmail.com' })).toHaveAttribute(
      'href',
      'mailto:qwerty@gmail.com',
    )
    expect(screen.getByRole('link', { name: '+38 050 234 23 23' })).toHaveAttribute(
      'href',
      'tel:+380502342323',
    )
  })

  it('renders the legal links and copyright', () => {
    renderFooter(footerMock)

    expect(
      screen.getByRole('link', { name: 'Політика конфіденційності' }),
    ).toBeInTheDocument()
    expect(screen.getByText(footerMock.copyright)).toBeInTheDocument()
  })

  it('renders only the copyright when data is null', () => {
    renderFooter(null)

    expect(screen.getByRole('contentinfo')).toHaveTextContent(
      `Copyright ${new Date().getFullYear()} Forum`,
    )
    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })
})
