import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.tsx'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home.tsx'
import Login from './pages/Login'
import Profile from './pages/Profile'
import ForgotPassword from './pages/ForgotPassword'
import Register from './pages/Register.tsx'
import StartupView from './pages/StartupView.tsx'
import InvestorDashboard from './pages/InvestorDashboard.tsx'
import Inbox from './pages/Inbox.tsx'
import NotFound from './pages/NotFound.tsx'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/register" element={<Register />} />
        <Route path="/startups/:id" element={<StartupView />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<InvestorDashboard />} />
          <Route path="/messages" element={<Inbox />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
        <Route path="/search" element={<div>Search</div>} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

export default App
