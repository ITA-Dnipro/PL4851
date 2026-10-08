import type { WhyWorthSectionData } from './types'

// Same content as the backend fixture; used as a fallback when the API is unavailable
export const whyWorthSectionMock: WhyWorthSectionData = {
  title: 'Чому варто',
  items: [
    {
      title: 'Прямий зв’язок з виробниками',
      desc: 'Знайомтеся з історією та цінностями брендів',
    },
    {
      title: 'Ексклюзивні пропозиції',
      desc: 'Знаходьте унікальні продукти, недоступні в масовому продажі',
    },
    {
      title: 'Інновації та тренди',
      desc: 'Будьте в курсі останніх новинок та технологій галузі',
    },
    {
      title: 'Співпраця та синергія',
      desc: 'Об’єднуйтесь, щоб творити нове та ділитися досвідом',
    },
    {
      title: 'Розвиток та масштабування',
      desc: 'Знаходьте нових партнерів, клієнтів та ринки збуту',
    },
    {
      title: 'Підтримка та знання',
      desc: 'Отримуйте консультації, експертну допомогу та доступ до освітніх ресурсів',
    },
  ],
}
