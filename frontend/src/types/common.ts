// Common types used across the application

export type Platform = 'xiaohongshu' | 'douyin' | 'kuaishou' | 'bilibili' | 'weibo' | 'tieba' | 'zhihu'

export type CrawlerType = 'video' | 'note' | 'comment' | 'search' | 'detail' | 'creator'

export type TaskStatus = 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'

export type Priority = 'low' | 'medium' | 'high'

export type SortOrder = 'asc' | 'desc'

export interface PaginationParams {
  page: number
  pageSize: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface FilterOptions {
  minLikes?: number
  maxLikes?: number
  minComments?: number
  maxComments?: number
  startDate?: string
  endDate?: string
  hasVideo?: boolean
  hasImage?: boolean
}
