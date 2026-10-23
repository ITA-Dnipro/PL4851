type AccessTokenListener = (token: string | null) => void

// The access token lives only in memory: JavaScript on the page can't read the
// refresh token (HttpOnly cookie), and the access token is gone after a reload
let accessToken: string | null = null
// Grows on every login and logout, so a refresh started in an earlier session
// can tell that its result is stale
let session = 0
const listeners = new Set<AccessTokenListener>()

export function getAccessToken() {
  return accessToken
}

export function getSession() {
  return session
}

// Login starts a new session with its token, logout with null
export function startSession(token: string | null) {
  session += 1
  setAccessToken(token)
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
