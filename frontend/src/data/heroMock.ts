import wine from '../assets/hero/wine.png'
import delivery from '../assets/hero/delivery.png'
import cheese from '../assets/hero/cheese.png'
import packaging from '../assets/hero/packaging.png'
import type { HeroContent } from '../types/content'

export const heroMock: HeroContent = {
  title: 'FORUM',
  subtitle: 'Об’єднуємо крафтових виробників та інноваторів',
  buttonLabel: 'Детальніше про нас',
  collage: [
    { key: 'wine', label: 'Виноробство', imageUrl: wine },
    { key: 'delivery', label: 'Доставка', imageUrl: delivery },
    { key: 'cheese', label: 'Сироварня', imageUrl: cheese },
    { key: 'packaging', label: 'Упаковка', imageUrl: packaging },
  ],
}