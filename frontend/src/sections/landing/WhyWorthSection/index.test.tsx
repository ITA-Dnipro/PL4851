import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import WhyWorthSection from '.'
import { whyWorthSectionMock } from './mocks'

describe('WhyWorthSection', () => {
  it('renders the section title and all items', () => {
    render(<WhyWorthSection data={whyWorthSectionMock} />)

    expect(
      screen.getByRole('heading', { level: 2, name: 'Чому варто' }),
    ).toBeInTheDocument()
    expect(screen.getAllByRole('listitem')).toHaveLength(
      whyWorthSectionMock.items.length,
    )
    expect(screen.getByText('Ексклюзивні пропозиції')).toBeInTheDocument()
  })

  it('cards are reachable with the keyboard', async () => {
    const user = userEvent.setup()
    render(<WhyWorthSection data={whyWorthSectionMock} />)
    const cards = screen.getAllByRole('article')

    await user.tab()
    expect(cards[0]).toHaveFocus()

    await user.tab()
    expect(cards[1]).toHaveFocus()
  })

  it('renders nothing when data is null', () => {
    const { container } = render(<WhyWorthSection data={null} />)

    expect(container).toBeEmptyDOMElement()
  })
})
