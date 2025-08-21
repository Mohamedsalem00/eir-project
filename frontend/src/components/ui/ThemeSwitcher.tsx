'use client'

import { useTheme } from '@/contexts/ThemeProvider' // Adjust the import path as needed

// Icons for the buttons
const SunIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
);

const MoonIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
);

const SystemIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>
);


export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()

  const buttons = [
    { name: 'light', icon: <SunIcon /> },
    { name: 'dark', icon: <MoonIcon /> },
    { name: 'system', icon: <SystemIcon /> },
  ]

  return (
    <div className="flex items-center p-1 bg-gray-200 dark:bg-gray-800 rounded-full">
      {buttons.map((btn) => {
        const isActive = theme === btn.name
        return (
          <button
            key={btn.name}
            onClick={() => setTheme(btn.name as 'light' | 'dark' | 'system')}
            className={`
              p-2 rounded-full transition-colors duration-200 capitalize
              ${isActive 
                ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400' 
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-700'
              }
            `}
            aria-label={`Switch to ${btn.name} mode`}
          >
            {btn.icon}
          </button>
        )
      })}
    </div>
  )
}
