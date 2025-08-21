'use client'

import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useLanguage } from '../contexts/LanguageContext'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { authService } from '../api/auth'
import { VerifyEmailNotice } from './VerifyEmailNotice'

export function RegisterForm() {
  const { register, isLoading, error } = useAuth()
  const { t, currentLang } = useLanguage()
  const router = useRouter()
  
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    mot_de_passe: '',
    confirmer_mot_de_passe: '',
    type_utilisateur: 'utilisateur_authentifie',
    numero_telephone: ''
  })
  const [showVerifyNotice, setShowVerifyNotice] = useState(false)
  const [registeredEmail, setRegisteredEmail] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({})

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (validationErrors[name]) {
      setValidationErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validateForm = () => {
    const errors: {[key: string]: string} = {}
    
    if (!formData.nom.trim()) {
      errors.nom = t('nom_requis')
    } else if (formData.nom.trim().length < 2) {
      errors.nom = t('nom_trop_court')
    }
    
    if (!formData.email) {
      errors.email = t('email_requis')
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = t('email_invalide')
    }
    
    if (!formData.mot_de_passe) {
      errors.mot_de_passe = t('mot_de_passe_requis')
    } else if (formData.mot_de_passe.length < 8) {
      errors.mot_de_passe = t('mot_de_passe_trop_court')
    }
    
    if (!formData.confirmer_mot_de_passe) {
      errors.confirmer_mot_de_passe = t('confirmation_requise')
    } else if (formData.mot_de_passe !== formData.confirmer_mot_de_passe) {
      errors.confirmer_mot_de_passe = t('mots_de_passe_non_identiques')
    }
    
    if (formData.numero_telephone && !/^\+?[0-9]{7,15}$/.test(formData.numero_telephone)) {
      errors.numero_telephone = t('numero_telephone_invalide')
    }
    
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    const { confirmer_mot_de_passe, ...registerData } = formData
    const success = await register(registerData)
    if (success) {
      setRegisteredEmail(formData.email)
      setShowVerifyNotice(true)
    }
  }

  if (showVerifyNotice && registeredEmail) {
    return <VerifyEmailNotice email={registeredEmail} />
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Link href="/" className="inline-block">
            <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">EIR</span>
            </div>
          </Link>
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-gray-100">
            {t('creer_compte')}
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {t('ou')}{' '}
            <Link 
              href="/login" 
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
            >
              {t('se_connecter')}
            </Link>
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow-2xl rounded-2xl p-8 space-y-6 border border-gray-200 dark:border-gray-700">
          <form className="space-y-4" onSubmit={handleSubmit}>
            {/* Form fields here */}
          <div className="space-y-4">
            <div>
              <label htmlFor="nom" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('nom_complet')}
              </label>
              <input
                id="nom"
                name="nom"
                type="text"
                autoComplete="name"
                required
                value={formData.nom}
                onChange={handleInputChange}
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  validationErrors.nom ? 'border-red-300 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                placeholder={t('entrer_nom')}
                dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
              />
              {validationErrors.nom && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.nom}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('adresse_email')}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  validationErrors.email ? 'border-red-300 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                placeholder={t('entrer_email')}
                dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
              />
              {validationErrors.email && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.email}</p>
              )}
            </div>

            <div>
              <label htmlFor="numero_telephone" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('numero_telephone')}
              </label>
              <input
                id="numero_telephone"
                name="numero_telephone"
                type="text"
                value={formData.numero_telephone}
                onChange={handleInputChange}
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  validationErrors.numero_telephone ? 'border-red-300 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                placeholder={t('entrer_numero_telephone')}
                dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
              />
              {validationErrors.numero_telephone && (
                <span className="text-xs text-red-600 dark:text-red-400">{validationErrors.numero_telephone}</span>
              )}
            </div>

            <div>
              <label htmlFor="type_utilisateur" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('type_utilisateur')}
              </label>
              <select
                id="type_utilisateur"
                name="type_utilisateur"
                value={formData.type_utilisateur}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="utilisateur_authentifie">{t('utilisateur_authentifie')}</option>
                {/* <option value="operateur">{t('operateur')}</option> */}
              </select>
            </div>

            <div>
              <label htmlFor="mot_de_passe" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('mot_de_passe')}
              </label>
              <input
                id="mot_de_passe"
                name="mot_de_passe"
                type="password"
                autoComplete="new-password"
                required
                value={formData.mot_de_passe}
                onChange={handleInputChange}
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  validationErrors.mot_de_passe ? 'border-red-300 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                placeholder={t('entrer_mot_de_passe')}
                dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
              />
              {validationErrors.mot_de_passe && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.mot_de_passe}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmer_mot_de_passe" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('confirmer_mot_de_passe')}
              </label>
              <input
                id="confirmer_mot_de_passe"
                name="confirmer_mot_de_passe"
                type="password"
                autoComplete="new-password"
                required
                value={formData.confirmer_mot_de_passe}
                onChange={handleInputChange}
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  validationErrors.confirmer_mot_de_passe ? 'border-red-300 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm`}
                placeholder={t('confirmer_mot_de_passe')}
                dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
              />
              {validationErrors.confirmer_mot_de_passe && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.confirmer_mot_de_passe}</p>
              )}
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {t('creation_en_cours')}
                </div>
              ) : (
                t('creer_compte')
              )}
            </button>
          </div>
          </form>
        </div>
      </div>
    </div>
  )
}
