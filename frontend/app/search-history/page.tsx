
'use client'

import AccessDenied from '../../src/components/AccessDenied'
import Navigation from '../../src/components/Navigation'
import { useAuth } from '../../src/contexts/AuthContext'
import { useLanguage } from '../../src/contexts/LanguageContext'
import { SearchHistory } from '../../src/components/SearchHistory'


export default function SearchHistoryPage() {
  const { user, isLoading } = useAuth() 
  const { t } = useLanguage()


  // Only allow authenticated users
  const allowedTypes = [process.env.NEXT_PUBLIC_REGULAR_USER_TYPE && 'utilisateur_authentifie' , process.env.NEXT_PUBLIC_ADMIN_USER_TYPE && 'administrateur', process.env.NEXT_PUBLIC_OPERATOR_USER_TYPE && 'operateur']
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
      <Navigation />
      <main className="container mx-auto px-4 py-12">
        <SearchHistory />
      </main>
    </div>
  )
}
