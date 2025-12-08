import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { API_BASE_URL, REQUEST_TIMEOUT } from '@/utils/constants'
import { ApiResponse } from '@/types'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError) => {
    // Handle common errors
    if (error.response) {
      switch (error.response.status) {
        case 401:
          console.error('Unauthorized access')
          // Redirect to login or refresh token
          break
        case 403:
          console.error('Forbidden access')
          break
        case 404:
          console.error('Resource not found')
          break
        case 500:
          console.error('Internal server error')
          break
        default:
          console.error('Request failed:', error.response.data)
      }
    } else if (error.request) {
      console.error('No response received:', error.request)
    } else {
      console.error('Error setting up request:', error.message)
    }
    return Promise.reject(error)
  }
)

// Generic API methods
export const apiClient = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.get(url, config)
  },

  post: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.post(url, data, config)
  },

  put: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.put(url, data, config)
  },

  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.delete(url, config)
  },

  patch: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.patch(url, data, config)
  },
}

export default api
