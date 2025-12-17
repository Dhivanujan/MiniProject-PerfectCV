/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Professional Purple/Violet Theme
        primary: {
          50: '#FAF5FF',   // Very light purple
          100: '#F3E8FF',
          200: '#E9D5FF',
          300: '#D8B4FE',
          400: '#C084FC',  // Bright purple
          500: '#A855F7',  // Main purple
          600: '#9333EA',  // Deep purple
          700: '#7E22CE',  // Rich purple
          800: '#6B21A8',
          900: '#581C87',
        },
        accent: {
          50: '#FDF4FF',
          100: '#FAE8FF',
          200: '#F5D0FE',
          300: '#F0ABFC',
          400: '#E879F9',  // Bright fuchsia
          500: '#D946EF',
          600: '#C026D3',
          700: '#A21CAF',
          800: '#86198F',
          900: '#701A75',
        },
        // Keep for backward compatibility
        sage: {
          50: '#FAF5FF',
          100: '#F3E8FF',
          200: '#E9D5FF',
          300: '#D8B4FE',
          400: '#C084FC',
          500: '#A855F7',
          600: '#9333EA',
          700: '#7E22CE',
          800: '#6B21A8',
          900: '#581C87',
        },
      },
    },
  },
  plugins: [],
};
