import HeroSection from '../sections/landing/HeroSection'
import { heroSectionMock } from '../sections/landing/HeroSection/mocks'
import BannerSection from '../sections/landing/BannerSection'
import { bannerSectionMock } from '../sections/landing/BannerSection/mocks'
import ForWhomSection from '../sections/landing/ForWhomSection'
import { forWhomSectionMock } from '../sections/landing/ForWhomSection/mocks'
import WhyWorthSection from '../sections/landing/WhyWorthSection'
import { whyWorthSectionMock } from '../sections/landing/WhyWorthSection/mocks'
import NewParticipantsSection from '../sections/landing/NewParticipantsSection'
import { useHomeData } from '../hooks/useHomeData'

// TODO: fetch section data from GET /api/content/landing/ instead of mocks
function Home() {

  const { startups, isLoading, isLoadingMore, loadMore } = useHomeData()
  return (
    <>
      <HeroSection data={heroSectionMock} />
      <NewParticipantsSection
          data={startups}
          isLoading={isLoading}
          onLoadMore={loadMore}
          isLoadingMore={isLoadingMore}
      />
      <BannerSection data={bannerSectionMock} />
      <ForWhomSection data={forWhomSectionMock} />
      <WhyWorthSection data={whyWorthSectionMock} />
    </>
  )
}

export default Home
