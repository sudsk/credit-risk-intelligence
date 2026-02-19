/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // EPAM Loveship Dark Theme
        primary: {
          50: '#E3F2FD',
          60: '#48A4D0',
          70: '#7DBCDB',
        },
        critical: {
          50: 'rgba(229, 98, 72, 0.15)',
          60: '#E56248',
          70: '#F78C77',
        },
        warning: {
          50: 'rgba(244, 184, 58, 0.15)',
          60: '#F4B83A',
          70: '#FFD06D',
        },
        success: {
          50: 'rgba(131, 185, 24, 0.15)',
          60: '#83B918',
          70: '#A6D151',
        },
        neutral: {
          50: '#FAFAFC',
          100: '#E1E3EB',
          200: '#ACAFBF',
          300: '#6C6F80',
          400: '#585B69',
          500: '#474A59',
          600: '#383B4A',
          700: '#303240',
          800: '#272833',
          900: '#1D1E26',
        },
      },
      fontFamily: {
        sans: ['Source Sans Pro', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '3px',
      },
      boxShadow: {
        'level-2': '0 1px 2px rgba(0, 0, 0, 0.2), 0 4px 22px 3px rgba(0, 0, 0, 0.26)',
        'level-3': '0 1px 2px rgba(0, 0, 0, 0.2), 0 3px 25px 3px rgba(0, 0, 0, 0.56)',
      },
    },
  },
  plugins: [],
}