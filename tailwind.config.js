/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./kns/**/*.{html,js}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
        serif: ['DM Serif Text', 'serif'],
      },
      colors: {
        knsPrimary: {
          DEFAULT: '#982b1c', // base color (500)
          50: '#fdf3f2',
          100: '#fbe3e0',
          200: '#f5bcb8',
          300: '#ef8f89',
          400: '#e56157',
          500: '#982b1c',
          600: '#872417',
          700: '#741d13',
          800: '#61160f',
          900: '#4f100b',
        },
        knsSecondary: {
          DEFAULT: '#048a81', // base color (500)
          50: '#f2fcfb',
          100: '#dff9f6',
          200: '#b9f0ea',
          300: '#8be5dd',
          400: '#5ad9cf',
          500: '#048a81',
          600: '#02766e',
          700: '#026259',
          800: '#014d45',
          900: '#003b34',
        },
        knsLight: {
          DEFAULT: '#fcfff7', // base color (100)
          50: '#ffffff',
          100: '#fcfff7',
          200: '#f7faeb',
          300: '#f2f6de',
          400: '#e9f1d1',
          500: '#e0ecc4',
          600: '#d7e7b6',
          700: '#cce0a8',
          800: '#c2d99a',
          900: '#b7d18c',
        },
        knsDark: {
          DEFAULT: '#0f0f0f', // base color (900)
          50: '#e5e5e5',
          100: '#cccccc',
          200: '#b3b3b3',
          300: '#999999',
          400: '#808080',
          500: '#666666',
          600: '#4d4d4d',
          700: '#333333',
          800: '#1a1a1a',
          900: '#0f0f0f',
        },
      },
    },
    screens: {
      xs: '576px',
      sm: '768px',
      md: '992px',
      lg: '1200px',
      xl: '1440px',
    },
  },
  plugins: [],
};
