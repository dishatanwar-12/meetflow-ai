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
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#6c52ee', // Main brand purple
          700: '#5840d8',
          800: '#4c35b8',
          900: '#3c2b91',
          DEFAULT: '#6c52ee',
        },
        brand: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#6c52ee',
          700: '#5840d8',
          800: '#4c35b8',
          900: '#1e1b4b', // Deep indigo / heading navy
          950: '#0f0e26',
          DEFAULT: '#6c52ee',
        },
        accent: {
          50: '#ecfdf5',
          100: '#d1fae5',
          500: '#10b981', // Emerald green
          600: '#059669',
        },
        surface: {
          DEFAULT: '#ffffff',
          subtle: '#f8f9fd',
          muted: '#f1f3f9',
          border: '#edf0f7',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 14px -2px rgba(108, 82, 238, 0.04), 0 2px 6px -1px rgba(0, 0, 0, 0.02)',
        'card': '0 4px 20px -2px rgba(108, 82, 238, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.02)',
        'card-hover': '0 10px 25px -3px rgba(108, 82, 238, 0.08), 0 4px 10px -2px rgba(0, 0, 0, 0.03)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      }
    },
  },
  plugins: [],
}
