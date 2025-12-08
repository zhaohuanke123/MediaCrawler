import { apiClient } from './api'

export interface StatisticsSummary {
  totalResults: number
  totalTasks: number
  totalComments: number
  platformDistribution: Record<string, number>
  typeDistribution: Record<string, number>
}

export interface PlatformStatistics {
  platform: string
  count: number
  percentage: number
  avgLikes: number
  avgComments: number
}

export interface TimelineStatistics {
  date: string
  count: number
  likes: number
  comments: number
}

export interface KeywordStatistics {
  keyword: string
  count: number
  weight: number
}

// Get statistics summary
export const getStatisticsSummary = async () => {
  const response = await apiClient.get<StatisticsSummary>('/statistics/summary')
  return response.data
}

// Get statistics by platform
export const getPlatformStatistics = async () => {
  const response = await apiClient.get<PlatformStatistics[]>('/statistics/platform')
  return response.data
}

// Get timeline statistics
export const getTimelineStatistics = async (params?: { startDate?: string; endDate?: string; granularity?: 'day' | 'week' | 'month' }) => {
  const response = await apiClient.get<TimelineStatistics[]>('/statistics/timeline', { params })
  return response.data
}

// Get keyword statistics (word cloud data)
export const getKeywordStatistics = async (params?: { limit?: number; minCount?: number }) => {
  const response = await apiClient.get<KeywordStatistics[]>('/statistics/keywords', { params })
  return response.data
}

// Get top authors
export const getTopAuthors = async (params?: { limit?: number; platform?: string }) => {
  const response = await apiClient.get('/statistics/top-authors', { params })
  return response.data
}

// Get engagement statistics
export const getEngagementStatistics = async (params?: { platform?: string; startDate?: string; endDate?: string }) => {
  const response = await apiClient.get('/statistics/engagement', { params })
  return response.data
}

export default {
  getStatisticsSummary,
  getPlatformStatistics,
  getTimelineStatistics,
  getKeywordStatistics,
  getTopAuthors,
  getEngagementStatistics,
}
