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

export interface PasswordResetConfirmRequest {
  uid: string
  token: string
  password: string
}

export interface PasswordResetConfirmResponse {
  detail: string
}

export function confirmPasswordReset(data: PasswordResetConfirmRequest) {
  return request<PasswordResetConfirmResponse>(
    '/auth/password-reset/confirm/',
    {
      method: 'POST',
      body: data,
    },
  )
}
