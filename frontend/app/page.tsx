'use client'

import { useEffect, useState } from 'react'
import { 
  IMEIService, 
  TACService, 
  PublicService,
  IMEIResponse, 
  IMEIDetailsResponse,
  TACResponse, 
  PublicStatsResponse,
  RateLimitInfo 
} from '../src/api'
import { SearchLimitDebug } from '../src/components/SearchLimitDebug'
import { useLanguage } from '../src/contexts/LanguageContext'

// Hook pour éviter les problèmes d'hydratation
function useHydrationSafeState() {
  const [isMounted, setIsMounted] = useState(false)
  
  useEffect(() => {
    setIsMounted(true)
  }, [])
  
  return isMounted
}

export default function Home() {
  // Utiliser le nouveau système de traduction
  const { t, currentLang, setCurrentLang } = useLanguage()
  
  // Hook pour éviter les problèmes d'hydratation
  const isMounted = useHydrationSafeState()
  
  const [imei, setImei] = useState('')
  const [result, setResult] = useState<IMEIDetailsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [rateLimitInfo, setRateLimitInfo] = useState<RateLimitInfo | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)

  // Stats
  const [stats, setStats] = useState<PublicStatsResponse | null>(null)
  const [statsLoading, setStatsLoading] = useState(false)
  const [statsError, setStatsError] = useState<string | null>(null)

  // TAC lookup
  const [tac, setTac] = useState('')
  const [tacResult, setTacResult] = useState<TACResponse | null>(null)
  const [tacLoading, setTacLoading] = useState(false)
  const [tacError, setTacError] = useState<string | null>(null)
  
  // Search count state for UI updates
  const [searchCount, setSearchCount] = useState(0)
  
  // Mobile menu state
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  // Time remaining state to avoid hydration issues
  const [timeRemaining, setTimeRemaining] = useState<string>('')
  
  // API connection state
  const [isApiConnected, setIsApiConnected] = useState<boolean | null>(null)
  const [apiCheckLoading, setApiCheckLoading] = useState(false)
  
  // État pour éviter les problèmes d'hydratation
  const [searchLimitReached, setSearchLimitReached] = useState(false)
  
  // Mise à jour de l'état après le montage pour éviter l'hydratation différentielle
  useEffect(() => {
    setSearchLimitReached(IMEIService.isSearchLimitReached())
    setSearchCount(IMEIService.getSearchCount())
    setTimeRemaining(IMEIService.getSessionTimeRemaining())
    
    // Update time remaining every minute to avoid hydration issues
    const interval = setInterval(() => {
      setTimeRemaining(IMEIService.getSessionTimeRemaining())
      setSearchLimitReached(IMEIService.isSearchLimitReached())
    }, 60000)
    
    return () => clearInterval(interval)
  }, [])
  
  // Update search count on component mount and after searches
  useEffect(() => {
    if (isMounted) {
      setSearchCount(IMEIService.getSearchCount())
      setSearchLimitReached(IMEIService.isSearchLimitReached())
    }
  }, [isMounted])

  useEffect(() => {
    const loadStats = async () => {
      setStatsLoading(true)
      const res = await PublicService.getPublicStats(currentLang)
      if (res.success && res.data) {
        setStats(res.data)
      } else {
        setStatsError(res.error || 'Erreur chargement statistiques')
      }
      setStatsLoading(false)
    }
    loadStats()
  }, [currentLang])

  // Fonction pour vérifier l'état de l'API
  const checkApiConnection = async () => {
    setApiCheckLoading(true)
    try {
      // Essayer d'obtenir les stats publiques comme test de connexion
      const res = await PublicService.getPublicStats(currentLang)
      setIsApiConnected(res.success)
    } catch (error) {
      setIsApiConnected(false)
    }
    setApiCheckLoading(false)
  }

  // Vérifier la connexion API au chargement
  useEffect(() => {
    checkApiConnection()
  }, [currentLang])

  const searchIMEI = async () => {
    setError(null)
    setResult(null)
    setRateLimitInfo(null)
    setValidationError(null)

    // Vérifier si l'API est connectée
    if (!isApiConnected) {
      setError(t('api_deconnectee') + ' - ' + t('service_indisponible'))
      return
    }

    const validation = IMEIService.validateIMEI(imei)
    if (!validation.isValid) {
      setValidationError(validation.error || 'IMEI invalide')
      return
    }

    if (searchLimitReached) {
      setError(`Limite de recherches atteinte (${IMEIService.getSearchLimit()}) pour cette session. Réinitialisation dans ${timeRemaining || IMEIService.getSessionTimeRemaining()}.`)
      return
    }

    setIsLoading(true)

    try {
      // Utiliser la nouvelle endpoint des détails complets IMEI
      const response = await IMEIService.getIMEIDetails(validation.cleanImei!, undefined, currentLang)

      if (response.success && response.data) {
        setResult(response.data)
        // Update search count state for UI
        if (isMounted) {
          setSearchCount(IMEIService.getSearchCount())
          setSearchLimitReached(IMEIService.isSearchLimitReached())
          setTimeRemaining(IMEIService.getSessionTimeRemaining())
        }
      } else {
        setError(response.error || 'Erreur inconnue')
        if (response.rateLimitInfo) {
          setRateLimitInfo(response.rateLimitInfo)
        }
      }
    } catch (e) {
      setError('Erreur inattendue lors de la recherche')
    } finally {
      setIsLoading(false)
    }
  }

  const searchTAC = async () => {
    setTacError(null)
    setTacResult(null)
    
    // Vérifier si l'API est connectée
    if (!isApiConnected) {
      setTacError(t('api_deconnectee') + ' - ' + t('service_indisponible'))
      return
    }
    
    const cleanTac = tac.replace(/\D/g, '')
    if (cleanTac.length !== 8) {
      setTacError('Le TAC doit contenir exactement 8 chiffres')
      return
    }
    setTacLoading(true)
    const res = await TACService.searchTAC(cleanTac, currentLang)
    if (res.success && res.data) {
      setTacResult(res.data)
    } else {
      setTacError(res.error || 'Erreur lors de la recherche TAC')
    }
    setTacLoading(false)
  }

  const resetSearch = () => {
    setImei('')
    setResult(null)
    setError(null)
    setRateLimitInfo(null)
    setValidationError(null)
    // Update search count display
    if (isMounted) {
      setSearchCount(IMEIService.getSearchCount())
      setSearchLimitReached(IMEIService.isSearchLimitReached())
      setTimeRemaining(IMEIService.getSessionTimeRemaining())
    }
  }

  const handleImeiChange = (value: string) => {
    const cleanValue = value.replace(/\D/g, '').slice(0, 15)
    setImei(cleanValue)
    if (validationError) setValidationError(null)
  }

  const currentValidation = IMEIService.validateIMEI(imei)
  const canSearch = isMounted && currentValidation.isValid && !isLoading && !searchLimitReached && isApiConnected

  return (
    <div className={`min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/20 ${currentLang === 'ar' ? 'rtl' : 'ltr'}`}>
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Brand */}
            <div className="flex items-center space-x-3 min-w-0 flex-1 lg:flex-initial">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-semibold text-sm sm:text-base">EIR</span>
                </div>
              </div>
              <div className="min-w-0">
                <h1 className="text-lg sm:text-xl font-semibold text-gray-900 leading-tight truncate">{t('titre')}</h1>
                <p className="text-xs sm:text-sm text-gray-600 hidden sm:block truncate">{t('sous_titre')}</p>
              </div>
            </div>
            
            {/* Mobile Menu Button */}
            <button 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg text-gray-600 hover:text-blue-600 hover:bg-gray-50 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
            
            {/* Desktop Language Switcher & Navigation */}
            <div className="hidden lg:flex items-center space-x-6">
              {/* Language Switcher */}
              <div className="flex items-center space-x-1 bg-gray-50 rounded-lg p-1">
                {(['fr', 'en', 'ar'] as const).map((lang) => (
                  <button
                    key={lang}
                    onClick={() => setCurrentLang(lang)}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      currentLang === lang
                        ? 'bg-white text-blue-600 shadow-sm'
                        : 'text-gray-600 hover:text-blue-600'
                    }`}
                  >
                    {lang.toUpperCase()}
                  </button>
                ))}
              </div>
              
              <nav className="flex items-center space-x-6 text-sm">
                <a href="#" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">{t('accueil')}</a>
                <a href="#what-is-imei" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">{t('quest_ce_que_imei')}</a>
                <a href="/test" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">{t('test_api')}</a>
                <a href="#" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium">{t('commencer')}</a>
              </nav>
            </div>
          </div>
          
          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="lg:hidden mt-4 pt-4 border-t border-gray-200">
              <div className="space-y-3">
                <a href="#" className="block text-gray-700 hover:text-blue-600 transition-colors font-medium py-2">{t('accueil')}</a>
                <a href="#what-is-imei" className="block text-gray-700 hover:text-blue-600 transition-colors font-medium py-2" onClick={() => setMobileMenuOpen(false)}>{t('quest_ce_que_imei')}</a>
                <a href="/test" className="block text-gray-700 hover:text-blue-600 transition-colors font-medium py-2">{t('test_api')}</a>
                
                {/* Mobile Language Switcher */}
                <div className="pt-3 border-t border-gray-200">
                  <span className="text-sm font-medium text-gray-600 mb-2 block">Language:</span>
                  <div className="flex items-center space-x-2">
                    {(['fr', 'en', 'ar'] as const).map((lang) => (
                      <button
                        key={lang}
                        onClick={() => setCurrentLang(lang)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          currentLang === lang
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-600 hover:text-blue-600 bg-gray-50'
                        }`}
                      >
                        {lang.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="pt-3">
                  <a href="#" className="block w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium text-center">{t('commencer')}</a>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="container mx-auto px-4 sm:px-6 py-12 sm:py-16">
        {/* Hero Section */}
        <div className="text-center max-w-4xl mx-auto mb-12 sm:mb-16">
          <div className="inline-flex items-center px-4 py-2 bg-blue-50 border border-blue-200 rounded-full text-sm font-medium text-blue-700 mb-6">
            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            {t('sous_titre')}
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-semibold text-gray-900 mb-6 leading-tight">
            {t('titre_hero').split(' ').map((word, index, array) => 
              index === array.length - 1 ? (
                <span key={index} className="text-blue-600">{word}</span>
              ) : (
                <span key={index}>{word} </span>
              )
            )}
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 leading-relaxed mb-8 max-w-3xl mx-auto">
            {t('sous_titre_hero')}
          </p>
          
          {/* Search limit indicator */}
          <div className="flex justify-center mb-8">
            <div className="inline-flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-4 px-4 py-3 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${!isMounted ? 'bg-gray-400' : searchLimitReached ? 'bg-red-500' : 'bg-green-500'}`}></div>
                <span className="text-sm font-medium text-gray-700">
                  {t('recherches_restantes')}: {isMounted ? Math.max(0, IMEIService.getSearchLimit() - searchCount) : '...'}/{IMEIService.getSearchLimit()}
                </span>
              </div>
              {isMounted && !searchLimitReached && (
                <>
                  <div className="hidden sm:block h-4 w-px bg-gray-300"></div>
                  <span className="text-sm text-gray-500">
                    {t('reinitialisation_dans')}: {timeRemaining || '...'}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* What is IMEI Section */}
        <section id="what-is-imei" className="max-w-6xl mx-auto mb-12 sm:mb-16">
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 sm:p-8">
            <div className="text-center mb-8">
              <div className="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-4">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Information Guide
              </div>
              <h2 className="text-2xl sm:text-3xl font-semibold text-gray-900 mb-4">{t('titre_quest_ce_que_imei')}</h2>
              <p className="text-base sm:text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
                {t('sous_titre_quest_ce_que_imei')}
              </p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 mb-8">
              <div className="space-y-4">
                <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('identification_unique')}</h3>
                    <p className="text-gray-600 text-sm leading-relaxed">{t('description_identification_unique')}</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('securite_tracage')}</h3>
                    <p className="text-gray-600 text-sm leading-relaxed">{t('description_securite_tracage')}</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('registre_equipements')}</h3>
                    <p className="text-gray-600 text-sm leading-relaxed">{t('description_registre_equipements')}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-6 text-center">{t('comment_trouver_imei')}</h3>
                
                <div className="space-y-6">
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                      <span className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm mr-3">1</span>
                      {t('methode_code_numerotation')}
                    </h4>
                    <div className="bg-gray-900 rounded-lg p-4 mb-3">
                      <code className="text-green-400 font-mono text-xl font-semibold">*#06#</code>
                    </div>
                    <p className="text-gray-600 text-sm leading-relaxed">{t('description_code_numerotation')}</p>
                  </div>
                  
                  <div className="space-y-3">
                    <h4 className="text-lg font-semibold text-gray-900">{t('autres_methodes')}</h4>
                    <div className="space-y-2">
                      <div className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-gray-200">
                        <span className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-white font-semibold text-xs">2</span>
                        <span className="text-gray-700 text-sm">{t('methode_parametres')}</span>
                      </div>
                      <div className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-gray-200">
                        <span className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-white font-semibold text-xs">3</span>
                        <span className="text-gray-700 text-sm">{t('methode_batterie')}</span>
                      </div>
                      <div className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-gray-200">
                        <span className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-white font-semibold text-xs">4</span>
                        <span className="text-gray-700 text-sm">{t('methode_boite')}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* IMEI Search Form */}
        <section className="max-w-4xl mx-auto mb-12 sm:mb-16">
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 sm:p-8">
            <div className="text-center mb-6">
              <div className="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-4">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
                IMEI Verification
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
                        validationError 
                          ? 'border-red-300 bg-red-50 text-red-900' 
                          : currentValidation.isValid 
                            ? 'border-green-300 bg-green-50 text-green-900' 
                            : 'border-gray-300 bg-white hover:border-gray-400'
                      }`}
                      maxLength={15}
                      disabled={isLoading}
                      dir="ltr"
                    />
                    {imei.length > 0 && (
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        {currentValidation.isValid ? (
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
              
              {/* Validation Messages */}
              {validationError && (
                <div className="mt-4 flex items-start space-x-3 p-4 rounded-lg border border-red-200 bg-red-50">
                  <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-red-800 text-sm">{t('imei_invalide')}</h4>
                    <p className="text-red-700 text-sm">{validationError}</p>
                  </div>
                </div>
              )}
              
              {!validationError && imei.length > 0 && !currentValidation.isValid && (
                <div className="mt-4 flex items-start space-x-3 p-4 rounded-lg border border-yellow-200 bg-yellow-50">
                  <div className="w-6 h-6 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-yellow-800 text-sm">{t('continuer_saisie')}</h4>
                    <p className="text-yellow-700 text-sm">{imei.length}/15 {t('chiffres_saisis')}</p>
                  </div>
                </div>
              )}
              
              {(result || error) && (
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

        {/* Enhanced Error Display */}
        {error && (
          <div className="max-w-6xl mx-auto mb-16">
            <div className="bg-white/90 backdrop-blur-lg border-3 border-red-300 rounded-4xl p-12 shadow-2xl relative overflow-hidden">
              {/* Background Effects */}
              <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-red-100/40 to-transparent rounded-full -mr-20 -mt-20"></div>
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-red-100/30 to-transparent rounded-full -ml-16 -mb-16"></div>
              
              <div className="relative z-10">
                <div className="flex items-start space-x-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-red-500 to-red-600 rounded-3xl flex items-center justify-center flex-shrink-0 shadow-xl">
                    <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-3xl font-black text-red-900 mb-4">{t('erreur_verification')}</h3>
                    <p className="text-xl text-red-800 leading-relaxed mb-6">{error}</p>
                    {rateLimitInfo && (
                      <div className="p-6 bg-gradient-to-r from-red-50 to-rose-50 rounded-3xl border-2 border-red-200 shadow-lg">
                        <h4 className="text-xl font-black text-red-900 mb-4">{t('info_limite_taux')}</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="p-4 bg-white/70 backdrop-blur-sm rounded-2xl border border-red-100">
                            <div className="text-lg font-black text-red-800 mb-2">{t('ressayer_apres')}</div>
                            <div className="text-2xl font-black text-red-600">{rateLimitInfo.retryAfter}</div>
                          </div>
                          <div className="p-4 bg-white/70 backdrop-blur-sm rounded-2xl border border-red-100">
                            <div className="text-lg font-black text-red-800 mb-2">{t('limite')}</div>
                            <div className="text-2xl font-black text-red-600">{rateLimitInfo.limit}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Professional Results Display */}
        {result && (
          <div className="max-w-6xl mx-auto mb-20">
            <div className="bg-white/95 backdrop-blur-lg rounded-4xl border border-gray-200/60 shadow-2xl p-12 md:p-16 relative overflow-hidden">
              {/* Advanced Background Effects */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-100/30 via-green-100/20 to-transparent rounded-full -mr-32 -mt-32"></div>
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-purple-100/25 via-indigo-100/15 to-transparent rounded-full -ml-24 -mb-24"></div>
              
              <div className="relative z-10">
                {/* Enhanced Header */}
                <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6 mb-8">
                  <div className="flex-1">
                    <div className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium mb-4">
                      <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Résultats de Vérification Complète
                    </div>
                    <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-3 leading-tight">
                      Détails IMEI : {result.imei}
                    </h3>
                    <p className="text-gray-600">Analyse complète incluant recherche locale, validation TAC et détails d'appareil</p>
                  </div>
                  <div className={`px-6 py-3 rounded-lg font-semibold border ${
                    result.resume?.statut_global === 'actif_valide' 
                      ? 'bg-green-50 text-green-800 border-green-200' 
                      : result.resume?.statut_global === 'invalide_luhn'
                        ? 'bg-red-50 text-red-800 border-red-200'
                        : 'bg-amber-50 text-amber-800 border-amber-200'
                  }`}>
                    {result.resume?.statut_global?.replace('_', ' ').toUpperCase() || 'ANALYSÉ'}
                  </div>
                </div>
                
                {/* Résumé Global */}
                {result.resume && (
                  <div className="mb-8">
                    <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                      <h4 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                          <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                        Résumé de Validation
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className={`p-4 rounded-lg border ${
                          result.resume.trouve_localement 
                            ? 'bg-green-50 border-green-200' 
                            : 'bg-gray-50 border-gray-200'
                        }`}>
                          <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${
                              result.resume.trouve_localement ? 'bg-green-500' : 'bg-gray-400'
                            }`}></div>
                            <span className="font-medium text-sm">Base Locale</span>
                          </div>
                          <span className="text-xs text-gray-600">
                            {result.resume.trouve_localement ? 'Trouvé' : 'Non trouvé'}
                          </span>
                        </div>
                        <div className={`p-4 rounded-lg border ${
                          result.resume.tac_valide 
                            ? 'bg-green-50 border-green-200' 
                            : 'bg-red-50 border-red-200'
                        }`}>
                          <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${
                              result.resume.tac_valide ? 'bg-green-500' : 'bg-red-500'
                            }`}></div>
                            <span className="font-medium text-sm">TAC Valide</span>
                          </div>
                          <span className="text-xs text-gray-600">
                            {result.resume.tac_valide ? 'Valide' : 'Invalide'}
                          </span>
                        </div>
                        <div className={`p-4 rounded-lg border ${
                          result.resume.luhn_valide 
                            ? 'bg-green-50 border-green-200' 
                            : 'bg-red-50 border-red-200'
                        }`}>
                          <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${
                              result.resume.luhn_valide ? 'bg-green-500' : 'bg-red-500'
                            }`}></div>
                            <span className="font-medium text-sm">Luhn Valide</span>
                          </div>
                          <span className="text-xs text-gray-600">
                            {result.resume.luhn_valide ? 'Valide' : 'Invalide'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Information Grid - 3 sections */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                  
                  {/* Recherche Locale */}
                  {result.recherche_locale && (
                    <div className="space-y-4">
                      <div className="p-6 bg-white rounded-lg border border-gray-200">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                          <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                            <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 3v7h10V7H5z" clipRule="evenodd" />
                            </svg>
                          </div>
                          Recherche Locale
                        </h4>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center py-2 border-b border-gray-100">
                            <span className="text-sm font-medium text-gray-600">Statut</span>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              result.recherche_locale.trouve 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {result.recherche_locale.trouve ? 'Trouvé' : 'Non trouvé'}
                            </span>
                          </div>
                          {result.recherche_locale.statut && (
                            <div className="flex justify-between items-center py-2 border-b border-gray-100">
                              <span className="text-sm font-medium text-gray-600">État</span>
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                result.recherche_locale.statut === 'actif' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {result.recherche_locale.statut}
                              </span>
                            </div>
                          )}
                          {result.recherche_locale.appareil && (
                            <>
                              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                                <span className="text-sm font-medium text-gray-600">Marque</span>
                                <span className="text-sm text-gray-900">{result.recherche_locale.appareil.marque}</span>
                              </div>
                              <div className="flex justify-between items-center py-2">
                                <span className="text-sm font-medium text-gray-600">Modèle</span>
                                <span className="text-sm text-gray-900">{result.recherche_locale.appareil.modele}</span>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Validation TAC */}
                  {result.validation_tac && (
                    <div className="space-y-4">
                      <div className="p-6 bg-white rounded-lg border border-gray-200">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                            <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                          Validation TAC
                        </h4>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center py-2 border-b border-gray-100">
                            <span className="text-sm font-medium text-gray-600">TAC</span>
                            <span className="text-sm font-mono text-gray-900">{result.validation_tac.tac}</span>
                          </div>
                          <div className="flex justify-between items-center py-2 border-b border-gray-100">
                            <span className="text-sm font-medium text-gray-600">TAC Valide</span>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              result.validation_tac.valide 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {result.validation_tac.valide ? 'Oui' : 'Non'}
                            </span>
                          </div>
                          <div className="flex justify-between items-center py-2 border-b border-gray-100">
                            <span className="text-sm font-medium text-gray-600">Luhn Valide</span>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              result.validation_tac.luhn_valide 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {result.validation_tac.luhn_valide ? 'Oui' : 'Non'}
                            </span>
                          </div>
                          <div className="flex justify-between items-center py-2">
                            <span className="text-sm font-medium text-gray-600">Source</span>
                            <span className="text-sm text-gray-900">{result.validation_tac.source}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Détails TAC */}
                  {result.details_tac && (
                    <div className="space-y-4">
                      <div className="p-6 bg-white rounded-lg border border-gray-200">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                          <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                            <svg className="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd" />
                            </svg>
                          </div>
                          Détails TAC
                        </h4>
                        <div className="space-y-3">
                          {result.details_tac.trouve ? (
                            <>
                              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                                <span className="text-sm font-medium text-gray-600">Marque</span>
                                <span className="text-sm text-gray-900">{result.details_tac.marque}</span>
                              </div>
                              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                                <span className="text-sm font-medium text-gray-600">Modèle</span>
                                <span className="text-sm text-gray-900">{result.details_tac.modele}</span>
                              </div>
                              {result.details_tac.type_appareil && (
                                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                                  <span className="text-sm font-medium text-gray-600">Type</span>
                                  <span className="text-sm text-gray-900">{result.details_tac.type_appareil}</span>
                                </div>
                              )}
                              {result.details_tac.statut && (
                                <div className="flex justify-between items-center py-2">
                                  <span className="text-sm font-medium text-gray-600">Statut</span>
                                  <span className="text-sm text-gray-900">{result.details_tac.statut}</span>
                                </div>
                              )}
                            </>
                          ) : (
                            <div className="text-center py-4">
                              <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                                <svg className="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                </svg>
                              </div>
                              <p className="text-sm text-gray-500">{result.details_tac.message}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                  
                </div>
                
                {/* Informations de Recherche */}
                <div className="bg-gray-50 rounded-lg p-6 border border-gray-200 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
                        <path fillRule="evenodd" d="M4 5a2 2 0 012-2v1a1 1 0 001 1h6a1 1 0 001-1V3a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm2.5 5a1.5 1.5 0 100-3 1.5 1.5 0 000 3zm2.45 4a2.5 2.5 0 10-4.9 0h4.9zM12 9a1 1 0 100 2h3a1 1 0 100-2h-3zm-1 4a1 1 0 011-1h2a1 1 0 110 2h-2a1 1 0 01-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <h5 className="font-semibold text-gray-800">Analyse Complète Effectuée</h5>
                      <p className="text-gray-600 text-sm">
                        Recherche locale, validation TAC et vérification Luhn
                      </p>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <div className="text-gray-600 font-medium text-sm mb-1">Horodatage</div>
                    <span className="text-sm text-gray-800 bg-white px-3 py-1 rounded border">
                      {result.timestamp ? new Date(result.timestamp).toLocaleString() : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Real Statistics Section */}
        <section className="max-w-6xl mx-auto mb-24">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 tracking-tight">{t('statistiques_systeme')}</h3>
              <p className="text-gray-600 mt-1">{t('donnees_publiques')}</p>
            </div>
            <button
              onClick={async () => {
                setStatsLoading(true)
                const res = await PublicService.getPublicStats(currentLang)
                if (res.success && res.data) { setStats(res.data); setStatsError(null) } else { setStatsError(res.error || t('erreur')) }
                setStatsLoading(false)
              }}
              disabled={!isApiConnected || statsLoading}
              className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                isApiConnected && !statsLoading
                  ? 'text-blue-700 hover:text-blue-900 bg-blue-50 hover:bg-blue-100'
                  : 'text-gray-400 bg-gray-50 cursor-not-allowed'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>{t('actualiser')}</span>
            </button>
          </div>
          <div className="bg-white/90 backdrop-blur border rounded-2xl p-8 shadow-xl">
            {statsLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="flex items-center space-x-3">
                  <svg className="animate-spin w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-gray-600 font-medium">{t('chargement')}</span>
                </div>
              </div>
            )}
            {statsError && (
              <div className="text-center py-12">
                <div className="text-red-600 font-medium">{t('erreur')}: {statsError}</div>
              </div>
            )}
            {stats && !statsLoading && (
              <div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
                  <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl border border-blue-200">
                    <div className="text-3xl font-black text-blue-900 mb-2">{stats.total_appareils?.toLocaleString()}</div>
                    <div className="text-sm font-semibold uppercase tracking-wide text-blue-700">{t('appareils')}</div>
                  </div>
                  <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-2xl border border-green-200">
                    <div className="text-3xl font-black text-green-900 mb-2">{stats.total_recherches?.toLocaleString()}</div>
                    <div className="text-sm font-semibold uppercase tracking-wide text-green-700">{t('recherches')}</div>
                  </div>
                  <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl border border-purple-200">
                    <div className="text-3xl font-black text-purple-900 mb-2">{stats.recherches_30_jours?.toLocaleString()}</div>
                    <div className="text-sm font-semibold uppercase tracking-wide text-purple-700">{t('jours_30')}</div>
                  </div>
                  <div className="text-center p-6 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-2xl border border-indigo-200">
                    <div className="text-3xl font-black text-indigo-900 mb-2">{stats.total_tacs_disponibles?.toLocaleString()}</div>
                    <div className="text-sm font-semibold uppercase tracking-wide text-indigo-700">TAC</div>
                  </div>
                </div>
                
                {stats.repartition_statuts && Object.keys(stats.repartition_statuts).length > 0 && (
                  <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200">
                    <h4 className="text-lg font-bold text-gray-800 mb-4">{t('repartition_statuts_imei')}</h4>
                    <div className="flex flex-wrap gap-3">
                      {Object.entries(stats.repartition_statuts).map(([status, count]) => (
                        <div key={status} className="px-4 py-2 bg-white rounded-xl border text-gray-700 font-medium shadow-sm">
                          {status}: <span className="font-bold text-gray-900">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="mt-8 text-center text-sm text-gray-500">
                  <span>{t('derniere_mise_a_jour')}: {new Date(stats.derniere_mise_a_jour).toLocaleString(currentLang === 'ar' ? 'ar-AE' : currentLang === 'en' ? 'en-US' : 'fr-FR')}</span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* TAC Lookup Section */}
        <section className="max-w-4xl mx-auto mb-28">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 tracking-tight mb-2">{t('recherche_tac')}</h3>
            <p className="text-gray-600">{t('description_recherche_tac')}</p>
          </div>
          <div className="bg-white/90 backdrop-blur border rounded-2xl p-8 shadow-xl mb-6">
            <div className="flex flex-col md:flex-row gap-6">
              <div className="flex-1">
                <label className="block text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">
                  {t('code_tac')}
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <input
                  type="text"
                  value={tac}
                  onChange={(e) => setTac(e.target.value.replace(/\D/g, '').slice(0,8))}
                  placeholder={t('entrer_tac')}
                  className="w-full p-4 border-2 border-gray-300 rounded-xl text-lg font-mono focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all"
                  maxLength={8}
                  disabled={tacLoading}
                  dir="ltr"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={searchTAC}
                  disabled={tacLoading || tac.replace(/\D/g,'').length !== 8 || !isApiConnected}
                  className={`h-16 font-bold px-8 rounded-xl text-lg tracking-wide transition-all transform ${
                    tac.replace(/\D/g,'').length === 8 && !tacLoading && isApiConnected
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl hover:scale-105' 
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {tacLoading ? t('recherche_en_cours') : t('rechercher')}
                </button>
              </div>
            </div>
            {tacError && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
                <div className="text-red-700 font-medium">{tacError}</div>
              </div>
            )}
          </div>
          
          {tacResult && (
            <div className="bg-white/90 backdrop-blur border rounded-2xl p-8 shadow-xl">
              <h4 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                <svg className="w-6 h-6 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 3v7h10V7H5z" clipRule="evenodd" />
                </svg>
                {t('resultat_tac')}
              </h4>
              {!tacResult.trouve ? (
                <div className="text-center py-8">
                  <div className="text-gray-600 text-lg">{t('tac_non_trouve_base')}</div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {[
                    { field: 'marque', label: t('marque') },
                    { field: 'modele', label: t('modele') },
                    { field: 'type_appareil', label: t('type_appareil') },
                    { field: 'categorie', label: t('categorie') },
                    { field: 'fabricant', label: t('fabricant') },
                    { field: 'statut', label: t('statut') }
                  ].map(({ field, label }) => 
                    tacResult[field] && (
                      <div key={field} className="bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-4">
                        <span className="block text-gray-500 font-semibold text-sm uppercase tracking-wide mb-2">{label}</span>
                        <span className="font-bold text-gray-900 text-lg">{tacResult[field]}</span>
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          )}
        </section>

        {/* API Status & CTA */}
        <div className="text-center space-y-6">
          {isApiConnected === null ? (
            // État de chargement
            <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-gray-50 to-gray-100 text-gray-600 border border-gray-200 rounded-full font-medium shadow-sm">
              <div className="w-3 h-3 bg-gray-400 rounded-full mr-3 animate-pulse"></div>
              <span>{t('chargement')}...</span>
            </div>
          ) : isApiConnected ? (
            // API connectée
            <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 border border-green-200 rounded-full font-medium shadow-sm">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-3 animate-pulse"></div>
              <span>{t('api_connectee')} ({process.env.NEXT_PUBLIC_API_URL})</span>
            </div>
          ) : (
            // API déconnectée
            <div className="space-y-3">
              <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-red-50 to-rose-50 text-red-700 border border-red-200 rounded-full font-medium shadow-sm">
                <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                <span>{t('api_deconnectee')} - {t('service_indisponible')}</span>
              </div>
              <button
                onClick={checkApiConnection}
                disabled={apiCheckLoading}
                className="inline-flex items-center px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {apiCheckLoading ? (
                  <>
                    <svg className="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {t('chargement')}
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {t('verifier_connexion')}
                  </>
                )}
              </button>
            </div>
          )}
          <div>
            <a 
              href="/test" 
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 text-white rounded-2xl font-bold text-lg transition-all transform hover:scale-105 hover:shadow-2xl"
            >
              <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {t('interface_test')}
            </a>
          </div>
        </div>
      </main>

      <footer className="bg-white/80 backdrop-blur border-t border-gray-200/50 mt-20">
        <div className="container mx-auto px-6 py-12 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <span className="text-white font-bold text-xl">EIR</span>
            </div>
            <h3 className="text-lg font-bold text-gray-900">{t('titre')}</h3>
          </div>
          <div className="text-sm text-gray-500 space-y-2">
            <p>&copy; 2025 Projet EIR. {t('tous_droits_reserves')}</p>
            <p>{t('construit_avec')}</p>
          </div>
        </div>
      </footer>
      
      {/* Debug component - Remove in production */}
      {process.env.NODE_ENV === 'development' && <SearchLimitDebug />}
    </div>
  )
}
