'use client'

import { useAuth } from '../../src/contexts/AuthContext'
import { useTranslation } from '@/hooks/useTranslation'
import Navigation from '@/components/Navigation'
import { useRouter } from 'next/navigation'
import { useEffect, useState, useCallback } from 'react'
import { DeviceService, DeviceItem } from '../../src/api'
import AccessDenied from '../../src/components/AccessDenied'
import Unauthorized401 from '../../src/components/Unauthorized401'
import { authService } from '../../src/api'

// Skeleton Loader Component for a better UX
function DeviceListSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden animate-pulse">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {[...Array(5)].map((_, i) => (
                <th key={i} className="px-6 py-4">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {[...Array(5)].map((_, i) => (
              <tr key={i}>
                <td className="px-6 py-4"><div className="h-5 bg-gray-300 rounded"></div></td>
                <td className="px-6 py-4"><div className="h-5 bg-gray-300 rounded"></div></td>
                <td className="px-6 py-4"><div className="h-5 bg-gray-300 rounded"></div></td>
                <td className="px-6 py-4"><div className="h-5 bg-gray-300 rounded"></div></td>
                <td className="px-6 py-4"><div className="h-5 bg-gray-300 rounded w-16"></div></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function MyDevicesPage() {
  const { user, isLoading: isAuthLoading } = useAuth()
  const token = user ? authService.getAuthToken() : undefined;
  const { t, currentLang } = useTranslation()
  const router = useRouter()

  const [devices, setDevices] = useState<DeviceItem[]>([])
  const [loadingDevices, setLoadingDevices] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isUnauthorized, setIsUnauthorized] = useState(false)

  const fetchDevices = useCallback(async () => {
    if (!token) {
      setLoadingDevices(false)
      return
    }

    setLoadingDevices(true)
    setError(null)
    
    const result = await DeviceService.getDevices(token, 0, 100, currentLang)
    
    if (result.success && result.data) {
      setDevices(result.data.devices)
    } else {
      // Detect 401 error and show Unauthorized401
      if (result.status === 401 || (result.error && result.error.toLowerCase().includes('401'))) {
        setIsUnauthorized(true)
        setError(null)
      } else {
        setError(result.error || t('erreur_inconnue'))
      }
    }
    
    setLoadingDevices(false)
  }, [token, currentLang, t])

  useEffect(() => {
    if (!isAuthLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchDevices()
    }
  }, [user, isAuthLoading, router, fetchDevices])

  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user || user.type_utilisateur !== 'utilisateur_authentifie') {
    return <AccessDenied supportEmail="support@eir.com" />
  }
  if (isUnauthorized) {
    return <Unauthorized401 supportEmail="support@eir.com" />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="container mx-auto px-4 sm:px-6 py-12">
        <div className="max-w-5xl mx-auto">
          <header className="mb-10 md:flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">{t('mes_appareils')}</h1>
              <p className="mt-2 text-lg text-gray-600">{t('mes_appareils_description')}</p>
            </div>
            <button 
              onClick={fetchDevices} 
              disabled={loadingDevices}
              className="mt-4 md:mt-0 flex items-center justify-center px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <svg className={`w-5 h-5 mr-2 ${loadingDevices ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {loadingDevices ? t('chargement') : t('actualiser')}
            </button>
          </header>

          {loadingDevices ? (
            <DeviceListSkeleton />
          ) : error ? (
            <div className="text-center text-red-700 bg-red-100 p-6 rounded-lg border border-red-200">
              <h3 className="font-semibold">{t('erreur')}</h3>
              <p>{error}</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">{t('marque')}</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">{t('modele')}</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">{t('numero_serie')}</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">{t('motif_acces')}</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {devices.length > 0 ? devices.map((device) => (
                      <tr key={device.id} className="hover:bg-gray-50 transition-colors duration-150">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">{device.marque}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{device.modele}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-mono">{device.numero_serie}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{t(device.motif_acces)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {device.can_modify ? (
                            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-xs font-medium transition-transform transform hover:scale-105 shadow-sm">
                              {t('modifier')}
                            </button>
                          ) : (
                            <span className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-xs font-medium border border-gray-200">
                              {t('lecture_seule')}
                            </span>
                          )}
                        </td>
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                          <div className="flex flex-col items-center">
                            <svg className="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            <p className="font-semibold">{t('aucun_appareil_trouve')}</p>
                            <p className="text-sm mt-1">{t('aucun_appareil_description')}</p>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
