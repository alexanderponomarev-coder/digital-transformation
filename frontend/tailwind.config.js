/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0c1210',
          900: '#14201c',
          800: '#1e2e28',
          700: '#2a4038',
          500: '#5c7368',
          300: '#a8b8b0',
          100: '#e6ebe8',
          50: '#f3f6f4',
        },
        tide: {
          600: '#0f6e6a',
          500: '#14837e',
          400: '#1fa39c',
          100: '#d7f1ef',
        },
        ember: {
          600: '#b45309',
          500: '#d97706',
          100: '#fef3c7',
        },
        moss: {
          600: '#3f6212',
          500: '#65a30d',
          100: '#ecfccb',
        },
      },
      fontFamily: {
        display: ['Syne', 'system-ui', 'sans-serif'],
        sans: ['Manrope', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 18px 50px -28px rgba(20, 32, 28, 0.35)',
      },
      backgroundImage: {
        mesh: 'radial-gradient(ellipse 80% 60% at 10% 0%, rgba(31,163,156,0.18), transparent 55%), radial-gradient(ellipse 70% 50% at 90% 10%, rgba(217,119,6,0.12), transparent 50%), radial-gradient(ellipse 60% 40% at 50% 100%, rgba(101,163,13,0.10), transparent 55%)',
      },
      keyframes: {
        rise: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fillbar: {
          '0%': { transform: 'scaleX(0)' },
          '100%': { transform: 'scaleX(1)' },
        },
        drift: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        },
      },
      animation: {
        rise: 'rise 0.7s ease-out both',
        fillbar: 'fillbar 0.9s ease-out both',
        drift: 'drift 5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
