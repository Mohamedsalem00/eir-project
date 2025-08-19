'use client'

import { useAuth } from '../../src/contexts/AuthContext'
import { useLanguage } from '../../src/contexts/LanguageContext'
import Navigation from '../../src/components/Navigation'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import AccessDenied from '../../src/components/AccessDenied'
import { authService } from '../../src/api'
import Unauthorized401 from '../../src/components/Unauthorized401'
import { ProfileData } from '../../src/types/Profile'
import ProfileSkeleton from '../../src/components/ui/ProfileSkeleton'

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const { t } = useLanguage()
  const router = useRouter()
  const [profileData, setProfileData] = useState<ProfileData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUnauthorized, setIsUnauthorized] = useState(false)

  const allowedTypes = [
    process.env.NEXT_PUBLIC_ADMIN_USER_TYPE && 'administrateur',
    process.env.NEXT_PUBLIC_OPERATOR_USER_TYPE && 'operateur',
    process.env.NEXT_PUBLIC_REGULAR_USER_TYPE && 'utilisateur_authentifie',
  ]
  const userType = user?.type_utilisateur

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login')
      return
    }
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

  // Access control
  if (!user) return <AccessDenied supportEmail="support@eir.com" />
  if (!allowedTypes.includes(userType)) return <AccessDenied supportEmail="support@eir.com" />
  if (isUnauthorized) return <Unauthorized401 supportEmail="support@eir.com" />


  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        {isLoading ? (
          <ProfileSkeleton />
        ) : (
        <div className="max-w-6xl mx-auto">
          
          {/* Header Section */}
          <div className="mb-12">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="px-6 sm:px-8 lg:px-12 py-8 sm:py-12">
                <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 sm:gap-8">
                  {/* Avatar */}
                  <div className="relative">
                    <div className="h-24 w-24 sm:h-28 sm:w-28 rounded-full bg-gray-600 flex items-center justify-center shadow-sm">
                      <svg className="h-12 w-12 sm:h-14 sm:w-14 text-white" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                      </svg>
                    </div>
                  </div>
                  
                  {/* User Info */}
                  <div className="flex-1 text-center sm:text-left">
                    <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-2">
                      {profileData?.nom || user.nom}
                    </h1>
                    {/* FIXED: Font size is now responsive */}
                    <p className="text-base sm:text-lg text-gray-600 mb-3">{profileData?.email || user.email}</p>
                    <div className="flex flex-wrap justify-center sm:justify-start gap-3">
                      <span className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-gray-100 text-gray-800 border border-gray-200">
                        {t(profileData?.type_utilisateur || user.type_utilisateur)}
                      </span>
                      <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium border ${
                        profileData?.statut_compte === 'active' 
                          ? 'bg-green-50 text-green-700 border-green-200' 
                          : 'bg-red-50 text-red-700 border-red-200'
                      }`}>
                        {t(profileData?.statut_compte || 'actif')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-8">
              
              {/* Personal Information */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                <div className="px-6 sm:px-8 py-6 border-b border-gray-200">
                  {/* FIXED: Font size is now responsive */}
                  <h2 className="text-lg md:text-xl font-semibold text-gray-900 flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-gray-100 flex items-center justify-center">
                      <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    {t('informations_personnelles')}
                  </h2>
                </div>
                <div className="p-6 sm:p-8">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <ProfileField 
                      label={t('nom')} 
                      value={profileData?.nom || user.nom}
                      icon={
                        <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      }
                    />
                    <ProfileField 
                      label={t('email')} 
                      value={profileData?.email || user.email}
                      icon={
                        <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                        </svg>
                      }
                    />
                  </div>
                </div>
              </div>

              {/* Permissions */}
              {profileData?.permissions && profileData.permissions.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                  <div className="px-6 sm:px-8 py-6 border-b border-gray-200">
                    {/* FIXED: Font size is now responsive */}
                    <h2 className="text-lg md:text-xl font-semibold text-gray-900 flex items-center gap-3">
                      <div className="h-8 w-8 rounded-lg bg-gray-100 flex items-center justify-center">
                        <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159-.026-1.563.434L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1221.75 8.25z" />
                        </svg>
                      </div>
                      {t('permissions')}
                    </h2>
                  </div>
                  <div className="p-6 sm:p-8">
                    <div className="flex flex-wrap gap-3">
                      {profileData.permissions.map((permission, index) => (
                        <span key={index} className="inline-flex items-center px-4 py-2 bg-gray-50 text-gray-700 text-sm font-medium rounded-lg border border-gray-200">
                          <svg className="h-3 w-3 mr-2 text-gray-500" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {t(permission)}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-8">
              
              {/* Statistics */}
              {profileData?.statistiques && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                  <div className="px-6 py-6 border-b border-gray-200">
                    {/* FIXED: Font size is now responsive */}
                    <h2 className="text-base sm:text-lg font-semibold text-gray-900 flex items-center gap-3">
                      <div className="h-8 w-8 rounded-lg bg-gray-100 flex items-center justify-center">
                        <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                        </svg>
                      </div>
                      {t('statistiques_compte')}
                    </h2>
                  </div>
                  <div className="p-6 space-y-4">
                    <StatCard 
                      value={profileData.statistiques.nombre_connexions} 
                      label={t('connexions_total')} 
                      icon={
                        <svg className="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                        </svg>
                      }
                    />
                    <StatCard 
                      value={profileData.statistiques.activites_7_derniers_jours} 
                      label={t('activites_7_jours')} 
                      icon={
                        <svg className="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                        </svg>
                      }
                    />
                    <StatCard 
                      value={profileData.statistiques.compte_cree_depuis_jours} 
                      label={t('jours_compte')} 
                      icon={
                        <svg className="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5a2.25 2.25 0 002.25-2.25m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5a2.25 2.25 0 012.25 2.25v7.5" />
                        </svg>
                      }
                    />
                    <StatCard 
                      value={profileData.statistiques.derniere_activite ? new Date(profileData.statistiques.derniere_activite).toLocaleDateString() : t('jamais')} 
                      label={t('derniere_activite')} 
                      icon={
                        <svg className="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      }
                    />
                  </div>
                </div>
              )}

              {/* Quick Actions */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                <div className="px-6 py-6 border-b border-gray-200">
                  {/* FIXED: Font size is now responsive */}
                  <h2 className="text-base sm:text-lg font-semibold text-gray-900 flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-gray-100 flex items-center justify-center">
                      <svg className="h-4 w-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 011.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.56.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.893.149c-.425.07-.765.383-.93.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 01-1.45.12l-.737-.527c-.35-.25-.806-.272-1.203-.107-.397.165-.71.505-.781.929l-.149.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.019-.398-1.11-.94l-.148-.894c-.071-.424-.384-.764-.781-.93-.398-.164-.854-.142-1.204.108l-.738.527c-.447.32-1.06.269-1.45-.12l-.773-.774a1.125 1.125 0 01-.12-1.45l.527-.737c.25-.35.273-.806.108-1.204-.165-.397-.505-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0 .55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.107-1.204l-.527-.738a1.125 1.125 0 01.12-1.45l.773-.773a1.125 1.125 0 011.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    {t('actions_compte')}
                  </h2>
                </div>
                <div className="p-6 space-y-3">
                  <ActionButton 
                    onClick={() => {}} 
                    variant="primary"
                    icon={
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                      </svg>
                    }
                  >
                    {t('modifier_profil')}
                  </ActionButton>
                  <ActionButton 
                    onClick={() => {}} 
                    variant="secondary"
                    icon={
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159-.026-1.563.434L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
                      </svg>
                    }
                  >
                    {t('changer_mot_de_passe')}
                  </ActionButton>
                  <ActionButton 
                    onClick={logout} 
                    variant="danger"
                    icon={
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                      </svg>
                    }
                  >
                    {t('deconnexion')}
                  </ActionButton>
                </div>
              </div>
            </div>
          </div>
        </div>)
        }
      </main>
    </div>
  )
}

/* Clean, Minimalist Components */
interface ProfileFieldProps {
  label: string
  value: string
  icon?: React.ReactNode
}

function ProfileField({ label, value, icon }: ProfileFieldProps) {
  return (
    <div className="group">
      <label className="flex items-center gap-2 text-sm font-medium text-gray-500 mb-2">
        {icon}
        {label}
      </label>
      <div className="bg-gray-50 rounded-lg px-4 py-3 group-hover:bg-gray-100 transition-colors">
        <p className="text-base font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  )
}

interface StatCardProps {
  value: string | number
  label: string
  icon?: React.ReactNode
}

function StatCard({ value, label, icon }: StatCardProps) {
  return (
    <div className="p-4 rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100 transition-colors">
      <div className="flex items-center justify-between mb-2">
        {/* FIXED: Font size is now responsive */}
        <div className="text-xl sm:text-2xl font-bold text-gray-900">{value}</div>
        {icon && <div className="opacity-60">{icon}</div>}
      </div>
      <div className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</div>
    </div>
  )
}

interface ActionButtonProps {
  onClick: () => void
  variant: 'primary' | 'secondary' | 'danger'
  icon?: React.ReactNode
  children: React.ReactNode
}

function ActionButton({ onClick, variant, icon, children }: ActionButtonProps) {
  const variantClasses = {
    primary: 'bg-gray-900 hover:bg-gray-800 text-white',
    secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-200',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
  }

  return (
    <button 
      onClick={onClick}
      // FIXED: Added responsive font size for buttons
      className={`w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg font-medium text-sm sm:text-base transition-colors ${variantClasses[variant]}`}
    >
      {icon}
      {children}
    </button>
  )
}