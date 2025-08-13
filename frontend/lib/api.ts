import axios, { AxiosResponse, AxiosError } from 'axios'

// Configuration de base pour axios
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept-Language': 'fr'
  }
})

// Types pour les réponses
export interface IMEIResponse {
  id?: string
  imei: string
  trouve: boolean
  statut?: string
  numero_slot?: number
  message: string
  recherche_enregistree: boolean
  id_recherche: string
  contexte_acces: {
    niveau_acces: string
    motif_acces: string
    portee_donnees?: string
  }
  appareil?: {
    id?: string
    marque: string
    modele: string
    emmc?: string
    utilisateur_id?: string
    created_date?: string
    last_updated?: string
  }
}

export interface PublicStatsResponse {
  total_appareils: number
  total_recherches: number
  recherches_30_jours: number
  total_tacs_disponibles: number
  repartition_statuts: Record<string, number>
  derniere_mise_a_jour: string
  periode_stats?: string
  type_donnees?: string
  message?: string
}

export interface TACResponse {
  tac: string
  trouve: boolean
  message?: string
  marque?: string
  modele?: string
  type_appareil?: string
  categorie?: string
  fabricant?: string
  statut?: string
  // Champs optionnels si backend retourne plus
  [key: string]: any
}

export interface ErrorResponse {
  detail: string
  status_code: number
  retry_after?: string
  limit?: string
}

export interface RateLimitInfo {
  message: string
  retryAfter: string
  limit: string
}

// Classe pour gérer les services API
export class EIRApiService {
  private static searchCount = 0
  private static maxSearches = parseInt(process.env.NEXT_PUBLIC_VISITOR_SEARCH_LIMIT || '10')

  /**
   * Rechercher un IMEI dans la base de données EIR
   */
  static async searchIMEI(imei: string, authToken?: string): Promise<{
    success: boolean
    data?: IMEIResponse
    error?: string
    rateLimitInfo?: RateLimitInfo
  }> {
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

      // Préparer les headers avec ou sans authentification
      const headers: any = {
        'Content-Type': 'application/json',
        'Accept-Language': 'fr'
      }

      // Ajouter le token d'authentification si disponible
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`
      }

      // Appel à l'API
      const response: AxiosResponse<IMEIResponse> = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/imei/${cleanImei}`,
        { 
          headers,
          timeout: 10000,
          // Permettre les requêtes CORS
          withCredentials: false
        }
      )
      
      // Incrémenter le compteur de recherches
      this.searchCount++

