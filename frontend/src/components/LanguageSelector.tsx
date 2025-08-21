'use client'

import { useLanguage } from '@/contexts/LanguageContext'
import { useTranslation } from '@/hooks/useTranslation'

const languageOptions = [
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'ar', name: 'العربية', flag: '🇲🇷' }
]

export default function LanguageSelector() {
  const { currentLang, setCurrentLang } = useLanguage()
  const { t } = useTranslation()

  return (
    <div className="relative">
      <select 
        value={currentLang} 
        onChange={(e) => setCurrentLang(e.target.value as 'fr' | 'en' | 'ar')}
        className="appearance-none w-full pl-4 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-full bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
        aria-label={t('language')}
      >
        {languageOptions.map((lang) => (
          <option key={lang.code} value={lang.code} className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200">
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-700 dark:text-gray-400">
        <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
      </div>
    </div>
  )
}
