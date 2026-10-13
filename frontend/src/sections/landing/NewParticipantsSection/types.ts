export interface StartupItem {
  id: number
  company_name: string
  short_description: string
  thumbnail_url: string
  logoUrl: string
  location: string
  tags: string[]
}

export interface StartupsListData {
  count: number
  next: string | null
  previous: string | null
  results: StartupItem[]
}

export interface ApiStartupItem {
  startup_id: number
  startup_name: string
  short_description: string
  logo: string
  location: string
  industries: string[]
}

export interface ApiStartupsListData {
  count: number
  next: string | null
  previous: string | null
  results: ApiStartupItem[]
}
