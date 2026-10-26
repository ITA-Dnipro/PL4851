// Reads the "exp" claim of a JWT as a timestamp in milliseconds.
// The signature isn't checked here: that's the backend's job.
export function getTokenExpiry(token: string): number | null {
  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const { exp } = JSON.parse(atob(payload))
    return typeof exp === 'number' ? exp * 1000 : null
  } catch {
    return null
  }
}
