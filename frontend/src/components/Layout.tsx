import { NavLink, Outlet } from 'react-router-dom'

interface NavItem {
  to: string
  label: string
}

const links: NavItem[] = [
  { to: '/', label: 'Home' },
  { to: '/startups/1', label: 'Startup #1' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/messages', label: 'Messages' },
  { to: '/login', label: 'Login' },
  { to: '/register', label: 'Register' },
]

function Layout() {
  return (
    <>
      <header className="header">
        <span className="logo">Forum</span>
        <nav>
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end>
              {link.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </>
  )
}

export default Layout
