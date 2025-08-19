'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslation } from '@/hooks/useTranslation'
import { useAuth } from '@/contexts/AuthContext'

export default function Unauthorized401({ supportEmail = "support@eir.com" }: { supportEmail?: string }) {
  const { t } = useTranslation()
  const router = useRouter()
  const { logout } = useAuth()

  // This effect ensures the user's session is cleared when they land on this page.
  useEffect(() => {
    logout()
  }, [logout])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 to-red-50 p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-gray-200 p-8 text-center">
        
        {/* Icon */}
        <div className="mx-auto h-20 w-20 bg-red-100 rounded-full flex items-center justify-center border-4 border-white shadow-md mb-6">
          <svg className="h-10 w-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>

        {/* Heading and Message */}
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('session_expiree_titre') || 'Session Expired'}</h1>
        <p className="text-gray-600 mb-8">{t('session_expiree_description') || 'Your session has expired or is invalid. Please log in again to continue.'}</p>

        {/* Call to Action Button */}
        <button
          onClick={() => router.push('/login')}
          className="w-full px-6 py-3 bg-red-600 text-white rounded-lg font-semibold text-lg hover:bg-red-700 transition-all duration-200 shadow-md hover:shadow-lg transform hover:-translate-y-1"
        >
          {t('reconnecter') || 'Return to Login'}
        </button>

        {/* Support Link */}
        <p className="mt-6 text-sm text-gray-500">
          {t('besoin_aide') || 'Need help?'} <a href={`mailto:${supportEmail}`} className="font-medium underline text-red-600 hover:text-red-800">{t('contacter_support') || 'Contact Support'}</a>
        </p>
      </div>
    </div>
  )
}