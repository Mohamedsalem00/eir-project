// components/SearchLimitPopup.tsx

import React from 'react'
import Link from 'next/link'

// This object holds all translations.
const messages = {
  fr: {
    title: 'Limite de recherches atteinte',
    description: 'Vous avez atteint la limite de recherches pour les visiteurs. Créez un compte pour débloquer plus de fonctionnalités et de recherches illimitées.',
    register: 'Créer un compte',
    login: 'Se connecter',
    close: 'Fermer'
  },
  en: {
    title: 'Search limit reached',
    description: 'You have reached the search limit for visitors. Register to unlock more features and unlimited searches.',
    register: 'Register',
    login: 'Login',
    close: 'Close'
  },
  ar: {
    title: 'تم بلوغ حد البحث',
    description: 'لقد وصلت إلى حد البحث للزوار. أنشئ حسابًا للحصول على ميزات أكثر وبحث غير محدود.',
    register: 'إنشاء حساب',
    login: 'تسجيل الدخول',
    close: 'إغلاق'
  }
}

// 1. (FIX) Create a type for the keys of the messages object.
// This ensures that only 'fr', 'en', or 'ar' can be passed as the language prop.
type Language = keyof typeof messages;

interface SearchLimitPopupProps {
  open: boolean
  onClose: () => void // Make onClose required, as a popup should always be closable.
  language?: Language // 2. (FIX) Use the new 'Language' type here.
}

export default function SearchLimitPopup({ open, onClose, language = 'fr' }: SearchLimitPopupProps) {
  // This is a "guard clause". If the popup shouldn't be open, render nothing. Perfect.
  if (!open) return null
  
  // Now this line is completely type-safe.
  const t = messages[language]

  return (
    // 3. (IMPROVEMENT) Added accessibility attributes for a modal dialog.
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
      role="dialog"
      aria-modal="true"
      aria-labelledby="search-limit-title" // Points to the h2 title
    >
      <div className="bg-white rounded-xl shadow-2xl p-8 max-w-sm w-full text-center relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-2xl leading-none"
          aria-label={t.close}
        >
          &times; {/* A more standard HTML entity for the 'x' button */}
        </button>
        <div className="mb-4">
          <span className="text-3xl" role="img" aria-label="lock icon">🔒</span>
        </div>
        <h2 
          id="search-limit-title" // The ID for aria-labelledby
          className="text-xl font-bold text-red-700 mb-2"
        >
          {t.title}
        </h2>
        <p className="text-gray-700 mb-6">{t.description}</p>
        <div className="flex gap-3 justify-center">
          <Link href="/register" className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">
            {t.register}
          </Link>
          <Link href="/login" className="px-4 py-2 bg-gray-100 text-blue-700 rounded-lg font-medium hover:bg-gray-200">
            {t.login}
          </Link>
        </div>
      </div>
    </div>
  )
}