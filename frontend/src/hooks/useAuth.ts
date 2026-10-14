export interface AuthUser {
  id: number;
  email: string;
}

export function useAuth() {
  return {
    user: null as AuthUser | null,
    isAuthenticated: false,
  };
}
