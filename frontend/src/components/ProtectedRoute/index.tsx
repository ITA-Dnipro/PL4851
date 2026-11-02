import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'

// Wraps routes that need a signed-in user
export default function ProtectedRoute() {
  const { status } = useAuth()
  const location = useLocation()

  // Wait for the session to be restored, so a reload doesn't bounce to the login page
  if (status === 'loading') {
    return null
  }
  if (status === 'anonymous') {
    // Login sends the user back here afterwards
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  return <Outlet />
}
