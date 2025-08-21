'use client'

import { useEffect, useState, useRef, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { emailVerifyService } from '@/api/emailVerifyService'
import { useTranslation } from '@/hooks/useTranslation'

function VerificationComponent() {
  const { t } = useTranslation()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')
  
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [message, setMessage] = useState<string>('')
  const hasVerifiedRef = useRef<string | null>(null)

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage(t('token_manquant'))
      return
    }
    if (hasVerifiedRef.current === token) return;
    hasVerifiedRef.current = token;

    const verifyToken = async () => {
      try {
        const response = await emailVerifyService.verifyEmail(token)
        setStatus('success')
        setMessage(response.message || t('email_verifie_succes'))
      } catch (err: any) {
        setStatus('error')
        setMessage(err.message || t('erreur_verification_email'))
      }
    }

    verifyToken()
  }, [token, t])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30 dark:from-gray-900 dark:to-blue-900/20 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6 sm:p-8 text-center">
        {status === 'verifying' && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-b-2 border-blue-600 mx-auto mb-6"></div>
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">{t('verification_en_cours')}</h1>
          </>
        )}
        {status === 'success' && (
          <>
            <div className="mx-auto h-16 w-16 sm:h-20 sm:w-20 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center mb-6">
              <svg className="h-8 w-8 sm:h-10 sm:w-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-green-700 dark:text-green-400 mb-2">{t('verification_reussie')}</h1>
            <p className="text-base text-gray-600 dark:text-gray-300 mb-6">{message}</p>
            <Link href="/login" className="w-full inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold text-base sm:text-lg hover:bg-blue-700 transition-colors">
              {t('aller_a_connexion')}
            </Link>
          </>
        )}
        {status === 'error' && (
          <>
            <div className="mx-auto h-16 w-16 sm:h-20 sm:w-20 bg-red-100 dark:bg-red-900/50 rounded-full flex items-center justify-center mb-6">
              <svg className="h-8 w-8 sm:h-10 sm:w-10 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-red-700 dark:text-red-400 mb-2">{t('erreur_verification')}</h1>
            <p className="text-base text-gray-600 dark:text-gray-300 mb-6">{message}</p>
            <Link href="/" className="w-full inline-block px-6 py-3 bg-gray-600 text-white rounded-lg font-semibold text-base sm:text-lg hover:bg-gray-700 transition-colors">
              {t('retour_accueil')}
            </Link>
          </>
        )}
      </div>
    </div>
  )
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <VerificationComponent />
    </Suspense>
  )
}
