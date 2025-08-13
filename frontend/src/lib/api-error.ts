import { AxiosError } from 'axios'
import { ErrorResponse, RateLimitInfo } from '../types/api'

// Fixed import path for Vercel deployment
export class ApiError extends Error {
  public status: number
  public rateLimitInfo?: RateLimitInfo

  constructor(message: string, status: number, rateLimitInfo?: RateLimitInfo) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.rateLimitInfo = rateLimitInfo
  }
}

export function handleApiError(error: AxiosError<ErrorResponse>): ApiError {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data

    switch (status) {
      case 401:
        return new ApiError('Authentification requise', status)
      
      case 403:
        return new ApiError('Accès refusé', status)
      
      case 404:
        return new ApiError('Ressource non trouvée', status)
      
      case 422:
        return new ApiError('Données invalides', status)
      
      case 429:
        const rateLimitInfo: RateLimitInfo = {
          message: 'Limite de taux atteinte',
          retryAfter: data?.retry_after || '15 minutes',
          limit: data?.limit || 'Non spécifié'
        }
        return new ApiError('Limite de recherche atteinte', status, rateLimitInfo)
      
      case 500:
        return new ApiError('Erreur interne du serveur', status)
      
      default:
        return new ApiError(data?.detail || 'Erreur inconnue', status)
    }
  }

  if (error.code === 'ECONNREFUSED') {
    return new ApiError('Impossible de se connecter au serveur', 0)
  }

  if (error.code === 'ECONNABORTED') {
    return new ApiError('Délai d\'attente dépassé', 0)
  }

  if (error.message?.includes('Network Error')) {
    return new ApiError('Erreur réseau', 0)
  }

  return new ApiError(error.message || 'Erreur inconnue', 0)
}
