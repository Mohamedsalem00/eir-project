'use client'
import { LoginForm } from '../../src/components/LoginForm'
import { useAuth } from '../../src/contexts/AuthContext'

export default function LoginPage() {

  const { user, isLoading: isAuthLoading } = useAuth()
  if(!isAuthLoading && user) {
    // If user is already authenticated, redirect to home page
    if (typeof window !== 'undefined') {
      window.location.href = '/'
    }
    return null
  }

  return <LoginForm />
}
