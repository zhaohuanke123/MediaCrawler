// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws'

// Pagination
export const DEFAULT_PAGE_SIZE = 20
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

// Task polling interval (ms)
export const TASK_POLL_INTERVAL = 2000

// Chart colors
export const CHART_COLORS = {
  primary: '#1890ff',
  success: '#52c41a',
  warning: '#faad14',
  error: '#f5222d',
  info: '#13c2c2',
  purple: '#722ed1',
  cyan: '#13c2c2',
  orange: '#fa8c16',
}

// Platform colors
export const PLATFORM_COLORS: Record<string, string> = {
  xiaohongshu: '#ff2442',
  douyin: '#000000',
  kuaishou: '#ff6600',
  bilibili: '#00a1d6',
  weibo: '#e6162d',
  tieba: '#2468f2',
  zhihu: '#0084ff',
}

// Date format
export const DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'
export const DATE_FORMAT_SHORT = 'YYYY-MM-DD'

// Local storage keys
export const STORAGE_KEYS = {
  THEME: 'mediacrawler_theme',
  LANGUAGE: 'mediacrawler_language',
  CRAWLER_CONFIG: 'mediacrawler_crawler_config',
  TABLE_SETTINGS: 'mediacrawler_table_settings',
}

// Max file upload size (MB)
export const MAX_FILE_SIZE = 10

// Request timeout (ms)
export const REQUEST_TIMEOUT = 30000

// Crawler limits
export const CRAWLER_LIMITS = {
  MIN_LIMIT: 1,
  MAX_LIMIT: 1000,
  DEFAULT_LIMIT: 50,
}

// Export types
export const EXPORT_FORMATS = ['json', 'csv', 'excel'] as const
export type ExportFormat = typeof EXPORT_FORMATS[number]
