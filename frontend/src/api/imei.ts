import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'
import { IMEIResponse, IMEIDetailsResponse, ApiResponse } from '../types/api'

// Fixed import paths for Vercel deployment - v2
export class IMEIService {
  private static readonly SESSION_KEY = 'eir_search_count'
  private static readonly SESSION_DATE_KEY = 'eir_search_date'
  private static readonly SESSION_RESET_HOURS = 24
  public static readonly maxSearches = parseInt(process.env.NEXT_PUBLIC_VISITOR_SEARCH_LIMIT || '10')
  
  // Initialiser le compteur de recherches depuis localStorage
  private static initializeSearchCount(): number {
    if (typeof window === 'undefined') return 0
    
    try {
      const storedDate = localStorage.getItem(this.SESSION_DATE_KEY)
      const storedCount = localStorage.getItem(this.SESSION_KEY)
      
      if (!storedDate || !storedCount) {
        // Première visite, initialiser
        this.resetSearchSession()
        return 0
      }
      
      const sessionDate = new Date(parseInt(storedDate))
      const now = new Date()
      const hoursDiff = (now.getTime() - sessionDate.getTime()) / (1000 * 60 * 60)
      
      if (hoursDiff >= this.SESSION_RESET_HOURS) {
        // Session expirée, réinitialiser
        this.resetSearchSession()
        return 0
      }
      
      return parseInt(storedCount) || 0
    } catch (error) {
      console.warn('Erreur lors de la lecture du localStorage:', error)
      this.resetSearchSession()
      return 0
    }
  }
  
  private static resetSearchSession(): void {
    if (typeof window === 'undefined') return
    
    try {
      const now = new Date().getTime().toString()
      localStorage.setItem(this.SESSION_DATE_KEY, now)
      localStorage.setItem(this.SESSION_KEY, '0')
    } catch (error) {
      console.warn('Erreur lors de l\'écriture du localStorage:', error)
    }
  }
  
  private static updateSearchCount(count: number): void {
    if (typeof window === 'undefined') return
    
    try {
      localStorage.setItem(this.SESSION_KEY, count.toString())
    } catch (error) {
      console.warn('Erreur lors de la mise à jour du localStorage:', error)
    }
  }

