import {
  type IconDefinition,
  faBoxArchive,
  faBreadSlice,
  faCartShopping,
  faCircle,
  faHotel,
  faPeopleGroup,
  faRocket,
  faTruck,
  faWineGlass,
} from '@fortawesome/free-solid-svg-icons'

// Icon names that can be set in the admin. Only these icons get into the bundle,
// so a new name must be added here explicitly.
const FOR_WHOM_ICONS: Record<string, IconDefinition> = {
  'bread-slice': faBreadSlice,
  'wine-glass': faWineGlass,
  hotel: faHotel,
  'cart-shopping': faCartShopping,
  'box-archive': faBoxArchive,
  truck: faTruck,
  rocket: faRocket,
  'people-group': faPeopleGroup,
}

export const FALLBACK_ICON = faCircle

export function getForWhomIcon(name: string): IconDefinition {
  return FOR_WHOM_ICONS[name] ?? FALLBACK_ICON
}
