/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e3f2fd',
          60: '#48a4d0',
          70: '#1976d2',
        },
        critical: {
          50: '#ffebee',
          60: '#e74c3c',
          70: '#c0392b',
        },
        warning: {
          50: '#fff3e0',
          60: '#f39c12',
          70: '#e67e22',
        },
        success: {
          50: '#e8f5e9',
          60: '#27ae60',
          70: '#229954',
        },
        neutral: {
          50: '#f5f5f5',
          60: '#424242',
          70: '#2e2e2e',
          80: '#1a1a1a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
