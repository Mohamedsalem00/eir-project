'use client'

import { useLanguage } from '@/contexts/LanguageContext'
import { useTranslation } from '@/hooks/useTranslation'

export function LanguageSelector() {
  const { currentLang, setCurrentLang, supportedLanguages } = useLanguage()
  const { t } = useTranslation()

  const languageNames = {
    fr: 'Français',
    en: 'English',
    ar: 'العربية'
  }

  return (
    <div className="flex items-center space-x-2 rtl:space-x-reverse">
      <label htmlFor="language-select" className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {currentLang === 'ar' ? 'اللغة' : currentLang === 'en' ? 'Language' : 'Langue'}:
      </label>
      <select
        id="language-select"
        value={currentLang}
        onChange={(e) => setCurrentLang(e.target.value as any)}
        className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
      >
        {supportedLanguages.map((lang) => (
          <option key={lang} value={lang}>
            {languageNames[lang]}
          </option>
        ))}
      </select>
    </div>
  )
}
