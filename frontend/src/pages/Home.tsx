import { API_URL } from '../config'
import BannerSection from '../sections/landing/BannerSection'
import { bannerSectionMock } from '../sections/landing/BannerSection/mocks'
import ForWhomSection from '../sections/landing/ForWhomSection'
import { forWhomSectionMock } from '../sections/landing/ForWhomSection/mocks'
import WhyWorthSection from '../sections/landing/WhyWorthSection'
import { whyWorthSectionMock } from '../sections/landing/WhyWorthSection/mocks'

function Home() {
  return (
    <section>
      <h1>Home</h1>
      <p>Landing page: connecting startups and investors.</p>
      <p className="muted">API: {API_URL}</p>
      <BannerSection data={bannerSectionMock} />
      <ForWhomSection data={forWhomSectionMock} />
      <WhyWorthSection data={whyWorthSectionMock} />
    </section>
  )
}

export default Home
