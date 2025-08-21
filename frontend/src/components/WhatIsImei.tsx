'use client'

import { useTranslation } from '@/hooks/useTranslation'

export function WhatIsImei() {
  const { t } = useTranslation()

  return (
    <section id="what-is-imei" className="max-w-6xl mx-auto mb-12 sm:mb-16">
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-6 sm:p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center px-3 py-1 bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium mb-4">
            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            {t('information_guide')}
          </div>
          <h2 className="text-2xl sm:text-3xl font-semibold text-gray-900 dark:text-gray-100 mb-4">{t('titre_quest_ce_que_imei')}</h2>
          <p className="text-base sm:text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            {t('sous_titre_quest_ce_que_imei')}
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 mb-8">
          <div className="space-y-4">
            <div className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{t('identification_unique')}</h3>
                <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{t('description_identification_unique')}</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{t('securite_tracage')}</h3>
                <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{t('description_securite_tracage')}</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{t('registre_equipements')}</h3>
                <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{t('description_registre_equipements')}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6 text-center">{t('comment_trouver_imei')}</h3>
            
            <div className="space-y-6">
              <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                  <span className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm mr-3">1</span>
                  {t('methode_code_numerotation')}
                </h4>
                <div className="bg-gray-900 dark:bg-black/50 rounded-lg p-4 mb-3">
                  <code className="text-green-400 font-mono text-xl font-semibold">*#06#</code>
                </div>
                <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{t('description_code_numerotation')}</p>
              </div>
              
              <div className="space-y-3">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('autres_methodes')}</h4>
                <div className="space-y-2">
                  <div className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-white font-semibold text-xs">2</span>
                    <span className="text-gray-700 dark:text-gray-300 text-sm">{t('methode_parametres')}</span>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-white font-semibold text-xs">3</span>
                    <span className="text-gray-700 dark:text-gray-300 text-sm">{t('methode_batterie')}</span>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <span className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-white font-semibold text-xs">4</span>
                    <span className="text-gray-700 dark:text-gray-300 text-sm">{t('methode_boite')}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
