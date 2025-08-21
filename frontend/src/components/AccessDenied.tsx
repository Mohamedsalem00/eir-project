'use client'

import React from 'react'
import Link from 'next/link'
import { useTranslation } from '@/hooks/useTranslation'

interface AccessDeniedProps {
  supportEmail?: string
}

export default function AccessDenied({ supportEmail }: AccessDeniedProps) {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 via-red-50/30 to-red-100/20 dark:from-gray-900 dark:via-red-900/20 dark:to-red-900/10 px-4">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
        <div className="mx-auto h-16 w-16 bg-red-100 dark:bg-red-900/50 rounded-full flex items-center justify-center mb-6">
          <svg className="h-8 w-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-12.728 12.728M5.636 5.636l12.728 12.728" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">{t('acces_refuse')}</h2>
        <p className="text-gray-700 dark:text-gray-300 mb-6">
          {t('acces_refuse_description')}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
          {t('contact_support', { email: supportEmail })}
        </p>
        <div className="flex justify-center">
          <Link href="/" className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            {t('retour_accueil')}
          </Link>
        </div>
      </div>
    </div>
  )
}
