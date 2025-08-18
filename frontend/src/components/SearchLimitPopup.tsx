'use client'

import React from 'react'
import Link from 'next/link'

interface SearchLimitPopupProps {
  t: (key: string) => string
  currentLang: string
  open: boolean
  onClose: () => void
}

export default function SearchLimitPopup({ t , currentLang, open, onClose }: SearchLimitPopupProps) {


  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
      role="dialog"
      aria-modal="true"
      aria-labelledby="search-limit-title"
    >
      <div className="bg-white rounded-xl shadow-2xl p-8 max-w-sm w-full text-center relative m-4">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-2xl leading-none"
          aria-label={t('fermer')}
        >
          &times;
        </button>
        <div className="mb-4">
          <span className="text-3xl" role="img" aria-label="lock icon">🔒</span>
        </div>
        <h2
          id="search-limit-title"
          className="text-xl font-bold text-red-700 mb-2"
        >
          {t('limite_recherches_atteinte_titre')}
        </h2>
        <p className="text-gray-700 mb-6">{t('limite_recherches_atteinte_description')}</p>
        <div className="flex gap-3 justify-center">
          <Link href="/register" className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">
            {t('inscription')}
          </Link>
          <Link href="/login" className="px-4 py-2 bg-gray-100 text-blue-700 rounded-lg font-medium hover:bg-gray-200">
            {t('connexion')}
          </Link>
        </div>
      </div>
    </div>
  )
}
