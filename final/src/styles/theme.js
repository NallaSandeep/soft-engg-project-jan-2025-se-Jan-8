import { createContext, useContext, useState, useEffect } from 'react';

export const ThemeContext = createContext({
  theme: 'light',
  toggleTheme: () => {},
});

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) return savedTheme;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    // Update document class and local storage
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Theme constants
export const themeConfig = {
  // colors: {
  //   light: {
  //     primary: '#ffffff',
  //     secondary: '#f3f4f6',
  //     accent: '#e5e7eb',
  //     text: {
  //       primary: '#1a1a1a',
  //       secondary: '#4b5563'
  //     }
  //   },
  //   dark: {
  //     primary: '#1a1a1a',
  //     secondary: '#2d2d2d',
  //     accent: '#3b3b3b',
  //     text: {
  //       primary: '#ffffff',
  //       secondary: '#a0a0a0'
  //     }
  //   },
  //   brand: {
  //     primary: '#3b82f6',
  //     secondary: '#60a5fa',
  //     success: '#22c55e',
  //     warning: '#f59e0b',
  //     error: '#ef4444'
  //   }
  // },
  // spacing: {
  //   sidebar: '280px',
  //   chat: '320px'
  // },
  // transition: {
  //   default: 'all 0.3s ease',
  //   fast: 'all 0.15s ease',
  //   slow: 'all 0.5s ease'
  // },
  // shadow: {
  //   sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  //   md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  //   lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
  // }
}; 