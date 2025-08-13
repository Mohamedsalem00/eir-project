import { apiClient } from '../../lib/api-client'
import { handleApiError } from '../../lib/api-error'
import { PublicStatsResponse, HealthResponse, ApiResponse } from '../types/api'

export class PublicService {
  static async getPublicStats(language: 'fr' | 'en' | 'ar' = 'fr'): Promise<ApiResponse<PublicStatsResponse>> {
    try {
      const response = await apiClient.get<PublicStatsResponse>('/public/statistiques', {
        headers: {
          'Accept-Language': language
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
    try {
      const response = await apiClient.get<HealthResponse>('/health', { 
        timeout: 5000,
        headers: {
          'Accept-Language': language
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
