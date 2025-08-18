// src/components/HeroSection.tsx

'use client'

import React from 'react'
import { useAuth } from '@/contexts/AuthContext'

interface HeroSectionProps {
  t: (key: string) => string
  currentLang: string
  isMounted: boolean
  searchLimitReached: boolean
  searchCount: number
  timeRemaining: string
  getSearchLimit: () => number
}

export const HeroSection: React.FC<HeroSectionProps> = ({ t, currentLang, isMounted, searchLimitReached, searchCount, timeRemaining, getSearchLimit }) => {
  const { user } = useAuth() // 👈 2. Get the user from the context

  return (
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
      
      {/* 👇 3. Conditionally render the search limit only for visitors */}
      {!user && (
        <div className="flex justify-center mb-8">
          <div className="inline-flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-4 px-4 py-3 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${!isMounted ? 'bg-gray-400' : searchLimitReached ? 'bg-red-500' : 'bg-green-500'}`}></div>
              <span className="text-sm font-medium text-gray-700">
                {t('recherches_restantes')}: {isMounted ? Math.max(0, getSearchLimit() - searchCount) : '...'}/{getSearchLimit()}
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
      )}
    </div>
  )
}