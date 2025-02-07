/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Light theme
        light: {
          primary: '#ffffff',
          secondary: '#f3f4f6',
          accent: '#e5e7eb',
          text: {
            primary: '#1a1a1a',
            secondary: '#4b5563'
          }
        },
        // Dark theme
        dark: {
          primary: '#1a1a1a',
          secondary: '#2d2d2d',
          accent: '#3b3b3b',
          text: {
            primary: '#ffffff',
            secondary: '#a0a0a0'
          }
        },
        // Brand colors
        brand: {
          primary: '#3b82f6',
          secondary: '#60a5fa',
          success: '#22c55e',
          warning: '#f59e0b',
          error: '#ef4444'
        }
      },
      spacing: {
        'sidebar': '280px',
        'chat': '320px'
      }
    },
  },
  plugins: [],
} 