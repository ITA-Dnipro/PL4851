import { request } from './client/request'

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

export interface RefreshResponse {
  access: string
}

export type LegalForm = 'sole_proprietor' | 'legal_entity'

export interface RegisterRequest {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  company_name: string
  role: UserRole
  legal_form: LegalForm
}

export interface RegisterResponse {
  id: number
  email: string
  detail: string
}

export function login(data: LoginRequest) {
  return request<LoginResponse>('/auth/login/', { method: 'POST', body: data })
}

// A new access token for the refresh token cookie
export function refresh() {
  return request<RefreshResponse>('/auth/refresh/', { method: 'POST' })
}

// Revokes the refresh token and deletes its cookie
export function logout() {
  return request<void>('/auth/logout/', { method: 'POST' })
}

// Creates an inactive account and sends the verification email
export function register(data: RegisterRequest) {
  return request<RegisterResponse>('/auth/register/', { method: 'POST', body: data })
}
