/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          200: '#bcccdc',
          300: '#9fb3c8',
          400: '#829ab1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#243b53',
          900: '#102a43', // Deep navy primary
          950: '#0b1d30',
        },
        accent: {
          50: '#e6fffa',
          100: '#b2f5ea',
          500: '#319795', // Restrained teal
          600: '#285e61',
        },
        surface: {
          DEFAULT: '#ffffff',
          warm: '#fbfbfb',
          muted: '#f8fafc',
          border: '#e2e8f0',
        },
        slate: {
          charcoal: '#1e293b',
          muted: '#64748b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

