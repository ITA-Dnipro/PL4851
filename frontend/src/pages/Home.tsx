import Hero from '../components/home/Hero'
import BannerSection from '../sections/landing/BannerSection'
import { bannerSectionMock } from '../sections/landing/BannerSection/mocks'
import ForWhomSection from '../sections/landing/ForWhomSection'
import { forWhomSectionMock } from '../sections/landing/ForWhomSection/mocks'
import WhyWorthSection from '../sections/landing/WhyWorthSection'
import { whyWorthSectionMock } from '../sections/landing/WhyWorthSection/mocks'

function Home() {
  return (
    <>
      <Hero />
      <BannerSection data={bannerSectionMock} />
      <ForWhomSection data={forWhomSectionMock} />
      <WhyWorthSection data={whyWorthSectionMock} />
    </>
  )
}

export default Home