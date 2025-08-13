'use client'

import { useLanguage } from '../../src/contexts/LanguageContext'

export default function TestPage() {
  const { t, currentLang, setCurrentLang } = useLanguage()

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4">Test des Traductions</h1>
        
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Langue:</label>
          <select 
            value={currentLang} 
            onChange={(e) => setCurrentLang(e.target.value as 'fr' | 'en' | 'ar')}
            className="border rounded px-3 py-2"
          >
            <option value="fr">Français</option>
            <option value="en">English</option>
            <option value="ar">العربية</option>
          </select>
        </div>

        <div className="space-y-4">
          <div>
            <strong>Titre:</strong> {t('titre')}
          </div>
          <div>
            <strong>Vérification IMEI:</strong> {t('verification_imei')}
          </div>
          <div>
            <strong>Nouvelle recherche:</strong> {t('nouvelle_recherche')}
          </div>
          <div>
            <strong>Test paramètres:</strong> {t('details_imei', { imei: '123456789012345' })}
          </div>
        </div>
      </div>
    </div>
  )
}
