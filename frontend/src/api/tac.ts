import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'
import { TACResponse, ApiResponse } from '../types/api'

export class TACService {
  static async searchTAC(tac: string, language: 'fr' | 'en' | 'ar' = 'fr'): Promise<ApiResponse<TACResponse>> {
    try {
      const cleanTac = tac.replace(/\D/g, '')
      
      if (cleanTac.length !== 8) {
        return {
          success: false,
          error: 'Le TAC doit contenir exactement 8 chiffres'
        }
      }

      const response = await apiClient.get<TACResponse>(`/tac/${cleanTac}`, {
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
      
      if (apiError.status === 404) {
        return {
          success: true,
          data: {
            tac,
            trouve: false,
            message: 'TAC non trouvé'
          }
        }
      }
      
      return {
        success: false,
        error: apiError.message
      }
    }
  }
}
