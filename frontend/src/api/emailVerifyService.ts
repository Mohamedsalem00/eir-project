import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'

export class EmailVerifyService {
  private static instance: EmailVerifyService
  private baseUrl = '/authentification'

  private constructor() {}

  public static getInstance(): EmailVerifyService {
    if (!EmailVerifyService.instance) {
      EmailVerifyService.instance = new EmailVerifyService()
    }
    return EmailVerifyService.instance
  }

  /**
   * Verifies an email using the provided token.
   * This is called when the user clicks the link in their email.
   */
  async verifyEmail(token: string): Promise<{ message: string }> {
    try {
      const response = await apiClient.get<{ message: string }>(
        `${this.baseUrl}/verify-email`,
        { params: { token } }
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }

  /**
   * Requests a new verification email to be sent.
   * This is called when the user clicks the "Resend" button.
   */
  async resendVerificationEmail(email: string): Promise<{ message: string }> {
    try {
      const response = await apiClient.post<{ message: string }>(
        `${this.baseUrl}/resend-verification-email`,
        { email }
      )
      return response.data
    } catch (error: any) {
      throw handleApiError(error)
    }
  }
}

export const emailVerifyService = EmailVerifyService.getInstance()
