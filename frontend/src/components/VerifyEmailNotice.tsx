'use client'

import { useState } from 'react'
import { useTranslation } from '@/hooks/useTranslation'
import { emailVerifyService } from '@/api/emailVerifyService'
import Link from 'next/link'

interface VerifyEmailNoticeProps {
  email: string
}

export function VerifyEmailNotice({ email }: VerifyEmailNoticeProps) {
  const { t } = useTranslation()
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleResend = async () => {
    setIsLoading(true)
    setMessage(null)
    setError(null)
    try {
      const response = await emailVerifyService.resendVerificationEmail(email)
      setMessage(response.message || t('email_verification_renvoye'))
    } catch (err: any) {
      setError(err.message || t('erreur_renvoi_email'))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30 dark:from-gray-900 dark:to-blue-900/20 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6 sm:p-8 text-center">
        <div className="mx-auto h-20 w-20 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center border-4 border-white dark:border-gray-800 shadow-md mb-6">
          <svg className="h-10 w-10 text-blue-500 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">{t('verifier_email_titre')}</h1>
        <p className="text-base text-gray-600 dark:text-gray-300 mb-6">
          {t('verifier_email_description', { email: email })}
        </p>
        
        {message && <p className="text-green-600 dark:text-green-400 text-sm mb-4">{message}</p>}
        {error && <p className="text-red-600 dark:text-red-400 text-sm mb-4">{error}</p>}

        <button
          onClick={handleResend}
          disabled={isLoading}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold text-base sm:text-lg hover:bg-blue-700 transition-all duration-200 shadow-md hover:shadow-lg transform hover:-translate-y-1 disabled:opacity-50"
        >
          {isLoading ? t('envoi_en_cours') : t('renvoyer_email')}
        </button>

        <p className="mt-6 text-sm text-gray-500 dark:text-gray-400">
          <Link href="/login" className="font-medium underline text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
            {t('retour_connexion')}
          </Link>
        </p>
      </div>
    </div>
  )
}
