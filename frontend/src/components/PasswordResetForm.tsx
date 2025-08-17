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
  
  // Request step
  const [requestData, setRequestData] = useState({
    email: '',
    methode_verification: 'EMAIL' as 'EMAIL' | 'SMS',
    telephone: ''
  })
  
  // Verify step
  const [verifyData, setVerifyData] = useState({
    token: '',
    code_verification: ''
  })
  
  // New password step
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
    
    try {
      const data: PasswordResetRequest = {
        email: requestData.email,
        methode_verification: requestData.methode_verification,
        telephone: requestData.methode_verification === 'SMS' ? requestData.telephone : undefined
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
        setSuccess('Password changed successfully! You can now login with your new password.')
        // Reset form
        setStep('request')
        setRequestData({ email: '', methode_verification: 'EMAIL', telephone: '' })
        setVerifyData({ token: '', code_verification: '' })
        setPasswordData({ token: '', nouveau_mot_de_passe: '', confirmer_mot_de_passe: '' })
        setResetToken('')
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
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          {t('adresse_email')}
        </label>
        <input
          id="email"
          type="email"
          required
          value={requestData.email}
          onChange={(e) => setRequestData(prev => ({ ...prev, email: e.target.value }))}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder={t('entrer_email')}
          dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
        />
      </div>
      
      <div>
        <label htmlFor="methode" className="block text-sm font-medium text-gray-700">
          {t('methode_verification')}
        </label>
        <select
          id="methode"
          value={requestData.methode_verification}
          onChange={(e) => setRequestData(prev => ({ 
            ...prev, 
            methode_verification: e.target.value as 'EMAIL' | 'SMS' 
          }))}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="EMAIL">{t('email')}</option>
          <option value="SMS">{t('sms')}</option>
        </select>
      </div>
      
      {requestData.methode_verification === 'SMS' && (
        <div>
          <label htmlFor="telephone" className="block text-sm font-medium text-gray-700">
            {t('numero_telephone')}
          </label>
          <input
            id="telephone"
            type="tel"
            required
            value={requestData.telephone}
            onChange={(e) => setRequestData(prev => ({ ...prev, telephone: e.target.value }))}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder={t('entrer_telephone')}
            dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
          />
        </div>
      )}
      
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isLoading ? t('envoi_en_cours') : t('envoyer_code_verification')}
      </button>
    </form>
  )

  const renderVerifyStep = () => (
    <form onSubmit={handleVerifyCode} className="space-y-4">
      <div>
        <label htmlFor="code" className="block text-sm font-medium text-gray-700">
          {t('code_verification')}
        </label>
        <input
          id="code"
          type="text"
          required
          value={verifyData.code_verification}
          onChange={(e) => setVerifyData(prev => ({ ...prev, code_verification: e.target.value }))}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder={t('entrer_code_verification')}
          dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
        />
        <p className="mt-1 text-sm text-gray-500">
          {t('code_envoye_par')} {requestData.methode_verification === 'SMS' ? t('sms') : t('email')}
        </p>
      </div>
      
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isLoading ? t('verification_en_cours') : t('verifier_code')}
      </button>
    </form>
  )

  const renderNewPasswordStep = () => (
    <form onSubmit={handleSetNewPassword} className="space-y-4">
      <div>
        <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700">
          {t('nouveau_mot_de_passe')}
        </label>
        <input
          id="newPassword"
          type="password"
          required
          minLength={8}
          value={passwordData.nouveau_mot_de_passe}
          onChange={(e) => setPasswordData(prev => ({ ...prev, nouveau_mot_de_passe: e.target.value }))}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder={t('entrer_nouveau_mot_de_passe')}
          dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
        />
      </div>
      
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
          {t('confirmer_mot_de_passe')}
        </label>
        <input
          id="confirmPassword"
          type="password"
          required
          value={passwordData.confirmer_mot_de_passe}
          onChange={(e) => setPasswordData(prev => ({ ...prev, confirmer_mot_de_passe: e.target.value }))}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder={t('confirmer_nouveau_mot_de_passe')}
          dir={currentLang === 'ar' ? 'rtl' : 'ltr'}
        />
      </div>
      
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
      >
        {isLoading ? t('changement_en_cours') : t('changer_mot_de_passe')}
      </button>
    </form>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/20 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            {t('reinitialisation_mot_de_passe')}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {t('ou')}{' '}
            <Link 
              href="/login" 
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              {t('retour_connexion')}
            </Link>
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center space-x-4">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            step === 'request' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
          }`}>
            1
          </div>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            step === 'verify' ? 'bg-blue-600 text-white' : step === 'new-password' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-600'
          }`}>
            2
          </div>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            step === 'new-password' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-600'
          }`}>
            3
          </div>
        </div>

        {/* Error Messages */}
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Success Messages */}
        {success && (
          <div className="rounded-md bg-green-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-700">{success}</p>
              </div>
            </div>
          </div>
        )}

        {/* Form Steps */}
        {step === 'request' && renderRequestStep()}
        {step === 'verify' && renderVerifyStep()}
        {step === 'new-password' && renderNewPasswordStep()}
      </div>
    </div>
  )
} 