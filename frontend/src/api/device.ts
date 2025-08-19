import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'
import { ApiResponse } from '../types/api'

export interface DeviceItem {
  id: string;
  marque: string;
  modele: string;
  numero_serie: string;
  can_modify: boolean;
  motif_acces: string;
}

interface DeviceResponse {
  devices: DeviceItem[];
}

export class DeviceService {
  static async getDevices(authToken: string, skip = 0, limit = 20, language: 'fr' | 'en' | 'ar' = 'fr'): Promise<ApiResponse<DeviceResponse> & { status?: number }> {
    try {
      if (!authToken) {
        return {
          success: false,
          error: 'Authentication token is required.',
          status: 401,
        }
      }
      const headers: any = {
        'Accept-Language': language,
        'Authorization': `Bearer ${authToken}`,
      }
      const config: any = {
        headers,
        params: { skip, limit },
      }
      const response = await apiClient.get<DeviceResponse>('/appareils', config)
      return {
        success: true,
        data: response.data,
        status: response.status,
      }
    } catch (error: any) {
      console.error('❌ Erreur lors de la récupération des appareils:', error)
      const apiError = handleApiError(error)
      return {
        success: false,
        error: apiError.message,
        status: apiError.status,
      }
    }
  }
}

export default DeviceService


