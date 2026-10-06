import { API_URL } from '../config'
import WhyWorthSection from '../sections/landing/WhyWorthSection'
import { whyWorthSectionMock } from '../sections/landing/WhyWorthSection/mocks'

function Home() {
  return (
    <section>
      <h1>Home</h1>
      <p>Landing page: connecting startups and investors.</p>
      <p className="muted">API: {API_URL}</p>
      <WhyWorthSection data={whyWorthSectionMock} />
    </section>
  )
}

export default Home
