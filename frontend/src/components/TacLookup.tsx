'use client'

import { useState } from 'react'
import { TACService, TACResponse } from '../api'
import { useTranslation } from '@/hooks/useTranslation'

interface TacLookupProps {
  isApiConnected: boolean | null;
}

// A simple skeleton loader component for the results card
function ResultSkeleton() {
  return (
    <div className="bg-white/90 backdrop-blur border border-gray-200 rounded-2xl p-8 shadow-xl animate-pulse">
      <div className="flex items-center justify-between mb-6 pb-6 border-b border-gray-200">
        <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        <div className="h-8 bg-gray-200 rounded-full w-24"></div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gray-100 rounded-xl p-4 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-6 bg-gray-300 rounded w-3/4"></div>
        </div>
        <div className="bg-gray-100 rounded-xl p-4 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-6 bg-gray-300 rounded w-3/4"></div>
        </div>
        <div className="bg-gray-100 rounded-xl p-4 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-6 bg-gray-300 rounded w-3/4"></div>
        </div>
      </div>
    </div>
  )
}

export function TacLookup({ isApiConnected }: TacLookupProps) {
  const { t, currentLang } = useTranslation()
  const [tac, setTac] = useState('')
  const [result, setResult] = useState<TACResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const searchTAC = async () => {
    setError(null)
    setResult(null)
    
    if (!isApiConnected) {
      setError(t('api_deconnectee') + ' - ' + t('service_indisponible'))
      return
    }
    
    const cleanTac = tac.replace(/\D/g, '')
    if (cleanTac.length !== 8) {
      setError(t('tac_invalide_longueur'))
      return
    }
    setIsLoading(true)
    const res = await TACService.searchTAC(cleanTac, currentLang)
    if (res.success && res.data) {
      setResult(res.data)
    } else {
      setError(res.error || t('erreur_recherche_tac'))
    }
    setIsLoading(false)
  }

  const handleTacChange = (value: string) => {
    setTac(value.replace(/\D/g, '').slice(0, 8));
    if (error) setError(null); // Clear error on new input
  };

  return (
    <section className="max-w-4xl mx-auto mb-28">
      <div className="text-center mb-8">
        <h3 className="text-2xl font-bold text-gray-900 tracking-tight mb-2">{t('recherche_tac')}</h3>
        <p className="text-gray-600">{t('description_recherche_tac')}</p>
      </div>
      <div className="bg-white/90 backdrop-blur border rounded-2xl p-8 shadow-xl mb-6">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex-1">
            <label className="block text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">
              {t('code_tac')}
              <span className="text-red-500 ml-1">*</span>
            </label>
            <input
              type="text"
              value={tac}
              onChange={(e) => handleTacChange(e.target.value)}
              placeholder={t('entrer_tac')}
              className="w-full p-4 border-2 border-gray-300 rounded-xl text-lg font-mono focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all"
              maxLength={8}
              disabled={isLoading}
              dir="ltr"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={searchTAC}
              disabled={isLoading || tac.replace(/\D/g,'').length !== 8 || !isApiConnected}
              className={`h-16 w-full md:w-auto font-bold px-8 rounded-xl text-lg tracking-wide transition-all transform ${
                tac.replace(/\D/g,'').length === 8 && !isLoading && isApiConnected
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl hover:scale-105' 
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {t('recherche_en_cours')}
                </div>
              ) : t('rechercher')}
            </button>
          </div>
        </div>
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center space-x-3">
            <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-red-700 font-medium">{error}</span>
          </div>
        )}
      </div>
      
      {/* Conditional Rendering for Loading, Error, and Result States */}
      {isLoading && <ResultSkeleton />}

      {result && (
        <div className={`bg-white/90 backdrop-blur border rounded-2xl p-8 shadow-xl transition-all duration-300 ${result.trouve ? 'border-blue-200' : 'border-yellow-200'}`}>
          <div className="flex items-center justify-between mb-6 pb-6 border-b">
             <h4 className="text-xl font-bold text-gray-800 flex items-center">
                <svg className="w-6 h-6 mr-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 3v7h10V7H5z" clipRule="evenodd" />
                </svg>
                {t('resultat_tac')}
             </h4>
             <div className={`px-4 py-2 rounded-full font-semibold text-sm capitalize ${result.trouve ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {result.trouve ? t('trouve', { fallback: 'Found' }) : t('non_trouve', { fallback: 'Not Found' })}
             </div>
          </div>

          {!result.trouve ? (
            <div className="text-center py-8">
              <p className="text-gray-600 text-lg">{t('tac_non_trouve_base')}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { field: 'marque', label: t('marque') },
                { field: 'modele', label: t('modele') },
                { field: 'type_appareil', label: t('type_appareil') },
                { field: 'categorie', label: t('categorie') },
                { field: 'fabricant', label: t('fabricant') },
                { field: 'statut', label: t('statut') }
              ].map(({ field, label }) => {
                const value = result[field as keyof TACResponse];
                if (!value) return null;
                return (
                  <div key={field} className="bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-4">
                    <span className="block text-gray-500 font-semibold text-sm uppercase tracking-wide mb-2">{label}</span>
                    <span className="font-bold text-gray-900 text-lg">{String(value)}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </section>
  )
}
