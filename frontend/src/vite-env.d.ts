/// <reference types="vite/client" />

// Types for variables in .env (must start with VITE_)
interface ImportMetaEnv {
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
