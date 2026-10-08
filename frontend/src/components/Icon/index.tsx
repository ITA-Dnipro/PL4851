import type { IconProps } from './types'

// Renders a Font Awesome icon as a plain SVG, without the Font Awesome runtime.
// Size and color come from CSS: `width`/`height` and `color`.
export default function Icon({ icon, className }: IconProps) {
  const [width, height, , , pathData] = icon.icon
  const paths = Array.isArray(pathData) ? pathData : [pathData]

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      data-icon={icon.iconName}
      fill="currentColor"
      aria-hidden="true"
      focusable="false"
    >
      {paths.map((path) => (
        <path key={path} d={path} />
      ))}
    </svg>
  )
}
