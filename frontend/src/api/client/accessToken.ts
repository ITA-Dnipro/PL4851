type AccessTokenListener = (token: string | null) => void

// The access token lives only in memory: JavaScript on the page can't read the
// refresh token (HttpOnly cookie), and the access token is gone after a reload
let accessToken: string | null = null
// Grows on every login and logout, so a refresh started in an earlier session
// can tell that its result is stale
let session = 0
// True after logout until the next login: the refresh cookie may live until the
// logout request finishes, and it must not sign the user back in
let isSessionEnded = false
const listeners = new Set<AccessTokenListener>()

export function getAccessToken() {
  return accessToken
}

export function getSession() {
  return session
}

export function sessionEnded() {
  return isSessionEnded
}

// Login: a new session with its token
export function startSession(token: string) {
  session += 1
  isSessionEnded = false
  setAccessToken(token)
}

// Logout: no token and no refresh until the next login
export function endSession() {
  session += 1
  isSessionEnded = true
  setAccessToken(null)
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
