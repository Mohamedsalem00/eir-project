'use client'

import { useLanguage } from '@/contexts/LanguageContext'

const languageOptions = [
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦' }
]

export default function LanguageSelector() {
  const { currentLang, setCurrentLang } = useLanguage()

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600">Langue:</span>
      <select 
        value={currentLang} 
        onChange={(e) => setCurrentLang(e.target.value as 'fr' | 'en' | 'ar')}
        className="px-3 py-1 border border-gray-300 rounded-md bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {languageOptions.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  )
}
