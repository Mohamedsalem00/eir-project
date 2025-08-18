import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'
import SearchService from './SearchService'
import { IMEIResponse, IMEIDetailsResponse, ApiResponse } from '../types/api'

// Fixed import paths for Vercel deployment - v2
export class IMEIService {


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
      
      // Incrémenter le compteur de recherches via SearchService
      const currentCount = SearchService.getSearchCount()
      SearchService['updateSearchCount'](currentCount + 1)

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
    return SearchService.getSearchCount()
  }

  static getSearchLimit(): number {
    return SearchService.getSearchLimit()
  }

  static resetSearchCount(): void {
    SearchService.resetSearchCount()
  }

  static isSearchLimitReached(): boolean {
    return SearchService.isSearchLimitReached()
  }

  static getRemainingSearches(): number {
    return SearchService.getRemainingSearches()
  }

  static getSessionTimeRemaining(): string {
    return SearchService.getSessionTimeRemaining()
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
      
      // Incrémenter le compteur de recherches via SearchService
      const currentCount = SearchService.getSearchCount()
      SearchService.updateSearchCount(currentCount + 1)

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