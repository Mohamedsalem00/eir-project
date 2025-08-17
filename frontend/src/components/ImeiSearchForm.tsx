'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useLanguage } from '../contexts/LanguageContext'
import { useTranslation } from '@/hooks/useTranslation'
import { IMEIService, IMEIResponse, RateLimitInfo, authService } from '../api' // Import authService
import { ImeiSearchResults } from './ImeiSearchResults'

// A simple skeleton loader component for the results card
function ResultSkeleton() {
  return (
    <div className="max-w-4xl mx-auto mb-16">
        <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6 sm:p-8 animate-pulse">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 pb-6 border-b border-gray-200">
            <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
                <div>
                    <div className="h-7 bg-gray-200 rounded w-48 mb-2"></div>
                    <div className="h-6 bg-gray-300 rounded w-36"></div>
                </div>
            </div>
            <div className="mt-4 sm:mt-0 h-8 bg-gray-200 rounded-full w-24"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            <div className="p-4 bg-gray-50 rounded-lg space-y-2">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="h-6 bg-gray-300 rounded w-3/4"></div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg space-y-2">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="h-6 bg-gray-300 rounded w-3/4"></div>
            </div>
          </div>
        </div>
    </div>
  )
}


// Define a type for the validation result to ensure consistency
type ValidationState = {
  isValid: boolean;
  cleanImei?: string | null;
  error?: string | null;
}

export function ImeiSearchForm() {
  const { user } = useAuth() // Get user from the context
  const { currentLang } = useLanguage()
  const { t } = useTranslation()
  
  const [imei, setImei] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<IMEIResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [rateLimitInfo, setRateLimitInfo] = useState<RateLimitInfo | null>(null)
  const [searchLimitReached, setSearchLimitReached] = useState(false)
  const [validation, setValidation] = useState<ValidationState>({ 
    isValid: false, 
  })

  useEffect(() => {
    const validationResult = IMEIService.validateIMEI(imei)
    setValidation(validationResult)
  }, [imei])

  // This effect now only runs for visitors
  useEffect(() => {
    if (!user) {
      setSearchLimitReached(IMEIService.isSearchLimitReached())
      const interval = setInterval(() => {
        setSearchLimitReached(IMEIService.isSearchLimitReached())
      }, 60000)
      return () => clearInterval(interval)
    } else {
      // If a user is logged in, ensure the limit is turned off
      setSearchLimitReached(false)
    }
  }, [user])

  const handleImeiChange = (value: string) => {
    const cleanValue = value.replace(/\D/g, '').slice(0, 15)
    setImei(cleanValue)
    if (error) setError(null);
    if (result) setResult(null);
  }

  const searchIMEI = async () => {
    // For visitors, check the search limit. For users, this condition is always false.
    if (!user && searchLimitReached) {
      setError(t('limite_recherches_atteinte'))
      return
    }
    if (!validation.isValid || !validation.cleanImei) return

    setIsLoading(true)
    setError(null)
    setResult(null)
    setRateLimitInfo(null)

    // Get token from the authService if the user exists
    const authToken = user ? authService.getAuthToken() : undefined;

    // Pass the token to the service. It will be undefined for visitors.
    const response = await IMEIService.getIMEIDetails(validation.cleanImei, authToken, currentLang)

    // Only update search limit for visitors
    if (!user) {
      setSearchLimitReached(IMEIService.isSearchLimitReached())
    }

    if (response.success && response.data) {
      setResult(response.data)
    } else {
      setError(response.error || t('erreur_recherche'))
      if (response.rateLimitInfo) {
        setRateLimitInfo(response.rateLimitInfo)
      }
    }

    setIsLoading(false)
  }

  const resetSearch = () => {
    setImei('')
    setResult(null)
    setError(null)
    setIsLoading(false)
    setRateLimitInfo(null)
  }

  // The search button is disabled for visitors if the limit is reached
  const canSearch = validation.isValid && !isLoading && (!searchLimitReached || !!user)

  return (
    <>
      <section className="max-w-4xl mx-auto mb-12 sm:mb-16">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 sm:p-8">
          <div className="text-center mb-6">
            <div className="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-4">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
              </svg>
              {t('recherche_imei')}
            </div>
            <h2 className="text-2xl sm:text-3xl font-semibold text-gray-900 mb-3">{t('verification_imei')}</h2>
            <p className="text-base text-gray-600 max-w-2xl mx-auto">
              {t('invite_imei')}
            </p>
          </div>
          
          <div className="max-w-2xl mx-auto">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {t('libelle_imei')} <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={imei}
                    onChange={(e) => handleImeiChange(e.target.value)}
                    placeholder={t('entrer_imei')}
                    className={`w-full px-4 py-3 border rounded-lg text-lg font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                      validation.error && imei.length > 0
                        ? 'border-red-300 bg-red-50 text-red-900' 
                        : validation.isValid 
                          ? 'border-green-300 bg-green-50 text-green-900' 
                          : 'border-gray-300 bg-white hover:border-gray-400'
                    }`}
                    maxLength={15}
                    disabled={isLoading}
                    dir="ltr"
                  />
                  {imei.length > 0 && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      {validation.isValid ? (
                        <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      ) : (
                        <div className="w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div className="mt-2 flex items-center justify-between text-sm">
                  <span className="text-gray-500">{t('format_imei')}</span>
                  <span className={`font-medium ${imei.length === 15 ? 'text-green-600' : 'text-gray-400'}`}>
                    {imei.length}/15
                  </span>
                </div>
              </div>
              
              <button
                onClick={searchIMEI}
                disabled={!canSearch}
                className={`w-full py-3 px-6 rounded-lg font-semibold text-base transition-colors ${
                  canSearch 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>{t('verification_en_cours')}</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                    </svg>
                    <span>{t('verifier_imei')}</span>
                  </div>
                )}
              </button>
            </div>
            
            {(result || error) && !isLoading && (
              <div className="mt-6 text-center">
                <button 
                  onClick={resetSearch} 
                  className="inline-flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  {t('nouvelle_recherche')}
                </button>
              </div>
            )}
          </div>
        </div>
      </section>
      
      {isLoading && <ResultSkeleton />}
      {!isLoading && <ImeiSearchResults result={result} error={error} rateLimitInfo={rateLimitInfo} />}
    </>
  )
}
