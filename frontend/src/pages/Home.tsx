import { API_URL } from '../config.ts'

function Home() {
  return (
    <section>
      <h1>Home</h1>
      <p>Landing page: connecting startups and investors.</p>
      <p className="muted">API: {API_URL}</p>
    </section>
  )
}

export default Home
