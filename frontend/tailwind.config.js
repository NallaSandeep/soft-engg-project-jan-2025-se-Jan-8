/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'mono': ['Inconsolata', 'monospace'],
      },
      colors: {
        // Light theme colors
        light: {
          primary: '#ffffff',
          secondary: '#fafafa',
          accent: '#f5f5f5',
          text: {
            primary: '#1a1a1a',
            secondary: '#4b5563',
            tertiary: '#6b7280'
          }
        },
        // Dark theme colors
        dark: {
          primary: '#121212',
          secondary: '#1e1e1e',
          accent: '#2d2d2d',
          text: {
            primary: '#ffffff',
            secondary: '#e5e5e5',
            tertiary: '#a3a3a3'
          }
        },
        // Brand colors
        brand: {
          primary: '#2563eb',
          secondary: '#3b82f6',
          success: '#16a34a',
          warning: '#d97706',
          error: '#dc2626',
          info: '#0284c7',
          // Hover states
          'primary-hover': '#1d4ed8',
          'secondary-hover': '#2563eb',
          'success-hover': '#15803d',
          'warning-hover': '#b45309',
          'error-hover': '#b91c1c',
          'info-hover': '#0369a1'
        }
      },
    },
  },
  plugins: [
  ],
}