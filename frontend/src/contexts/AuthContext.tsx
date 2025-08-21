'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService, LoginRequest, RegisterRequest, UserProfile } from '../api/auth'

type User = UserProfile

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<boolean>
  register: (userData: RegisterData) => Promise<boolean>
  logout: () => void
  isLoading: boolean
  error: string | null
}

type RegisterData = RegisterRequest

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = authService.getAuthToken()
    const userData = authService.getUserData()
    
    if (token && userData) {
      setUser(userData)
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const loginData: LoginRequest = { email, mot_de_passe: password }
      const loginResponse = await authService.login(loginData)

      authService.setAuthToken(loginResponse.access_token)

      const userProfile = await authService.getProfile()
      setUser(userProfile)
      authService.setUserData(userProfile)

      return true
    } catch (err: any) {
      // Handle FastAPI HTTPException with status and detail
      if (err.response && err.response.status === 403 && err.response.data?.detail === 'EMAIL_NON_VERIFIE') {
        setError('EMAIL_NON_VERIFIE');
      } else if (err.message === 'EMAIL_NON_VERIFIE') {
        setError('EMAIL_NON_VERIFIE');
      } else {
        // Fallback to the existing error message for all other cases
        setError(err.message || 'Login failed');
      }
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (userData: RegisterData): Promise<boolean> => {
    setIsLoading(true)
    setError(null)
    
    try {
      // The register API call now just registers the user.
      // It does NOT log them in.
      await authService.register(userData)
      // Return true to signal the form to show the verification notice.
      return true 
    } catch (err: any) {
      setError(err.message || 'Registration failed')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      if (authService.isAuthenticated()) {
        await authService.logout()
      }
    } catch (error) {
      console.warn('Logout API call failed:', error)
    } finally {
      setUser(null)
      authService.clearAuth()
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      login,
      register,
      logout,
      isLoading,
      error
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
