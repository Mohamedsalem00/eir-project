'use client'

import { useEffect, useState, useCallback } from 'react'
import { SearchService, PublicService, PublicStatsResponse } from '@/api'
import { SearchLimitDebug } from '@/components/SearchLimitDebug'
import { Footer } from '@/components/Footer'
import { HeroSection } from '@/components/HeroSection'
import Navigation from '@/components/Navigation'
import { ImeiSearchForm } from '@/components/ImeiSearchForm'
import { WhatIsImei } from '@/components/WhatIsImei'
import { Statistics } from '@/components/Statistics'
import { TacLookup } from '@/components/TacLookup'
import { ApiStatus } from '@/components/ApiStatus'
import SearchLimitPopup from '@/components/SearchLimitPopup'
import { useTranslation } from '@/hooks/useTranslation'
import { useAuth } from '@/contexts/AuthContext'

// Hook to prevent hydration issues
function useHydrationSafeState() {
  const [isMounted, setIsMounted] = useState(false)
  useEffect(() => { setIsMounted(true) }, [])
  return isMounted
}

export default function Home() {
  const { user } = useAuth()
  const { t, currentLang } = useTranslation()
  const isMounted = useHydrationSafeState()
  
  // State for search limit indicator
  const [searchCount, setSearchCount] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState<string>('')
  const [searchLimitReached, setSearchLimitReached] = useState(false)
  
  // State for API data
  const [stats, setStats] = useState<PublicStatsResponse | null>(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [statsError, setStatsError] = useState<string | null>(null)
  
  const isApiConnected = stats !== null && statsError === null;
    
  const loadStats = useCallback(async () => {
    setStatsLoading(true);
    setStatsError(null);
    try {
      const res = await PublicService.getPublicStats(currentLang);
      if (res.success && res.data) {
        setStats(res.data);
      } else {
        setStats(null);
        setStatsError(res.error || t('erreur_chargement_statistiques'));
      }
    } catch (err) {
      setStats(null);
      setStatsError(t('erreur_api_indisponible'));
    }
    setStatsLoading(false);
  }, [currentLang, t]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  useEffect(() => {
    const updateLimitInfo = () => {
      setSearchCount(SearchService.getSearchCount())
      setTimeRemaining(SearchService.getSessionTimeRemaining())
      setSearchLimitReached(SearchService.isSearchLimitReached())
    }
    updateLimitInfo()
    
    const interval = setInterval(updateLimitInfo, 60000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/20 dark:from-gray-900 dark:via-blue-900/20 dark:to-indigo-900/10 ${currentLang === 'ar' ? 'rtl' : 'ltr'}`}>
      <Navigation />

      <main className="container mx-auto px-4 sm:px-6 py-12 sm:py-16">
        <HeroSection
          t={t}
          currentLang={currentLang}
          isMounted={isMounted}
          searchLimitReached={searchLimitReached}
          searchCount={searchCount}
          timeRemaining={timeRemaining}
          getSearchLimit={SearchService.getSearchLimit}
        />

        <ImeiSearchForm />

        <WhatIsImei />

        <Statistics 
          stats={stats}
          isLoading={statsLoading}
          error={statsError}
          onRefresh={loadStats}
        />

        <TacLookup isApiConnected={isApiConnected} />
        {process.env.NODE_ENV === 'development' && 
        <ApiStatus 
          isApiConnected={isApiConnected}
          isLoading={statsLoading}
          onRetry={loadStats}
        />
        }
      {!user && (
        <SearchLimitPopup currentLang={currentLang} t={t} open={searchLimitReached} onClose={() => setSearchLimitReached(false)} />
      )}
      </main>

      <Footer
        title={t('titre')}
        copyright={`© 2025 Projet EIR. ${t('tous_droits_reserves')}`}
        builtWith={t('construit_avec')}
      />
      
      {process.env.NODE_ENV === 'development' && <SearchLimitDebug />}
    </div>
  )
}
