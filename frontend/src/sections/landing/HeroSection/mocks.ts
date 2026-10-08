import wine from '../../../assets/hero/wine.png'
import delivery from '../../../assets/hero/delivery.png'
import cheese from '../../../assets/hero/cheese.png'
import packaging from '../../../assets/hero/packaging.png'
import type { HeroSectionData } from './types'

export const heroSectionMock: HeroSectionData = {
  title: 'FORUM',
  subtitle: 'Об’єднуємо крафтових виробників та інноваторів',
  cta_text: 'Детальніше про нас',
  cta_url: '/register',
  hero_images: [
    { title: 'Виноробство', url: wine },
    { title: 'Доставка', url: delivery },
    { title: 'Сироварня', url: cheese },
    { title: 'Упаковка', url: packaging },
  ],
}