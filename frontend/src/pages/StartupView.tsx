import { useParams } from 'react-router-dom'

function StartupView() {
  const { id } = useParams<{ id: string }>()

  return (
    <section>
      <h1>Startup #{id}</h1>
      <p>Startup profile and its projects will go here.</p>
    </section>
  )
}

export default StartupView
