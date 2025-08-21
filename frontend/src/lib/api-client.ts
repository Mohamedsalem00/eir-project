import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { useLanguage } from '../contexts/LanguageContext'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const timeout = process.env.NEXT_PUBLIC_API_TIMEOUT ? parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT, 10) : 30000
    console.log('🔧 API Client initialized with baseURL:', baseURL, 'timeout:', timeout)

    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json'
        // Accept-Language will be set dynamically per request
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Set Accept-Language header from localStorage (set by LanguageContext)
        if (typeof window !== 'undefined') {
          const lang = localStorage.getItem('eir-language') || 'fr'
          config.headers['Accept-Language'] = lang
        }

        if (process.env.NODE_ENV === 'development') {
          console.log('🚀 API Request:', config.method?.toUpperCase(), config.url, 'Accept-Language:', config.headers['Accept-Language'])
        }
        
        return config
      },
      (error) => {
        console.error('❌ Request Error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        if (process.env.NODE_ENV === 'development') {
          console.log('✅ API Response:', response.status, response.config.url)
        }
        return response
      },
      (error) => {
        if (process.env.NODE_ENV === 'development') {
          console.error('❌ API Error:', error.response?.status, error.config?.url)
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: any): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config)
  }

  async post<T>(url: string, data?: any, config?: any): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config)
  }

  async put<T>(url: string, data?: any, config?: any): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config)
  }

  async delete<T>(url: string, config?: any): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config)
  }
}

export const apiClient = new ApiClient()
export default apiClient
