'use client'

import { useAuth } from '../../src/contexts/AuthContext'
import { useLanguage } from '../../src/contexts/LanguageContext'
import  Navigation  from '../../src/components/Navigation'
import { SearchHistory } from '../../src/components/SearchHistory'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useAuthGuard } from '../../src/hooks/useAuthGuard'
import AccessDenied from '../../src/components/AccessDenied'

export default function DashboardPage() {
  const { user, isLoading } = useAuth() 
  const { t } = useLanguage()
  const router = useRouter()

  // Only allow admin and operator
  const allowedTypes = [process.env.NEXT_PUBLIC_ADMIN_USER_TYPE && 'administrateur', process.env.NEXT_PUBLIC_OPERATOR_USER_TYPE && 'operateur']
  const userType = user?.type_utilisateur

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/20 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">{t('chargement')}</p>
        </div>
      </div>
    )
  }

  // Not authenticated
  if (!user) {
    return <AccessDenied supportEmail="support@eir.com" />
  }

  // Not allowed
  if (!allowedTypes.includes(userType)) {
    return <AccessDenied supportEmail="support@eir.com" />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/20">
      {/* The Navigation component gets user data from the context automatically */}
      <Navigation />
      
      <main className="container mx-auto px-4 sm:px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              {t('bienvenue')}, {user.nom}!
            </h1>
            <p className="text-xl text-gray-600">
              {t('tableau_bord_description')}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('recherche_imei')}</h3>
              <p className="text-gray-600 text-sm mb-4">{t('recherche_imei_description')}</p>
              <a href="/" className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
                {t('commencer')}
              </a>
            </div>

            {/* Profile Management */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('profil')}</h3>
              <p className="text-gray-600 text-sm mb-4">{t('gerer_profil_description')}</p>
              <a href="/profile" className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors">
                {t('gerer')}
              </a>
            </div>

            {/* API Testing */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('test_api')}</h3>
              <p className="text-gray-600 text-sm mb-4">{t('test_api_description')}</p>
              <a href="/test" className="inline-flex items-center px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors">
                {t('tester')}
              </a>
            </div>
          </div>

          {/* User Info */}
          <div className="mt-12 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{t('informations_compte')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-500">{t('nom')}</label>
                <p className="mt-1 text-lg font-semibold text-gray-900">{user.nom}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">{t('email')}</label>
                <p className="mt-1 text-lg font-semibold text-gray-900">{user.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">{t('type_utilisateur')}</label>
                <p className="mt-1 text-lg font-semibold text-gray-900">{t(user.type_utilisateur)}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">{t('statut')}</label>
                <span className="mt-1 inline-flex px-3 py-1 text-sm font-semibold text-green-800 bg-green-100 rounded-full">
                  {t('actif')}
                </span>
              </div>
            </div>
          </div>

          {/* 👇 Render the new Search History component */}
          <SearchHistory />
        </div>
      </main>
    </div>
  )
}
