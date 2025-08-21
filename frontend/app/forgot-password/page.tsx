'use client'
import { PasswordResetForm } from '../../src/components/PasswordResetForm'
import { useAuth } from '../../src/contexts/AuthContext'


export default function ForgotPasswordPage() {

    const { user, isLoading: isAuthLoading } = useAuth()
    if(!isAuthLoading && user) {
      // If user is already authenticated, redirect to home page
      if (typeof window !== 'undefined') {
        window.location.href = '/'
      }
      return null
    }

  return <PasswordResetForm />
}
