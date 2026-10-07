import { faTruck, type IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import Icon from '.'

function renderIcon(icon: IconDefinition, className?: string) {
  const { container } = render(<Icon icon={icon} className={className} />)
  return container.querySelector('svg')
}

describe('Icon', () => {
  it('renders the icon as an svg sized by its own dimensions', () => {
    const [width, height] = faTruck.icon
    const svg = renderIcon(faTruck)

    expect(svg).toHaveAttribute('viewBox', `0 0 ${width} ${height}`)
    expect(svg).toHaveAttribute('data-icon', 'truck')
    expect(svg?.querySelectorAll('path')).toHaveLength(1)
  })

  it('is hidden from screen readers and takes color from CSS', () => {
    const svg = renderIcon(faTruck)

    expect(svg).toHaveAttribute('aria-hidden', 'true')
    expect(svg).toHaveAttribute('fill', 'currentColor')
  })

  it('passes the className through', () => {
    const svg = renderIcon(faTruck, 'my-icon')

    expect(svg).toHaveClass('my-icon')
  })

  it('renders every path of a multi-path icon', () => {
    const duotone: IconDefinition = {
      prefix: 'fas',
      iconName: 'truck',
      icon: [512, 512, [], 'f000', ['M0 0h1', 'M1 1h1']],
    }

    expect(renderIcon(duotone)?.querySelectorAll('path')).toHaveLength(2)
  })
})
