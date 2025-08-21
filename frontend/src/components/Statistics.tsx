'use client'

import { PublicStatsResponse } from '../api'
import { useTranslation } from '@/hooks/useTranslation'

interface StatisticsProps {
  stats: PublicStatsResponse | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export function Statistics({ stats, isLoading, error, onRefresh }: StatisticsProps) {
  const { t, currentLang } = useTranslation()

  return (
    <section className="max-w-6xl mx-auto mb-24">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 tracking-tight">{t('statistiques_systeme')}</h3>
          <p className="text-gray-600 dark:text-gray-300 mt-1">{t('donnees_publiques')}</p>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            !isLoading
              ? 'text-blue-700 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 dark:text-blue-300 dark:hover:text-blue-200 dark:bg-blue-900/50 dark:hover:bg-blue-900'
              : 'text-gray-400 bg-gray-50 dark:text-gray-500 dark:bg-gray-800 cursor-not-allowed'
          }`}
        >
          <svg className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>{t('actualiser')}</span>
        </button>
      </div>
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur border rounded-2xl p-8 shadow-xl">
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center space-x-3">
              <svg className="animate-spin w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-gray-600 dark:text-gray-400 font-medium">{t('chargement')}</span>
            </div>
          </div>
        )}
        {!isLoading && error && (
          <div className="text-center py-12">
            <div className="text-red-600 dark:text-red-400 font-medium">{t('erreur')}: {error}</div>
          </div>
        )}
        {!isLoading && stats && (
          <div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
              <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/50 dark:to-blue-900 rounded-2xl border border-blue-200 dark:border-blue-800">
                <div className="text-3xl font-black text-blue-900 dark:text-blue-200 mb-2">{stats.total_appareils?.toLocaleString()}</div>
                <div className="text-sm font-semibold uppercase tracking-wide text-blue-700 dark:text-blue-400">{t('appareils')}</div>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/50 dark:to-green-900 rounded-2xl border border-green-200 dark:border-green-800">
                <div className="text-3xl font-black text-green-900 dark:text-green-200 mb-2">{stats.total_recherches?.toLocaleString()}</div>
                <div className="text-sm font-semibold uppercase tracking-wide text-green-700 dark:text-green-400">{t('recherches')}</div>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/50 dark:to-purple-900 rounded-2xl border border-purple-200 dark:border-purple-800">
                <div className="text-3xl font-black text-purple-900 dark:text-purple-200 mb-2">{stats.recherches_30_jours?.toLocaleString()}</div>
                <div className="text-sm font-semibold uppercase tracking-wide text-purple-700 dark:text-purple-400">{t('jours_30')}</div>
              </div>
              <div className="text-center p-6 bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/50 dark:to-indigo-900 rounded-2xl border border-indigo-200 dark:border-indigo-800">
                <div className="text-3xl font-black text-indigo-900 dark:text-indigo-200 mb-2">{stats.total_tacs_disponibles?.toLocaleString()}</div>
                <div className="text-sm font-semibold uppercase tracking-wide text-indigo-700 dark:text-indigo-400">TAC</div>
              </div>
            </div>
            {stats.repartition_statuts && Object.keys(stats.repartition_statuts).length > 0 && (
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-2xl p-6 border border-gray-200 dark:border-gray-600">
                <h4 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4">{t('repartition_statuts_imei')}</h4>
                <div className="flex flex-wrap gap-3">
                  {Object.entries(stats.repartition_statuts).map(([status, count]) => (
                    <div key={status} className="px-4 py-2 bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700 text-gray-700 dark:text-gray-300 font-medium shadow-sm">
                      {t(status)}: <span className="font-bold text-gray-900 dark:text-gray-100">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
              <span>{t('derniere_mise_a_jour')}: {new Date(stats.derniere_mise_a_jour).toLocaleString(currentLang === 'ar' ? 'ar-AE' : currentLang === 'en' ? 'en-US' : 'fr-FR')}</span>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
