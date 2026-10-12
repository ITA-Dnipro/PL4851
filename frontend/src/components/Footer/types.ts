export interface FooterLinkData {
  label: string
  url: string
}

export interface FooterLinkGroupData {
  title: string
  links: FooterLinkData[]
}

export interface FooterContactsData {
  address: string[]
  email: string
  phone: string
}

export interface FooterData {
  contacts: FooterContactsData
  link_groups: FooterLinkGroupData[]
  legal_links: FooterLinkData[]
  copyright: string
}
