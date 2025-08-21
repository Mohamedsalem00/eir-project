'use client'
import { useAuth } from '@/contexts/AuthContext'
import { RegisterForm } from '../../src/components/RegisterForm'

export default function RegisterPage() {

    const { user, isLoading: isAuthLoading } = useAuth()
    if(!isAuthLoading && user) {
      // If user is already authenticated, redirect to home page
      if (typeof window !== 'undefined') {
        window.location.href = '/'
      }
      return null
    }
  return <RegisterForm />
}
