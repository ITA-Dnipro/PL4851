import { apiRequest } from './client'

export type UserRole = 'startup' | 'investor'

export interface LoginRequest {
  email: string
  password: string
  remember: boolean
}

export interface AuthUser {
  id: number
  email: string
  role: UserRole
}

// The refresh token comes in an HttpOnly cookie, not in the body
export interface LoginResponse {
  access: string
  user: AuthUser
}

export function login(data: LoginRequest) {
  return apiRequest<LoginResponse>('/auth/login/', { method: 'POST', body: data })
}
