import { apiClient } from './api'
import { Result, ResultDetail, ResultsFilter, PaginationParams, Comment } from '@/types'

// Get results list
export const getResults = async (params?: PaginationParams & ResultsFilter) => {
  const response = await apiClient.get('/results', { params })
  return response.data
}

// Get result by ID
export const getResult = async (id: string) => {
  const response = await apiClient.get<ResultDetail>(`/results/${id}`)
  return response.data
}

// Delete result
export const deleteResult = async (id: string) => {
  const response = await apiClient.delete(`/results/${id}`)
  return response.data
}

// Batch delete results
export const batchDeleteResults = async (ids: string[]) => {
  const response = await apiClient.post('/results/batch-delete', { ids })
  return response.data
}

// Export results
export const exportResults = async (params?: ResultsFilter & { format?: 'json' | 'csv' | 'excel' }) => {
  const response = await apiClient.get('/results/export', {
    params,
    responseType: 'blob',
  })
  return response.data
}

// Get comments for a result
export const getComments = async (resultId: string, params?: PaginationParams) => {
  const response = await apiClient.get<Comment[]>(`/results/${resultId}/comments`, { params })
  return response.data
}

// Search results
export const searchResults = async (query: string, params?: PaginationParams) => {
  const response = await apiClient.get('/results/search', {
    params: { q: query, ...params },
  })
  return response.data
}

export default {
  getResults,
  getResult,
  deleteResult,
  batchDeleteResults,
  exportResults,
  getComments,
  searchResults,
}
