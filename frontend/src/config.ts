// Base URL of the backend API, taken from .env (VITE_API_URL)
  export const API_URL: string = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

  // Origin of the backend server (without /api)
  export const BACKEND_ORIGIN: string = API_URL.replace(/\/api\/?$/, '')
