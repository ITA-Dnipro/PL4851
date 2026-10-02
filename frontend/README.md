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
| Path | Page |
|---|---|
| `/` | Home |
| `/login` | Login |
| `/register` | Register |
| `/startups/:id` | StartupView |
| `/dashboard` | InvestorDashboard |
| `/messages` | Inbox |

## Structure
```
src/
  main.tsx          entry point, wraps App in BrowserRouter
  App.tsx           route definitions
  config.ts         API_URL from .env
  vite-env.d.ts     types for .env variables
  components/       shared components (Layout with nav bar)
  pages/            one file per page
```
