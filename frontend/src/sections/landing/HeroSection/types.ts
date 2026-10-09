export interface HeroImage {
  title: string
  url: string
}

export interface HeroSectionData {
  title: string
  subtitle: string
  cta_text: string
  cta_url: string
  hero_images: HeroImage[]
}
