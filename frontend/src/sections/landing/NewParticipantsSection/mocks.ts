import ura from '../../../assets/participants/ura.jpg'
import uraLogo from '../../../assets/participants/ura-logo.svg';
import mhp from '../../../assets/participants/mhp.jpg';
import mhpLogo from '../../../assets/participants/mhp-logo.svg';
import type { StartupsListData } from './types'

export const newParticipantsSectionMock: StartupsListData = {
  count: 4,
  next: null,
  previous: null,
  results: [
    {
      id: 1,
      company_name: 'Асоціація рітейлерів України',
      short_description: 'Інші послуги',
      thumbnail_url: ura,
      logoUrl: uraLogo,
      location: 'Київ, Київська обл, Закарпатська обл.',
      tags: ['послуги'],
    },
    {
      id: 2,
      company_name: 'МХП',
      short_description: 'Інші послуги',
      thumbnail_url: mhp,
      logoUrl: mhpLogo,
      location: 'Київ, Київська обл, Закарпатська обл.',
      tags: ['послуги'],
    },
  ],
}
