import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'
import { ApiResponse, SearchHistoryItem } from '../types/api'

interface SearchHistoryResponse {
  searches: SearchHistoryItem[];
}

export class SearchHistoryService {
  static async getSearchHistory(authToken: string, language: 'fr' | 'en' | 'ar' = 'fr'): Promise<ApiResponse<SearchHistoryResponse>> {
    try {
      if (!authToken) {
        return {
          success: false,
          error: 'Authentication token is required.',
        }
      }

      const headers: any = {
        'Accept-Language': language,
        'Authorization': `Bearer ${authToken}`,
      }

      const config: any = {
        headers,
      }

      const response = await apiClient.get<SearchHistoryResponse>('/recherches', config)

      return {
        success: true,
        data: response.data,
      }
    } catch (error: any) {
      console.error('❌ Erreur lors de la récupération de l\'historique des recherches:', error)
      const apiError = handleApiError(error)
      
      return {
        success: false,
        error: apiError.message,
      }
    }
  }
}
