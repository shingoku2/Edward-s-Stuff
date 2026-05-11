import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
// base: './' is required when the HUD is loaded via file:// from PyQt6 WebEngine
// (absolute "/assets/..." would resolve to the filesystem root, not dist/).
export default defineConfig({
  base: './',
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
