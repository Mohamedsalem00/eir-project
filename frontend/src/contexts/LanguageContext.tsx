'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

// Import des traductions
import frTranslations from '../i18n/fr.json'
import enTranslations from '../i18n/en.json'
import arTranslations from '../i18n/ar.json'

type Language = 'fr' | 'en' | 'ar'

const translations = {
  fr: frTranslations,
  en: enTranslations,
  ar: arTranslations
}

interface LanguageContextType {
  currentLang: Language
  setCurrentLang: (lang: Language) => void
  supportedLanguages: Language[]
  t: (key: string, params?: Record<string, string | number>) => string
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

const SUPPORTED_LANGUAGES: Language[] = ['fr', 'en', 'ar']
const DEFAULT_LANGUAGE: Language = 'fr'
const STORAGE_KEY = 'preferred-language'

interface LanguageProviderProps {
  children: ReactNode
}

export function LanguageProvider({ children }: LanguageProviderProps) {

  const [currentLang, setCurrentLangState] = useState<Language>(DEFAULT_LANGUAGE)
  const [isLangLoaded, setIsLangLoaded] = useState(false)

  useEffect(() => {
    // Charger la langue depuis le localStorage
    if (typeof window !== 'undefined') {
      const savedLang = localStorage.getItem(STORAGE_KEY) as Language
      if (savedLang && SUPPORTED_LANGUAGES.includes(savedLang)) {
        setCurrentLangState(savedLang)
      }
    }
    setIsLangLoaded(true)
  }, [])

  const setCurrentLang = (lang: Language) => {
    if (SUPPORTED_LANGUAGES.includes(lang)) {
      setCurrentLangState(lang)
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, lang)
      }
      
      // Mettre à jour la direction du texte pour l'arabe
      if (typeof document !== 'undefined') {
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'
        document.documentElement.lang = lang
      }
    }
  }

  useEffect(() => {
    // Définir la direction initiale
    if (typeof document !== 'undefined') {
      document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr'
      document.documentElement.lang = currentLang
    }
  }, [currentLang])

  const t = (key: string, params?: Record<string, string | number>): string => {
    const translation = translations[currentLang]
    let text = translation[key as keyof typeof translation] || key

    // Remplacer les paramètres dans le texte (ex: {imei})
    if (params && typeof text === 'string') {
      Object.entries(params).forEach(([paramKey, paramValue]) => {
        text = text.replace(`{${paramKey}}`, String(paramValue))
      })
    }

    return text
  }

  const value: LanguageContextType = {
    currentLang,
    setCurrentLang,
    supportedLanguages: SUPPORTED_LANGUAGES,
    t,
  }

  if (!isLangLoaded) {
    // Optionally, show a loader or nothing until language is loaded
    return null
  }
  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext)
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}