      return {
        success: true,
        data: response.data
      }

    } catch (error) {
      console.error('Erreur lors de la recherche IMEI:', error)
      return this.handleApiError(error as AxiosError<ErrorResponse>)
    }
  }

  /**
   * Rechercher un TAC (8 chiffres)
   */
  static async searchTAC(tac: string): Promise<{
    success: boolean
    data?: TACResponse
    error?: string
  }> {
    try {
      // Nettoyage du TAC (enlever tout ce qui n'est pas un chiffre)
      const cleanTac = tac.replace(/\D/g, '')
      
      // Validation du format TAC
      if (cleanTac.length !== 8) {
        return {
          success: false,
          error: 'Le TAC doit contenir exactement 8 chiffres'
        }
      }

      // Appel à l'API pour rechercher le TAC
      const response: AxiosResponse<TACResponse> = await apiClient.get(`/tac/${cleanTac}`)
      return {
        success: true,
        data: response.data
      }

    } catch (error) {
      const axiosErr = error as AxiosError<any>
      if (axiosErr.response?.status === 404) {
        // TAC non trouvé, retourner un résultat "trouvé: false" sans erreur
        return { success: true, data: { tac, trouve: false, message: 'TAC non trouvé' } }
      }
      return {
        success: false,
        error: 'Erreur lors de la recherche TAC'
      }
    }
  }

  /**
   * Obtenir les statistiques publiques
   */
  static async getPublicStats(): Promise<{
    success: boolean
    data?: PublicStatsResponse
    error?: string
  }> {
    try {
      const response = await apiClient.get<PublicStatsResponse>('/public/statistiques')
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: 'Impossible de charger les statistiques'
      }
    }
  }

  /**
   * Vérifier l'état de l'API
   */
  static async checkHealth(): Promise<{
    success: boolean
    data?: any
    error?: string
  }> {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`,
        { timeout: 5000 }
      )
      return {
        success: true,
        data: response.data
      }
    } catch {
      return {
        success: false,
        error: 'API non disponible'
      }
    }
  }

  /**
   * Gestionnaire d'erreurs API centralisé
   */
  private static handleApiError(error: AxiosError<ErrorResponse>): {
    success: false
    error: string
    rateLimitInfo?: RateLimitInfo
  } {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data

      switch (status) {
        case 401:
          return {
            success: false,
            error: '🔐 Authentification requise. Cette recherche nécessite une connexion.'
          }

        case 403:
          return {
            success: false,
            error: '🚫 Accès refusé. Vous n\'avez pas les permissions pour accéder à cet IMEI.'
          }

        case 404:
          return {
            success: false,
            error: '❌ IMEI non trouvé dans la base de données.'
          }

        case 422:
          return {
            success: false,
            error: '📝 Format IMEI invalide. Veuillez vérifier le numéro saisi.'
          }

        case 429:
          // Rate limiting atteint
          return {
            success: false,
            error: '⚠️ Limite de recherche atteinte. Veuillez patienter avant de refaire une recherche.',
            rateLimitInfo: {
              message: 'Trop de recherches effectuées',
              retryAfter: data?.retry_after || '15 minutes',
              limit: data?.limit || 'Non spécifié'
            }
          }

        case 500:
          return {
            success: false,
            error: '🔧 Erreur interne du serveur. Veuillez réessayer plus tard.'
          }

        default:
          return {
            success: false,
            error: `Erreur serveur (${status}): ${data?.detail || 'Erreur inconnue'}`
          }
      }
    } else if (error.code === 'ECONNREFUSED') {
      return {
        success: false,
        error: '🔌 Impossible de se connecter au serveur. Vérifiez que l\'API EIR est démarrée sur ' + (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
      }
    } else if (error.code === 'ECONNABORTED') {
      return {
        success: false,
        error: '⏰ Délai d\'attente dépassé. Le serveur met trop de temps à répondre.'
      }
    } else if (error.message?.includes('Network Error')) {
      return {
        success: false,
        error: '🌐 Erreur réseau. Vérifiez que l\'API backend est démarrée et accessible.'
      }
    } else {
      return {
        success: false,
        error: `❌ Erreur de connexion: ${error.message}`
      }
    }
  }

  /**
   * Obtenir le nombre de recherches effectuées
   */
  static getSearchCount(): number {
    return this.searchCount
  }

  /**
   * Obtenir la limite de recherches
   */
  static getSearchLimit(): number {
    return this.maxSearches
  }

  /**
   * Reset le compteur de recherches
   */
  static resetSearchCount(): void {
    this.searchCount = 0
  }

  /**
   * Vérifier si la limite de recherches est atteinte
   */
  static isSearchLimitReached(): boolean {
    return this.searchCount >= this.maxSearches
  }

  /**
   * Valider le format IMEI
   */
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

// Configuration des intercepteurs pour logging
if (process.env.NODE_ENV === 'development') {
  apiClient.interceptors.request.use(
    (config) => {
      console.log('🚀 Requête API:', config.method?.toUpperCase(), config.url)
      return config
    },
    (error) => {
      console.error('❌ Erreur requête API:', error)
      return Promise.reject(error)
    }
  )

  apiClient.interceptors.response.use(
    (response) => {
      console.log('✅ Réponse API:', response.status, response.config.url)
      return response
    },
    (error) => {
      console.error('❌ Erreur réponse API:', error.response?.status, error.config?.url)
      return Promise.reject(error)
    }
  )
}

export default EIRApiService
