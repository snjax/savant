/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FF6B00', // orange for important buttons
          hover: '#E65D00',   // slightly darker orange for hover states
        },
        secondary: {
          DEFAULT: 'rgb(82, 23, 109)', // purple for headings and less important elements
          hover: 'rgb(71, 20, 95)',    // slightly darker purple for hover states
        }
      }
    },
  },
  plugins: [],
} 
