'use client'

import { useTranslation } from '@/hooks/useTranslation'

interface ApiStatusProps {
  isApiConnected: boolean | null;
  isLoading: boolean;
  onRetry: () => void;
}

export function ApiStatus({ isApiConnected, isLoading, onRetry }: ApiStatusProps) {
  const { t } = useTranslation()

  return (
    <div className="text-center space-y-6">
      {isLoading ? (
        <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600 rounded-full font-medium shadow-sm">
          <div className="w-3 h-3 bg-gray-400 rounded-full mr-3 animate-pulse"></div>
          <span>{t('chargement')}...</span>
        </div>
      ) : isApiConnected ? (
        <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/50 dark:to-emerald-900/50 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800 rounded-full font-medium shadow-sm">
          <div className="w-3 h-3 bg-green-500 rounded-full mr-3 animate-pulse"></div>
          <span>{t('api_connectee')}</span>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-900/50 dark:to-rose-900/50 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800 rounded-full font-medium shadow-sm">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
            <span>{t('api_deconnectee')} - {t('service_indisponible')}</span>
          </div>
          <button
            onClick={onRetry}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 dark:bg-red-900/50 dark:hover:bg-red-900 dark:text-red-300 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
             <svg className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {isLoading ? t('chargement') : t('verifier_connexion')}
          </button>
        </div>
      )}
      <div>
        <a 
          href="/test" 
          className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 text-white rounded-2xl font-bold text-lg transition-all transform hover:scale-105 hover:shadow-2xl"
        >
          <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {t('interface_test')}
        </a>
      </div>
    </div>
  )
}
