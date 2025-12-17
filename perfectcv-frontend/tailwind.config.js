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
        // Professional Teal/Cyan Theme
        primary: {
          50: '#F0FAFA',   // Very light teal
          100: '#E0F5F5',
          200: '#C2EBEB',
          300: '#99DEDE',
          400: '#2BC0C0',  // Bright cyan
          500: '#0E9EA3',  // Main teal
          600: '#0D7E82',  // Medium teal
          700: '#0D5859',  // Dark teal
          800: '#0A4445',
          900: '#083536',
        },
        accent: {
          50: '#F0FDFD',
          100: '#CCFBFB',
          200: '#99F7F7',
          300: '#5EEFF0',
          400: '#2BC0C0',  // Bright turquoise
          500: '#17A2A2',
          600: '#0E9EA3',
          700: '#0D7E82',
          800: '#0A5F62',
          900: '#084B4D',
        },
        // Keep for backward compatibility
        sage: {
          50: '#F0FAFA',
          100: '#E0F5F5',
          200: '#C2EBEB',
          300: '#99DEDE',
          400: '#2BC0C0',
          500: '#0E9EA3',
          600: '#0D7E82',
          700: '#0D5859',
          800: '#0A4445',
          900: '#083536',
        },
      },
    },
  },
  plugins: [],
};
