type AccessTokenListener = (token: string | null) => void

// The access token lives only in memory: JavaScript on the page can't read the
// refresh token (HttpOnly cookie), and the access token is gone after a reload
let accessToken: string | null = null
const listeners = new Set<AccessTokenListener>()

export function getAccessToken() {
  return accessToken
}

export function setAccessToken(token: string | null) {
  accessToken = token
  listeners.forEach((listener) => listener(token))
}

// Called on every change, including a session that ends inside authRequest
export function subscribeToAccessToken(listener: AccessTokenListener) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}
