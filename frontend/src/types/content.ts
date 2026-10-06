export interface HeroCollageItem {
  key: 'wine' | 'delivery' | 'cheese' | 'packaging'
  label: string
  imageUrl: string,
  alt?: string
}

export interface HeroContent {
  title: string
  subtitle: string
  buttonLabel: string
  collage: HeroCollageItem[]
}