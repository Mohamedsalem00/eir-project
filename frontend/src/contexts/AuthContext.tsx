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
    // Check if user is already logged in (from localStorage)
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
      
      // Store token
      authService.setAuthToken(loginResponse.access_token)
      
      // Fetch user profile
      const userProfile = await authService.getProfile()
      setUser(userProfile)
      
      // Store user data
      authService.setUserData(userProfile)
      
      return true
    } catch (err: any) {
      setError(err.message || 'Login failed')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (userData: RegisterData): Promise<boolean> => {
    setIsLoading(true)
    setError(null)
    
    try {
      await authService.register(userData)
      
      // Registration successful, now login
      return await login(userData.email, userData.mot_de_passe)
    } catch (err: any) {
      setError(err.message || 'Registration failed')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      // Call logout API if user is authenticated
      if (authService.isAuthenticated()) {
        await authService.logout()
      }
    } catch (error) {
      // Continue with logout even if API call fails
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
