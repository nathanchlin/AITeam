/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        coder: {
          primary: '#3B82F6',
          secondary: '#60A5FA',
          light: '#93C5FD',
        },
        analyst: {
          primary: '#10B981',
          secondary: '#34D399',
          light: '#6EE7B7',
        },
        assistant: {
          primary: '#8B5CF6',
          secondary: '#A78BFA',
          light: '#C4B5FD',
        },
        custom: {
          primary: '#F59E0B',
          secondary: '#FBBF24',
          light: '#FCD34D',
        },
      },
      animation: {
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
