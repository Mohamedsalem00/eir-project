import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'

// Authentication Types
export interface LoginRequest {
  email: string
  mot_de_passe: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  nom: string
  email: string
  mot_de_passe: string
  type_utilisateur: string
}

export interface RegisterResponse {
  id: string
  nom: string
  email: string
  type_utilisateur: string
}

export interface UserProfile {
  id: string
  nom: string
  email: string
  type_utilisateur: string
  date_creation?: string
  derniere_connexion?: string
  niveau_acces?: string
  portee_donnees?: string
  organisation?: string
  est_actif?: boolean
  marques_autorisees?: string[]
  plages_imei_autorisees?: string[]
  statut_compte: string
  permissions: string[]
  statistiques: {
    nombre_connexions: number
    activites_7_derniers_jours: number
    compte_cree_depuis_jours: number
    derniere_activite?: string
  }
}

export interface PasswordResetRequest {
  email: string
  methode_verification: 'EMAIL' | 'SMS'
  telephone?: string
}

export interface PasswordResetResponse {
  success: boolean
  message: string
  token?: string
  methode_verification?: string
  expires_in_minutes?: number
}

export interface VerifyCodeRequest {
  token: string
  code_verification: string
}

export interface NewPasswordRequest {
  token: string
  nouveau_mot_de_passe: string
  confirmer_mot_de_passe: string
}

// Authentication Service
export class AuthService {
  private static instance: AuthService
  private baseUrl = '/authentification'

  private constructor() {}

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService()
    }
    return AuthService.instance
  }

  /**
   * User login
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>(
        `${this.baseUrl}/connexion`,
        credentials
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * User registration
   */
  async register(userData: RegisterRequest): Promise<RegisterResponse> {
    try {
      const response = await apiClient.post<RegisterResponse>(
        `${this.baseUrl}/inscription`,
        userData
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * Get user profile (requires authentication)
   */
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await apiClient.get<UserProfile>(
        `${this.baseUrl}/profile`
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * Get simple user profile (requires authentication)
   */
  async getSimpleProfile(): Promise<RegisterResponse> {
    try {
      const response = await apiClient.get<RegisterResponse>(
        `${this.baseUrl}/profile/simple`
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * User logout (requires authentication)
   */
  async logout(): Promise<{ message: string }> {
    try {
      const response = await apiClient.post<{ message: string }>(
        `${this.baseUrl}/deconnexion`
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<PasswordResetResponse> {
    try {
      const response = await apiClient.post<PasswordResetResponse>(
        `${this.baseUrl}/mot-de-passe-oublie`,
        data
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * Verify reset code
   */
  async verifyResetCode(data: VerifyCodeRequest): Promise<PasswordResetResponse> {
    try {
      const response = await apiClient.post<PasswordResetResponse>(
        `${this.baseUrl}/verifier-code-reset`,
        data
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * Set new password
   */
  async setNewPassword(data: NewPasswordRequest): Promise<PasswordResetResponse> {
    try {
      const response = await apiClient.post<PasswordResetResponse>(
        `${this.baseUrl}/nouveau-mot-de-passe`,
        data
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false
    const token = localStorage.getItem('auth_token')
    return !!token
  }

  /**
   * Get stored auth token
   */
  getAuthToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('auth_token')
  }

  /**
   * Clear authentication data
   */
  clearAuth(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem('auth_token', token)
  }

  /**
   * Set user data
   */
  setUserData(userData: UserProfile): void {
    if (typeof window === 'undefined') return
    localStorage.setItem('user_data', JSON.stringify(userData))
  }

  /**
   * Get stored user data
   */
  getUserData(): UserProfile | null {
    if (typeof window === 'undefined') return null
    const userData = localStorage.getItem('user_data')
    if (!userData) return null
    try {
      return JSON.parse(userData)
    } catch {
      return null
    }
  }
}

// Export singleton instance
export const authService = AuthService.getInstance()
export default authService 