  static async searchIMEI(imei: string, authToken?: string, language: 'fr' | 'en' | 'ar' = 'fr'): Promise<ApiResponse<IMEIResponse>> {
    try {
      // Validation côté client
      if (!imei || imei.length < 14) {
        return {
          success: false,
          error: 'L\'IMEI doit contenir au moins 14 chiffres'
        }
      }

      // Nettoyage de l'IMEI (enlever tout ce qui n'est pas un chiffre)
      const cleanImei = imei.replace(/\D/g, '')
      
      if (cleanImei.length > 15) {
        return {
          success: false,
          error: 'L\'IMEI ne peut pas dépasser 15 chiffres'
        }
      }

      // Préparer les headers avec authentification et langue
      // Ensure Accept-Language is always a valid backend language
      const supportedLangs = ['ar', 'fr', 'en']
      const langHeader = supportedLangs.includes(language) ? language : 'fr'
      const headers: any = {
        'Accept-Language': langHeader
      }

      // Ajouter le token d'authentification si disponible
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`
      }

      const config: any = {
        timeout: 10000,
        withCredentials: false,
        headers
      }

      // Appel à l'API
      const response = await apiClient.get<IMEIResponse>(`/imei/${cleanImei}`, config)
      
      // Incrémenter le compteur de recherches
      const currentCount = this.getSearchCount()
      this.updateSearchCount(currentCount + 1)

      return {
        success: true,
        data: response.data
      }

    } catch (error: any) {
      console.error('❌ Erreur lors de la recherche IMEI:', error)
      const apiError = handleApiError(error)
      
      return {
        success: false,
        error: apiError.message,
        rateLimitInfo: apiError.rateLimitInfo
      }
    }
  }

  static getSearchCount(): number {
    return this.initializeSearchCount()
  }

  static getSearchLimit(): number {
    return IMEIService.maxSearches
  }

  static resetSearchCount(): void {
    this.resetSearchSession()
  }

  static isSearchLimitReached(): boolean {
    return this.getSearchCount() >= IMEIService.maxSearches
  }

  static getRemainingSearches(): number {
    return Math.max(0, IMEIService.maxSearches - this.getSearchCount())
  }

  static getSessionTimeRemaining(): string {
    if (typeof window === 'undefined') return '24h'
    
    try {
      const storedDate = localStorage.getItem(this.SESSION_DATE_KEY)
      if (!storedDate) return '24h'
      
      const sessionDate = new Date(parseInt(storedDate))
      const now = new Date()
      const hoursRemaining = this.SESSION_RESET_HOURS - ((now.getTime() - sessionDate.getTime()) / (1000 * 60 * 60))
      
      if (hoursRemaining <= 0) return '0h'
      
      if (hoursRemaining < 1) {
        const minutesRemaining = Math.ceil(hoursRemaining * 60)
        return `${minutesRemaining}min`
      }
      
      return `${Math.ceil(hoursRemaining)}h`
    } catch (error) {
      return '24h'
    }
  }

  // ============== FONCTION MODIFIÉE CI-DESSOUS ==============
  // Cette fonction appelle maintenant l'endpoint de base /imei/{imei}
  static async getIMEIDetails(imei: string, authToken?: string, language: 'fr' | 'en' | 'ar' = 'fr'): Promise<ApiResponse<IMEIResponse>> {
    try {
      // Validation côté client
      if (!imei || imei.length < 14) {
        return {
          success: false,
          error: 'L\'IMEI doit contenir au moins 14 chiffres'
        }
      }

      // Nettoyage de l'IMEI
      const cleanImei = imei.replace(/\D/g, '')
      
      if (cleanImei.length > 15) {
        return {
          success: false,
          error: 'L\'IMEI ne peut pas dépasser 15 chiffres'
        }
      }

      // Préparer les headers avec authentification et langue
      // Ensure Accept-Language is always a valid backend language
      const supportedLangs = ['ar', 'fr', 'en']
      const langHeader = supportedLangs.includes(language) ? language : 'fr'
      const headers: any = {
        'Accept-Language': langHeader
      }

      // Ajouter le token d'authentification si disponible
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`
      }

      const config: any = {
        timeout: 15000,
        withCredentials: false,
        headers
      }

      // Appel à l'endpoint SANS /details et avec le bon type de réponse
      const response = await apiClient.get<IMEIResponse>(`/imei/${cleanImei}`, config)
      
      // Incrémenter le compteur de recherches
      const currentCount = this.getSearchCount()
      this.updateSearchCount(currentCount + 1)

      return {
        success: true,
        data: response.data
      }

    } catch (error: any) {
      console.error('❌ Erreur lors de la récupération des détails IMEI:', error)
      const apiError = handleApiError(error)
      
      return {
        success: false,
        error: apiError.message,
        rateLimitInfo: apiError.rateLimitInfo
      }
    }
  }

  static validateIMEI(imei: string): {
    isValid: boolean
    error?: string
    cleanImei?: string
  } {
    // Nettoyage
    const cleanImei = imei.replace(/\D/g, '')

    // Vérifications
    if (cleanImei.length === 0) {
      return {
        isValid: false,
        error: 'Veuillez saisir un numéro IMEI'
      }
    }

    if (cleanImei.length < 14) {
      return {
        isValid: false,
        error: `IMEI trop court (${cleanImei.length}/15 chiffres)`
      }
    }

    if (cleanImei.length > 15) {
      return {
        isValid: false,
        error: `IMEI trop long (${cleanImei.length}/15 chiffres)`
      }
    }

    return {
      isValid: true,
      cleanImei
    }
  }
}

export default IMEIService