'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useTranslation } from '@/hooks/useTranslation'
import { SearchHistoryService } from '@/api'
import { SearchHistoryItem } from '@/types/api'
import { authService } from '@/api/auth'
import Unauthorized401 from '../../src/components/Unauthorized401'

export function SearchHistory() {
  const { user } = useAuth()
      // Get token from the authService if the user exists
  const authToken = user ? authService.getAuthToken() : undefined;
  const { t, currentLang } = useTranslation()
  const [history, setHistory] = useState<SearchHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isUnauthorized, setIsUnauthorized] = useState(false)

  const fetchHistory = useCallback(async () => {
    if (!authToken) return;

    setIsLoading(true)
    setError(null)
    const response = await SearchHistoryService.getSearchHistory(authToken, currentLang)

    if (response.success && response.data) {
      setHistory(response.data.searches)
    } else {
      // Detect 401 error and show Unauthorized401
      if (response.status === 401 || (response.error && response.error.toLowerCase().includes('401'))) {
        setIsUnauthorized(true)
        setError(null)
      } else {
        setError(response.error || t('erreur_inconnue'))
      }
    }
    setIsLoading(false)
  }, [authToken, currentLang, t])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  if (isUnauthorized) {
      return <Unauthorized401 supportEmail="support@eir.com" />
  }

  return (
    <div className="mt-12 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{t('historique_recherches')}</h2>
        <button
          onClick={fetchHistory}
          disabled={isLoading}
          className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors disabled:opacity-50"
        >
          {t('actualiser')}
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg animate-pulse">
              <div className="h-5 bg-gray-200 rounded w-1/3"></div>
              <div className="h-5 bg-gray-200 rounded w-1/4"></div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-8 text-red-600">
          <p>{error}</p>
        </div>
      ) : history.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>{t('aucune_recherche_historique')}</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('date')}
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('imei_recherche')}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.map((item) => (
                <tr key={item.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(item.date_recherche).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                    {item.imei_recherche}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
