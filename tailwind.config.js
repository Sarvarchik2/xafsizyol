/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FF385C', // Airbnb Red
          dark: '#E31C5F',
        },
        secondary: {
          DEFAULT: '#008489', // Airbnb Teal
        },
        airbnb: {
          black: '#222222',
          gray: '#717171',
          lightGray: '#DDDDDD',
          bg: '#F7F7F7',
        }
      },
      borderRadius: {
        'airbnb': '12px',
        'airbnb-lg': '24px',
      },
      boxShadow: {
        'airbnb': '0px 4px 16px rgba(0, 0, 0, 0.08)',
        'airbnb-hover': '0px 6px 20px rgba(0, 0, 0, 0.12)',
      },
      fontFamily: {
        sans: ['Inter', 'Plus Jakarta Sans', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
