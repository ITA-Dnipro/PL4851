# Frontend (React + TypeScript + Vite)

## Requirements
- Node.js 20.19+ within the 20.x series, or Node.js 22.12+; npm

## Setup
```bash
cd frontend
npm install
cp .env.example .env    # edit VITE_API_URL if needed
```

## Commands
| Command | What it does |
|---|---|
| `npm run dev` | Start dev server at http://localhost:5173 (auto-reload on save) |
| `npm run build` | Type-check (tsc) + production build into `dist/` |
| `npm run preview` | Serve the production build locally |

## Routes
| Path | Page | Sign-in required |
|---|---|---|
| `/` | Home | |
| `/login` | Login | |
| `/forgot-password` | ForgotPassword (placeholder) | |
| `/register` | Register | |
| `/startups/:id` | StartupView | |
| `/dashboard` | InvestorDashboard | yes |
| `/messages` | Inbox | yes |
| `/profile` | Profile (placeholder) | yes |

Pages that need a signed-in user go inside the `ProtectedRoute` group in `App.tsx`.

## Structure
```
src/
  main.tsx          entry point: BrowserRouter > AuthProvider > App
  App.tsx           route definitions
  config.ts         API_URL from .env
  vite-env.d.ts     types for .env variables
  api/              backend requests (see "API and auth")
  context/          AuthProvider and AuthContext
  hooks/            shared hooks (useAuth)
  components/       shared components, one folder each (Header, Footer, UserMenu, ProtectedRoute)
  sections/         page sections, e.g. landing/HeroSection
  pages/            pages; a page with its own files gets a folder (Login/)
  styles/           CSS variables
  test/             test setup and helpers shared by tests
```

Tests sit next to the code they test (`index.test.tsx`, `request.test.ts`).

## API and auth
```
api/
  auth.ts                login(), refresh(), logout()
  client/
    request.ts           request(): a plain request to the backend
    authRequest.ts       authRequest(): request() + access token, refresh on 401
    accessToken.ts       the access token in memory
    errors.ts            ApiError
```

Every request goes through `request()`: it adds `API_URL`, sends and parses JSON, includes the refresh token cookie (`credentials: 'include'`) and turns failures into `ApiError` (`status`, `message` from `detail`, `fieldErrors`, `retryAfter`; status `0` means no connection).

Endpoint functions are grouped by backend area (`api/auth.ts`, later `api/startups.ts`…) and choose one of two helpers:

- `request()` — public endpoints and the auth endpoints (login, refresh, logout), which work with a password or the cookie;
- `authRequest()` — endpoints that need a signed-in user. It sends `Authorization: Bearer <access>`; on 401 it gets a new access token once (one shared refresh for parallel requests) and repeats the request.

```ts
export function login(data: LoginRequest) {
  return request<LoginResponse>('/auth/login/', { method: 'POST', body: data })
}
```

### Tokens
- **Access** (15 min) lives only in memory (`accessToken.ts`) and is gone after a reload.
- **Refresh** (1 day, 30 days with "Remember me") is an HttpOnly cookie set by the backend; JavaScript can't read it. So an XSS script on the page can't steal the refresh token.

### AuthProvider
`context/AuthProvider.tsx` keeps the session; components read it with `useAuth()`:

| Field | Meaning |
|---|---|
| `status` | `loading` (restoring the session after a reload), `authenticated` or `anonymous` |
| `isAuthenticated` | `status === 'authenticated'` |
| `user` | `id`, `email`, `role` after login; `null` after a reload until `GET /api/auth/me/` exists |
| `login()`, `logout()`, `refresh()` | actions; `logout()` signs out locally even if the request fails |

- On start it calls refresh: with a valid cookie the user stays signed in after a reload.
- It refreshes the access token a minute before it expires (not sooner than in 30 s).
- When a refresh returns 401 (cookie expired or revoked), the session ends: `status` becomes `anonymous`.

`ProtectedRoute` shows nothing while `loading`, sends `anonymous` users to `/login` and remembers the page, so login returns there. `UserMenu` ("Мій профіль" in the header) links to the profile and logs out, going to `/` first.

Requests to `/api/auth/` need the API on the same site as the frontend: use `localhost` for both, not `127.0.0.1`.

## Icons
Icons come from the free Font Awesome solid set and are rendered with `components/Icon`:

```tsx
import { faTruck } from '@fortawesome/free-solid-svg-icons'

<Icon icon={faTruck} className={styles.icon} />   // size: width/height, color: color
```

Import only the icons you use. Icons set in the admin by name (e.g. "For whom" cards) must be added to the section's `icons.ts`, otherwise a fallback icon is shown.
