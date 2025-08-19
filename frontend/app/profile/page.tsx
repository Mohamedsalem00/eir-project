'use client'

import { useAuth } from '../../src/contexts/AuthContext'
import { useLanguage } from '../../src/contexts/LanguageContext'
import  Navigation  from '../../src/components/Navigation'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import AccessDenied from '../../src/components/AccessDenied'
import { authService } from '../../src/api'
import Unauthorized401 from '../../src/components/Unauthorized401'

interface ProfileData {
  id: string
  nom: string
  email: string
  type_utilisateur: string
  date_creation?: string
  derniere_connexion?: string
  statut_compte: string
  permissions: string[]
  statistiques: {
    nombre_connexions: number
    activites_7_derniers_jours: number
    compte_cree_depuis_jours: number
    derniere_activite?: string
  }
}

export default function ProfilePage() {
  const { user, logout } = useAuth()
  
  const { t } = useLanguage()
  const router = useRouter()
  const [profileData, setProfileData] = useState<ProfileData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUnauthorized, setIsUnauthorized] = useState(false)


  const allowedTypes = [process.env.NEXT_PUBLIC_ADMIN_USER_TYPE && 'administrateur', process.env.NEXT_PUBLIC_OPERATOR_USER_TYPE && 'operateur', process.env.NEXT_PUBLIC_REGULAR_USER_TYPE && 'utilisateur_authentifie']
  const userType = user?.type_utilisateur
  
  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login')
      return
    }

    // Fetch detailed profile data using authService
    const fetchProfile = async () => {
      try {
        const data = await authService.getProfile()
        setProfileData(data)
      } catch (error) {
        console.error('Error fetching profile:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchProfile()
  }, [user, isLoading, router])



  // Not authenticated
  if (!user) {
    return <AccessDenied supportEmail="support@eir.com" />
  }

  // Not allowed
  if (!allowedTypes.includes(userType)) {
    return <AccessDenied supportEmail="support@eir.com" />
  }

  if (isUnauthorized) {
      return <Unauthorized401 supportEmail="support@eir.com" />
  }

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/20">
      <Navigation />
      
      <main className="container mx-auto px-4 sm:px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="mx-auto h-24 w-24 bg-blue-100 rounded-full flex items-center justify-center mb-6">
              <svg className="h-12 w-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              {t('profil_utilisateur')}
            </h1>
            <p className="text-xl text-gray-600">
              {t('gerer_votre_compte')}
            </p>
          </div>

          {/* Profile Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{t('informations_personnelles')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-500">{t('nom')}</label>
                <p className="mt-1 text-lg font-semibold text-gray-900">{profileData?.nom || user.nom}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">{t('email')}</label>
                <p className="mt-1 text-lg font-semibold text-gray-900">{profileData?.email || user.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">{t('type_utilisateur')}</label>
                <p className="mt-1 text-lg font-semibold text-gray-900">{t(profileData?.type_utilisateur || user.type_utilisateur)}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">{t('statut_compte')}</label>
                <span className={`mt-1 inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
                  profileData?.statut_compte === 'active' 
                    ? 'text-green-800 bg-green-100' 
                    : 'text-red-800 bg-red-100'
                }`}>
                  {t(profileData?.statut_compte || 'actif')}
                </span>
              </div>
            </div>
          </div>

          {/* Statistics */}
          {profileData?.statistiques && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">{t('statistiques_compte')}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center p-6 bg-blue-50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-900 mb-2">
                    {profileData.statistiques.nombre_connexions}
                  </div>
                  <div className="text-sm font-medium text-blue-700">{t('connexions_total')}</div>
                </div>
                <div className="text-center p-6 bg-green-50 rounded-lg">
                  <div className="text-3xl font-bold text-green-900 mb-2">
                    {profileData.statistiques.activites_7_derniers_jours}
                  </div>
                  <div className="text-sm font-medium text-green-700">{t('activites_7_jours')}</div>
                </div>
                <div className="text-center p-6 bg-purple-50 rounded-lg">
                  <div className="text-3xl font-bold text-purple-900 mb-2">
                    {profileData.statistiques.compte_cree_depuis_jours}
                  </div>
                  <div className="text-sm font-medium text-purple-700">{t('jours_compte')}</div>
                </div>
                <div className="text-center p-6 bg-indigo-50 rounded-lg">
                  <div className="text-3xl font-bold text-indigo-900 mb-2">
                    {profileData.statistiques.derniere_activite ? 
                      new Date(profileData.statistiques.derniere_activite).toLocaleDateString() : 
                      t('jamais')}
                  </div>
                  <div className="text-sm font-medium text-indigo-700">{t('derniere_activite')}</div>
                </div>
              </div>
            </div>
          )}

          {/* Permissions */}
          {profileData?.permissions && profileData.permissions.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">{t('permissions')}</h2>
              <div className="flex flex-wrap gap-3">
                {profileData.permissions.map((permission) => (
                  <span 
                    key={permission}
                    className="px-4 py-2 bg-blue-100 text-blue-800 text-sm font-medium rounded-full"
                  >
                    {t(permission)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Account Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{t('actions_compte')}</h2>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors">
                {t('modifier_profil')}
              </button>
              <button className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors">
                {t('changer_mot_de_passe')}
              </button>
              <button 
                onClick={logout}
                className="px-6 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
              >
                {t('deconnexion')}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
