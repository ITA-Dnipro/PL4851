import { Outlet } from 'react-router-dom'
import Header from './Header'
import Footer from './Footer'
import { footerMock } from './Footer/mocks'

function Layout() {
  return (
    <>
      <Header />
      <main className="page">
        <Outlet />
      </main>
      <Footer data={footerMock} />
    </>
  )
}

export default Layout
