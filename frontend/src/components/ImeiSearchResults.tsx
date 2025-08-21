'use client'

import { IMEIResponse, RateLimitInfo } from '@/api'
import { useTranslation } from '@/hooks/useTranslation'

interface ImeiSearchResultsProps {
  result: IMEIResponse | null;
  error: string | null;
  rateLimitInfo: RateLimitInfo | null;
}

export function ImeiSearchResults({ result, error, rateLimitInfo }: ImeiSearchResultsProps) {
  const { t } = useTranslation()

  const getStatusTheme = (status: string) => {
    switch (status) {
      case 'active':
        return {
          badge: 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300',
          border: 'border-green-200 dark:border-green-800',
          icon: (
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          )
        };
      case 'bloque':
        return {
          badge: 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300',
          border: 'border-red-200 dark:border-red-800',
          icon: (
            <div className="w-12 h-12 bg-red-100 dark:bg-red-900/50 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
          )
        };
      default:
        return {
          badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300',
          border: 'border-yellow-200 dark:border-yellow-800',
          icon: (
            <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/50 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
          )
        };
    }
  };

  if (!result && !error) {
    return null
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto mb-16">
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-red-200 dark:border-red-700 shadow-sm p-6 sm:p-8">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-red-100 dark:bg-red-900/50 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-red-800 dark:text-red-300">{t('erreur_verification')}</h3>
              <p className="text-red-700 dark:text-red-400 mt-1">{error}</p>
              {rateLimitInfo && (
                <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-500/30 text-sm">
                  <h4 className="font-semibold text-red-900 dark:text-red-300">{t('info_limite_taux')}</h4>
                  <p className="text-red-700 dark:text-red-400">{t('ressayer_apres')}: {rateLimitInfo.retryAfter}s</p>
                  <p className="text-red-700 dark:text-red-400">{t('limite')}: {rateLimitInfo.limit} {t('requetes')}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (result) {
    if (!result.trouve) {
      return (
        <section className="max-w-4xl mx-auto mb-16">
          <div className="bg-white dark:bg-gray-800 rounded-2xl border border-yellow-200 dark:border-yellow-700 shadow-lg p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 pb-6 border-b border-yellow-200 dark:border-yellow-700">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{t('titre_resultats')}</h3>
                <p className="text-lg text-gray-700 dark:text-gray-300 font-mono mt-1">{result.imei}</p>
              </div>
              <div className="mt-4 sm:mt-0 px-4 py-2 rounded-full font-semibold text-sm capitalize bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300">
                {t('non_trouve', { fallback: 'Not Found' })}
              </div>
            </div>
            <div className="text-center py-4">
              <p className="text-lg text-gray-700 dark:text-gray-300">{result.message}</p>
            </div>
          </div>
        </section>
      );
    }

    const theme = getStatusTheme(result.statut);
    return (
      <section className="max-w-4xl mx-auto mb-16">
        <div className={`bg-white dark:bg-gray-800 rounded-2xl border ${theme.border} shadow-lg p-6 sm:p-8`}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 pb-6 border-b dark:border-gray-700">
            <div className="flex items-center space-x-4">
              {theme.icon}
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{t('titre_resultats')}</h3>
                <p className="text-lg text-gray-700 dark:text-gray-300 font-mono mt-1">{result.imei}</p>
              </div>
            </div>
            <div className={`mt-4 sm:mt-0 px-4 py-2 rounded-full font-semibold text-sm capitalize ${theme.badge}`}>
              {t(result.statut)}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span className="block text-sm font-medium text-gray-500 dark:text-gray-400">{t('marque')}</span>
              <p className="text-lg font-semibold text-gray-800 dark:text-gray-200">{result.appareil?.marque || 'N/A'}</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span className="block text-sm font-medium text-gray-500 dark:text-gray-400">{t('modele')}</span>
              <p className="text-lg font-semibold text-gray-800 dark:text-gray-200">{result.appareil?.modele || 'N/A'}</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span className="block text-sm font-medium text-gray-500 dark:text-gray-400">{t('numero_serie')}</span>
              <p className="text-lg font-semibold text-gray-800 dark:text-gray-200 font-mono">{result.appareil?.numero_serie || 'N/A'}</p>
            </div>
             <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span className="block text-sm font-medium text-gray-500 dark:text-gray-400">{t('message')}</span>
              <p className="text-lg font-semibold text-gray-800 dark:text-gray-200">{result.message}</p>
            </div>
          </div>
        </div>
      </section>
    )
  }

  return null;
}
