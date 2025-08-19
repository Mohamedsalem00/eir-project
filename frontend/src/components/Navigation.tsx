'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useLanguage } from '@/contexts/LanguageContext'
import { useTranslation } from '@/hooks/useTranslation'
import { useAuth } from '@/contexts/AuthContext'
import LanguageSelector from '@/components/LanguageSelector'

// A reusable confirmation modal component
function ConfirmationModal({ t, isOpen, onClose, onConfirm, title, children }: { t: (key: string) => string, isOpen: boolean, onClose: () => void, onConfirm: () => void, title: string, children: React.ReactNode }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" aria-modal="true" role="dialog">
      <div className="bg-white rounded-xl shadow-2xl p-8 max-w-sm w-full text-center m-4">
        <h2 className="text-xl font-bold text-gray-900 mb-4">{title}</h2>
        <p className="text-gray-600 mb-8">{children}</p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-100 text-gray-800 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            {t('annuler')}
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            {t('se_deconnecter')}
          </button>
        </div>
      </div>
    </div>
  );
}


// Define a type for the user object for better type safety
interface User {
  id: string
  nom: string
  email: string
  type_utilisateur: string
}

export default function Navigation() {
  const { t, currentLang, setCurrentLang } = useLanguage()
  const { user, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false)

  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'auto'
    }
    return () => {
      document.body.style.overflow = 'auto'
    }
  }, [mobileMenuOpen])

  const closeMobileMenu = () => setMobileMenuOpen(false)

  const handleLogoutClick = () => {
    setShowLogoutConfirm(true); // Show confirmation modal instead of logging out directly
  }

  const confirmLogout = () => {
    logout()
    setShowLogoutConfirm(false)
    closeMobileMenu()
  }

  // Determine user type and access level
  const isPersonalUser = user && user.type_utilisateur === 'utilisateur_authentifie' && user.niveau_acces === 'standard'
  const isOperator = user && user.type_utilisateur === 'operateur'
  const isAdmin = user && user.type_utilisateur === 'administrateur'

  // Navigation links based on user type
  let navLinks = [
    { href: '/', label: t('accueil') },
    { href: '#what-is-imei', label: t('quest_ce_que_imei') },
  ]

  if (user) {
    if (isPersonalUser) {
      navLinks = [
        { href: '/', label: t('accueil') },
        { href: '/my-devices', label: t('mes_appareils') },
        { href: '/search-history', label: t('historique_recherches') },
      ]
    } else if (isOperator) {
      navLinks.push({ href: '/dashboard', label: t('tableau_bord') })
      navLinks.push({ href: '/organisation', label: t('organisation') })
    } else if (isAdmin) {
      navLinks.push({ href: '/dashboard', label: t('tableau_bord') })
      navLinks.push({ href: '/admin', label: t('admin_panel') })
    }
  }

  return (
    <>
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Brand */}
            <div className="flex items-center space-x-3">
              <Link href="/" className="flex items-center space-x-3" onClick={closeMobileMenu}>
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-md">
                    <span className="text-white font-bold text-lg">EIR</span>
                  </div>
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-xl font-semibold text-gray-900">
                    {t('titre')}
                  </h1>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-6">
              <nav className="flex items-center space-x-8 text-sm font-medium">
                {navLinks.map((link) => (
                  <Link key={link.href} href={link.href} className="text-gray-600 p-4 hover:text-blue-600 transition-colors duration-200">
                    {link.label}
                  </Link>
                ))}
              </nav>

              <div className="flex items-center space-x-4">
                {/* Language Selector (desktop) */}
                <LanguageSelector />

                <div className="h-6 w-px bg-gray-200"></div>

                {/* Auth Buttons & User Links */}
                {user ? (
                  <div className="flex items-center space-x-5">
                    <Link href="/profile" className="text-gray-600 hover:text-blue-600 p-4 transition-colors duration-200 text-sm font-medium">
                      {t('profil')}
                    </Link>
                    <Link href="#" onClick={handleLogoutClick} className="text-gray-600 p-4  hover:text-blue-600 transition-colors duration-200 text-sm font-medium">
                      {t('deconnexion')}
                    </Link>
              
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Link href="/login" className="px-4 py-2 text-sm font-medium text-gray-600 p-4 hover:text-blue-600 transition-colors duration-200">
                      {t('connexion')}
                    </Link>
                    <Link href="/register" className="px-4 py-2 text-sm font-medium bg-blue-600 p-4 text-white rounded-lg hover:bg-blue-700 shadow-sm hover:shadow-md transition-all duration-200">
                      {t('inscription')}
                    </Link>
                  </div>
                )}
              </div>
            </div>

            {/* Mobile Menu Button */}
            <div className="lg:hidden">
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="p-2 rounded-lg text-gray-600 hover:text-blue-600 hover:bg-gray-100 transition-colors"
                aria-label="Open menu"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Panel */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-50" role="dialog" aria-modal="true">
          <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" onClick={closeMobileMenu} />
          <div className="fixed top-0 right-0 bottom-0 w-full max-w-xs bg-white shadow-xl animate-slide-in">
            <div className="p-6 flex flex-col h-full">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-lg font-semibold text-gray-900">{t('titre')}</h2>
                <button
                  onClick={closeMobileMenu}
                  className="p-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors"
                  aria-label="Close menu"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <nav className="flex flex-col space-y-2">
                {navLinks.map((link) => (
                  <Link key={link.href} href={link.href} onClick={closeMobileMenu} className="px-4 py-3 rounded-lg text-gray-700 hover:text-blue-600 hover:bg-gray-50 font-medium transition-colors">
                    {link.label}
                  </Link>
                ))}
              </nav>

              <div className="mt-auto">
                <div className="pt-6 border-t border-gray-200">
                  {user ? (
                    <div className="space-y-2">
                      <Link href="/profile" onClick={closeMobileMenu} className="block px-4 py-3 rounded-lg text-gray-700 hover:text-blue-600 hover:bg-gray-50 font-medium transition-colors">
                        {t('profil')}
                      </Link>
                      <Link href="#"  onClick={() => { handleLogoutClick(); closeMobileMenu(); }} className="block px-4 py-3 rounded-lg text-gray-700 hover:text-blue-600 hover:bg-gray-50 font-medium transition-colors">
                        {t('deconnexion')}
                      </Link>
                        


                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Link href="/login" onClick={closeMobileMenu} className="block w-full text-center px-4 py-3 rounded-lg text-gray-700 bg-gray-100 hover:bg-gray-200 font-medium transition-colors">
                        {t('connexion')}
                      </Link>
                      <Link href="/register" onClick={closeMobileMenu} className="block w-full text-center px-4 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 font-medium transition-colors shadow-sm">
                        {t('inscription')}
                      </Link>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="flex justify-center">
                    {/* Language Selector (mobile) */}
                    <LanguageSelector />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <ConfirmationModal
        t={t}
        isOpen={showLogoutConfirm}
        onClose={() => setShowLogoutConfirm(false)}
        onConfirm={confirmLogout}
        title={t('confirmation_deconnexion')}
      >
        {t('confirmation_deconnexion_message')}
      </ConfirmationModal>

      <style jsx global>{`
        @keyframes slide-in {
          from { transform: translateX(100%); }
          to { transform: translateX(0); }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-in-out;
        }
      `}</style>
    </>
  )
}
