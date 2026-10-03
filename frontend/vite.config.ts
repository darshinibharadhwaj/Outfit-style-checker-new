import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // In development, forward /api calls to the FastAPI backend
    proxy: { '/api': 'http://localhost:8000' },
  },
  build: {
    // Build straight into the backend so FastAPI can serve the website
    outDir: '../backend/app/static',
    emptyOutDir: true,
  },
})
