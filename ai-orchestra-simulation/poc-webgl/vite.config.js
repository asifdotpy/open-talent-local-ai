import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate Three.js and R3F into their own chunks
          'three-vendor': ['three'],
          'r3f-vendor': ['@react-three/fiber', '@react-three/drei'],
          'rpm-vendor': ['@readyplayerme/visage'],
          // React in separate chunk
          'react-vendor': ['react', 'react-dom'],
          // State management
          'state-vendor': ['zustand']
        }
      }
    },
    // Increase chunk size warning limit since we're optimizing
    chunkSizeWarningLimit: 1000
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['three', '@react-three/fiber', '@react-three/drei']
  }
})