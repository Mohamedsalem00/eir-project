'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useLanguage } from '@/contexts/LanguageContext'
import { useAuth } from '@/contexts/AuthContext'
import LanguageSelector from '@/components/LanguageSelector'
import { ThemeSwitcher } from './ui/ThemeSwitcher'
import { ConfirmationModal } from './ui/ConfirmationModal' // 1. Import the new component

export default function Navigation() {
  const { t } = useLanguage()
  const { user, logout } = useAuth()
  const pathname = usePathname()
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
    setShowLogoutConfirm(true);
  }

  const confirmLogout = () => {
    logout()
    setShowLogoutConfirm(false)
    closeMobileMenu()
  }

  const isPersonalUser = user?.type_utilisateur === 'utilisateur_authentifie'
  const isOperator = user?.type_utilisateur === 'operateur'
  const isAdmin = user?.type_utilisateur === 'administrateur'

  const baseLinks = [
    { href: '/', label: t('accueil') },
  ]

  const userLinks = isPersonalUser ? [
    { href: '/my-devices', label: t('mes_appareils') },
    { href: '/search-history', label: t('historique_recherches') },
  ] : []

  const operatorLinks = isOperator ? [
    { href: '/dashboard', label: t('tableau_bord') },
    { href: '/organisation', label: t('organisation') },
  ] : []

  const adminLinks = isAdmin ? [
    { href: '/dashboard', label: t('tableau_bord') },
    { href: '/admin', label: t('admin_panel') },
  ] : []

  const navLinks = user ? [...baseLinks, ...userLinks, ...operatorLinks, ...adminLinks] : [
    ...baseLinks,
    { href: '#what-is-imei', label: t('quest_ce_que_imei') }
  ]

  const profileLinks = [
      { href: '/profile', label: t('profil') },
  ]

  return (
    <>
      <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 sticky top-0 z-40 shadow-sm">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Link href="/" className="flex items-center space-x-3" onClick={closeMobileMenu}>
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-md">
                    <span className="text-white font-bold text-lg">EIR</span>
                  </div>
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                    {t('titre')}
                  </h1>
                </div>
              </Link>
            </div>

            <div className="hidden lg:flex items-center space-x-6">
              <nav className="flex items-center space-x-1 text-sm font-medium">
                {navLinks.map((link) => {
                  const isActive = pathname === link.href;
                  return (
                    <Link key={link.href} href={link.href} className={`px-4 py-2 rounded-md transition-colors duration-200 ${
                        isActive 
                        ? 'text-blue-600 bg-blue-50 dark:text-blue-300 dark:bg-blue-900/50' 
                        : 'text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}>
                      {link.label}
                    </Link>
                  )
                })}
              </nav>

              <div className="flex items-center space-x-4">
                <ThemeSwitcher />
                <LanguageSelector />

                <div className="h-6 w-px bg-gray-200 dark:bg-gray-700"></div>

                {user ? (
                  <div className="flex items-center space-x-1">
                    {profileLinks.map(link => {
                        const isActive = pathname === link.href;
                        return (
                            <Link key={link.href} href={link.href} className={`px-4 py-2 rounded-md transition-colors duration-200 text-sm font-medium ${
                                isActive 
                                ? 'text-blue-600 bg-blue-50 dark:text-blue-300 dark:bg-blue-900/50' 
                                : 'text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                            }`}>
                            {link.label}
                            </Link>
                        )
                    })}
                    <button onClick={handleLogoutClick} className="px-4 py-2 rounded-md transition-colors duration-200 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-800">
                      {t('deconnexion')}
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Link href="/login" className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200">
                      {t('connexion')}
                    </Link>
                    <Link href="/register" className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-sm hover:shadow-md transition-all duration-200">
                      {t('inscription')}
                    </Link>
                  </div>
                )}
              </div>
            </div>

            <div className="lg:hidden">
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
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

      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-50" role="dialog" aria-modal="true">
          <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" onClick={closeMobileMenu} />
          <div className="fixed top-0 right-0 bottom-0 w-full max-w-xs bg-white dark:bg-gray-900 shadow-xl animate-slide-in">
            <div className="p-6 flex flex-col h-full">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('titre')}</h2>
                <button
                  onClick={closeMobileMenu}
                  className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  aria-label="Close menu"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <nav className="flex flex-col space-y-2">
                {navLinks.map((link) => {
                  const isActive = pathname === link.href;
                  return (
                    <Link key={link.href} href={link.href} onClick={closeMobileMenu} className={`px-4 py-3 rounded-lg font-medium transition-colors ${
                        isActive 
                        ? 'text-blue-600 bg-blue-50 dark:text-blue-300 dark:bg-blue-900/50' 
                        : 'text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}>
                      {link.label}
                    </Link>
                  )
                })}
              </nav>

              <div className="mt-auto">
                <div className="pt-6 border-t border-gray-200 dark:border-gray-800">
                  {user ? (
                    <div className="space-y-2">
                      {profileLinks.map(link => {
                        const isActive = pathname === link.href;
                        return (
                            <Link key={link.href} href={link.href} onClick={closeMobileMenu} className={`block px-4 py-3 rounded-lg font-medium transition-colors ${
                                isActive 
                                ? 'text-blue-600 bg-blue-50 dark:text-blue-300 dark:bg-blue-900/50' 
                                : 'text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                            }`}>
                            {link.label}
                            </Link>
                        )
                      })}
                      <button onClick={() => { handleLogoutClick(); closeMobileMenu(); }} className="block w-full text-left px-4 py-3 rounded-lg text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800 font-medium transition-colors">
                        {t('deconnexion')}
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Link href="/login" onClick={closeMobileMenu} className="block w-full text-center px-4 py-3 rounded-lg text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700 font-medium transition-colors">
                        {t('connexion')}
                      </Link>
                      <Link href="/register" onClick={closeMobileMenu} className="block w-full text-center px-4 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 font-medium transition-colors shadow-sm">
                        {t('inscription')}
                      </Link>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-800">
                  <div className="flex justify-center items-center space-x-4">
                    <ThemeSwitcher />
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
  variant="danger" 
  actionTextKey="se_deconnecter"
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
