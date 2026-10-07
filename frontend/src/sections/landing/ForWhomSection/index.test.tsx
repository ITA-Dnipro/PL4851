import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import ForWhomSection from '.'
import { forWhomSectionMock } from './mocks'

describe('ForWhomSection', () => {
  it('renders the section title and all cards', () => {
    render(<ForWhomSection data={forWhomSectionMock} />)

    expect(
      screen.getByRole('heading', { level: 2, name: 'Для кого' }),
    ).toBeInTheDocument()
    expect(screen.getAllByRole('listitem')).toHaveLength(
      forWhomSectionMock.items.length,
    )
    expect(screen.getAllByRole('heading', { level: 3 })).toHaveLength(
      forWhomSectionMock.items.length,
    )
  })

  it('renders the description only when it is present', () => {
    render(
      <ForWhomSection
        data={{
          title: 'Для кого',
          items: [
            { icon: 'rocket', title: 'Стартапери', desc: 'Опис' },
            { icon: 'truck', title: 'Логісти', desc: '' },
          ],
        }}
      />,
    )

    expect(screen.getByText('Опис')).toBeInTheDocument()
    expect(screen.getAllByRole('paragraph')).toHaveLength(1)
  })

  it('renders the icon by its name', () => {
    const { container } = render(
      <ForWhomSection
        data={{
          title: 'Для кого',
          items: [{ icon: 'truck', title: 'Логісти', desc: '' }],
        }}
      />,
    )

    const icon = container.querySelector('svg[data-icon="truck"]')
    expect(icon).toBeInTheDocument()
    // Decorative: the card title already describes it
    expect(icon).toHaveAttribute('aria-hidden', 'true')
  })

  it('renders a fallback icon for an unknown name', () => {
    const { container } = render(
      <ForWhomSection
        data={{
          title: 'Для кого',
          items: [{ icon: 'no-such-icon', title: 'Інше', desc: '' }],
        }}
      />,
    )

    expect(container.querySelector('svg[data-icon="circle"]')).toBeInTheDocument()
  })

  it('renders nothing when data is null', () => {
    const { container } = render(<ForWhomSection data={null} />)

    expect(container).toBeEmptyDOMElement()
  })
})
