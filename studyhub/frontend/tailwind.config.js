module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'code': ['"Source Code Pro"', 'monospace'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            pre: {
              backgroundColor: '#eff0f1',
              color: '#073763',
              overflowX: 'auto',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              padding: '0.5rem',
              fontFamily: '"Source Code Pro", monospace',
              fontSize: '1rem',
              fontWeight: '500',
              width: '100%',
            },
            'pre code': {
              backgroundColor: 'transparent',
              borderWidth: '0',
              borderRadius: '0',
              padding: '0',
              color: 'inherit',
              fontSize: '0.875rem',
              fontFamily: 'inherit',
              lineHeight: '1.7142857',
              whiteSpace: 'pre-wrap',
            },
            code: {
              backgroundColor: '#f3f4f6',
              padding: '0.2em 0.4em',
              borderRadius: '0.25rem',
              fontWeight: '400',
            },
            'code::before': {
              content: '""'
            },
            'code::after': {
              content: '""'
            }
          }
        },
        // Add dark mode styles
        invert: {
          css: {
            code: {
              backgroundColor: '#282b2d',
              color: '#e2e8f0',
            },
            'code::before': {
              content: '""'
            },
            'code::after': {
              content: '""'
            },
            pre: {
              backgroundColor: '#282b2d',
              color: '#cfe2f3',
            },
            'pre code': {
              color: '#cfe2f3',
            },
          }
        }
      }
    }
  },
  plugins: [
    require('@tailwindcss/typography'),
  ]
}