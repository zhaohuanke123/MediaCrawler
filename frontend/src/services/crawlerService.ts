import { apiClient } from './api'
import { CrawlerConfig, Platform, CrawlerType } from '@/types'

export interface StartCrawlerRequest {
  platform: Platform
  type: CrawlerType
  config: {
    keyword?: string
    pages?: number
    sort?: string
    filters?: Record<string, any>
  }
  crawlerOptions?: {
    headless?: boolean
    timeout?: number
    proxy?: string
    useCache?: boolean
  }
}

export interface PlatformListResponse {
  platforms: Array<{
    id: string
    name: string
    displayName: string
    supported: boolean
  }>
}

// Start crawler task
export const startCrawler = async (config: StartCrawlerRequest) => {
  const response = await apiClient.post('/crawler/start', config)
  return response.data
}

// Pause crawler task
export const pauseCrawler = async (taskId: string) => {
  const response = await apiClient.post(`/crawler/pause/${taskId}`)
  return response.data
}

// Resume crawler task
export const resumeCrawler = async (taskId: string) => {
  const response = await apiClient.post(`/crawler/resume/${taskId}`)
  return response.data
}

// Cancel crawler task
export const cancelCrawler = async (taskId: string) => {
  const response = await apiClient.post(`/crawler/cancel/${taskId}`)
  return response.data
}

// Get supported platforms
export const getPlatforms = async () => {
  const response = await apiClient.get<PlatformListResponse>('/crawler/platforms')
  return response.data
}

// Get crawler configuration
export const getCrawlerConfig = async () => {
  const response = await apiClient.get('/crawler/config')
  return response.data
}

// Update crawler configuration
export const updateCrawlerConfig = async (config: Partial<CrawlerConfig>) => {
  const response = await apiClient.put('/crawler/config', config)
  return response.data
}

export default {
  startCrawler,
  pauseCrawler,
  resumeCrawler,
  cancelCrawler,
  getPlatforms,
  getCrawlerConfig,
  updateCrawlerConfig,
}
