// Export all API services
export { authService, AuthService } from './auth'
export { default as IMEIService } from './imei'
export { default as TACService } from './tac'
export { default as PublicService } from './public'

// Export types
export type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  UserProfile,
  PasswordResetRequest,
  PasswordResetResponse,
  VerifyCodeRequest,
  NewPasswordRequest
} from './auth'

export type {
  IMEIResponse,
  IMEIDetailsResponse,
  PublicStatsResponse,
  TACResponse,
  ErrorResponse,
  RateLimitInfo,
  HealthResponse,
  SearchIMEIRequest,
  SearchTACRequest,
  ApiResponse
} from '../types/api'

// Re-export utilities
export { apiClient } from '../lib/api-client'
export { handleApiError, ApiError } from '../lib/api-error'
