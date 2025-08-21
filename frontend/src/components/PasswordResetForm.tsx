'use client'

import { useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { authService, PasswordResetRequest } from '../api/auth'
import Link from 'next/link'

export function PasswordResetForm() {
  const { t, currentLang } = useLanguage()
  const [step, setStep] = useState<'request' | 'verify' | 'new-password'>('request')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const [requestData, setRequestData] = useState({
    email: '',
    methode_verification: 'email' as 'email' | 'sms',
    telephone: ''
  })
  
  const [verifyData, setVerifyData] = useState({
    token: '',
    code_verification: ''
  })
  
  const [passwordData, setPasswordData] = useState({
    token: '',
    nouveau_mot_de_passe: '',
    confirmer_mot_de_passe: ''
  })
  
  const [resetToken, setResetToken] = useState<string>('')

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setSuccess(null)
    
    try {
      const data: PasswordResetRequest = {
        email: requestData.email,
        methode_verification: requestData.methode_verification,
        telephone: requestData.methode_verification === 'sms' ? requestData.telephone : undefined
      }
      
      const response = await authService.requestPasswordReset(data)
      
      if (response.success && response.token) {
        setResetToken(response.token)
        setSuccess(response.message)
        setStep('verify')
      } else {
        setError(response.message || 'Reset request failed')
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await authService.verifyResetCode({
        token: resetToken,
        code_verification: verifyData.code_verification
      })
      
      if (response.success) {
        setSuccess(response.message)
        setStep('new-password')
      } else {
        setError(response.message || 'Code verification failed')
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSetNewPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    
    if (passwordData.nouveau_mot_de_passe !== passwordData.confirmer_mot_de_passe) {
      setError('Passwords do not match')
      setIsLoading(false)
      return
    }
    
    try {
      const response = await authService.setNewPassword({
        token: resetToken,
        nouveau_mot_de_passe: passwordData.nouveau_mot_de_passe,
        confirmer_mot_de_passe: passwordData.confirmer_mot_de_passe
      })
      
      if (response.success) {
        setSuccess('Password changed successfully! You can now login.')
        setTimeout(() => {
            // Optionally redirect to login after a delay
            window.location.href = '/login';
        }, 3000);
      } else {
        setError(response.message || 'Password change failed')
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const renderRequestStep = () => (
    <form onSubmit={handleRequestReset} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('adresse_email')}
        </label>
        <input
          id="email"
          type="email"
          required
          value={requestData.email}
          onChange={(e) => setRequestData(prev => ({ ...prev, email: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700/50 text-gray-900 dark:text-gray-100"
          placeholder={t('entrer_email')}
        />
      </div>
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 font-semibold"
      >
        {isLoading ? t('envoi_en_cours') : t('envoyer_code_verification')}
      </button>
    </form>
  )

  const renderVerifyStep = () => (
    <form onSubmit={handleVerifyCode} className="space-y-4">
      <div>
        <label htmlFor="code" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('code_verification')}
        </label>
        <input
          id="code"
          type="text"
          required
          value={verifyData.code_verification}
          onChange={(e) => setVerifyData(prev => ({ ...prev, code_verification: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700/50 text-gray-900 dark:text-gray-100"
          placeholder={t('entrer_code_verification')}
        />
      </div>
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 font-semibold"
      >
        {isLoading ? t('verification_en_cours') : t('verifier_code')}
      </button>
    </form>
  )

  const renderNewPasswordStep = () => (
    <form onSubmit={handleSetNewPassword} className="space-y-4">
      <div>
        <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('nouveau_mot_de_passe')}
        </label>
        <input
          id="newPassword"
          type="password"
          required
          minLength={8}
          value={passwordData.nouveau_mot_de_passe}
          onChange={(e) => setPasswordData(prev => ({ ...prev, nouveau_mot_de_passe: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700/50 text-gray-900 dark:text-gray-100"
          placeholder={t('entrer_nouveau_mot_de_passe')}
        />
      </div>
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('confirmer_mot_de_passe')}
        </label>
        <input
          id="confirmPassword"
          type="password"
          required
          value={passwordData.confirmer_mot_de_passe}
          onChange={(e) => setPasswordData(prev => ({ ...prev, confirmer_mot_de_passe: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700/50 text-gray-900 dark:text-gray-100"
          placeholder={t('confirmer_nouveau_mot_de_passe')}
        />
      </div>
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-4 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 font-semibold"
      >
        {isLoading ? t('changement_en_cours') : t('changer_mot_de_passe')}
      </button>
    </form>
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Link href="/" className="inline-block">
            <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
            </div>
          </Link>
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-gray-100">
            {t('reinitialisation_mot_de_passe')}
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {t('ou')}{' '}
            <Link 
              href="/login" 
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
            >
              {t('retour_connexion')}
            </Link>
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow-2xl rounded-2xl p-8 space-y-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-center space-x-4">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                step === 'request' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
              }`}>1</div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                step === 'verify' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
              }`}>2</div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                step === 'new-password' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
              }`}>3</div>
            </div>

            {error && (
                <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4 text-sm text-red-700 dark:text-red-400">
                    {error}
                </div>
            )}
            {success && (
                <div className="rounded-md bg-green-50 dark:bg-green-900/20 p-4 text-sm text-green-700 dark:text-green-300">
                    {success}
                </div>
            )}

            {step === 'request' && renderRequestStep()}
            {step === 'verify' && renderVerifyStep()}
            {step === 'new-password' && renderNewPasswordStep()}
        </div>
      </div>
    </div>
  )
}
