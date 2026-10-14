import type { ForWhomSectionData } from './types'

// Same content as the backend fixture; used until the page loads it from the API
export const forWhomSectionMock: ForWhomSectionData = {
  title: 'Для кого',
  items: [
    { icon: 'bread-slice', title: 'Виробники крафтової продукції', desc: '' },
    { icon: 'wine-glass', title: 'Сомельє та ресторатори', desc: '' },
    {
      icon: 'hotel',
      title: 'Представники готельно-ресторанного бізнесу',
      desc: '',
    },
    {
      icon: 'cart-shopping',
      title: 'Представники роздрібних та гуртових торгових мереж',
      desc: '',
    },
    {
      icon: 'box-archive',
      title: 'Представники пакувальної індустрії',
      desc: '',
    },
    {
      icon: 'truck',
      title: 'Представники логістичних компаній та служб доставки',
      desc: '',
    },
    { icon: 'rocket', title: 'Стартапери', desc: '' },
    { icon: 'people-group', title: 'Інші фахівці галузі', desc: '' },
  ],
}
