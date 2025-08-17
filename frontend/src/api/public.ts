import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'
import { PublicStatsResponse, HealthResponse, ApiResponse } from '../types/api'

// Fixed imports for Vercel build
export class PublicService {
  static async getPublicStats(language: 'fr' | 'en' | 'ar' = 'fr'): Promise<ApiResponse<PublicStatsResponse>> {
    const supportedLangs = ['ar', 'fr', 'en']
    const langHeader = supportedLangs.includes(language) ? language : 'fr'
    try {
      const response = await apiClient.get<PublicStatsResponse>('/public/statistiques', {
        headers: {
          'Accept-Language': langHeader
        }
      })
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      const apiError = handleApiError(error)
      return {
        success: false,
        error: apiError.message
      }
    }
  }

  static async checkHealth(language: 'fr' | 'en' | 'ar' = 'fr'): Promise<ApiResponse<HealthResponse>> {
    const supportedLangs = ['ar', 'fr', 'en']
    const langHeader = supportedLangs.includes(language) ? language : 'fr'
    try {
      const response = await apiClient.get<HealthResponse>('/health', { 
        timeout: 5000,
        headers: {
          'Accept-Language': langHeader
        }
      })
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      const apiError = handleApiError(error)
      return {
        success: false,
        error: apiError.message
      }
    }
  }
}

export default PublicService
