import type { FooterData } from './types'

// Content from the mockup; used until the layout data is loaded from the API.
// Pages for these links don't exist yet, so they point to '#'.
export const footerMock: FooterData = {
  contacts: {
    address: ['Львівська Політехніка', 'вул. Степана Бандери 12, Львів'],
    email: 'qwerty@gmail.com',
    phone: '+38 050 234 23 23',
  },
  link_groups: [
    {
      title: 'Підприємства',
      links: [
        { label: 'Компанії', url: '#' },
        { label: 'Стартапи', url: '#' },
      ],
    },
    {
      title: 'Сектори',
      links: [
        { label: 'Виробники', url: '#' },
        { label: 'Імпортери', url: '#' },
        { label: 'Роздрібні мережі', url: '#' },
        { label: 'HORECA', url: '#' },
        { label: 'Інші послуги', url: '#' },
      ],
    },
  ],
  legal_links: [
    { label: 'Політика конфіденційності', url: '#' },
    { label: 'Умови користування', url: '#' },
    { label: 'Зворотній зв’язок', url: '#' },
  ],
  copyright: 'Copyright 2023 Forum. All rights reserved.',
}
