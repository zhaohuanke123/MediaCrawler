import { Platform } from '@/types'
import { PLATFORM_INFO } from '@/types/crawler'

// Get platform display name
export const getPlatformDisplayName = (platform: Platform): string => {
  return PLATFORM_INFO[platform]?.displayName || platform
}

// Get platform icon
export const getPlatformIcon = (platform: Platform): string => {
  return PLATFORM_INFO[platform]?.icon || '📱'
}

// Get platform color
export const getPlatformColor = (platform: Platform): string => {
  const colors: Record<Platform, string> = {
    xiaohongshu: '#ff2442',
    douyin: '#000000',
    kuaishou: '#ff6600',
    bilibili: '#00a1d6',
    weibo: '#e6162d',
    tieba: '#2468f2',
    zhihu: '#0084ff',
  }
  return colors[platform] || '#1890ff'
}

// Get all platforms
export const getAllPlatforms = (): Platform[] => {
  return Object.keys(PLATFORM_INFO) as Platform[]
}

// Check if platform supports crawler type
export const isPlatformSupportType = (platform: Platform, type: string): boolean => {
  return PLATFORM_INFO[platform]?.supportedTypes.includes(type as any) || false
}

// Get supported types for platform
export const getSupportedTypes = (platform: Platform): string[] => {
  return PLATFORM_INFO[platform]?.supportedTypes || []
}

// Get platform name for API
export const getPlatformApiName = (platform: Platform): string => {
  return PLATFORM_INFO[platform]?.name || platform
}

// Parse platform from API name
export const parsePlatformFromApiName = (apiName: string): Platform | null => {
  const entry = Object.entries(PLATFORM_INFO).find(([_, info]) => info.name === apiName)
  return entry ? (entry[0] as Platform) : null
}

// Get platform description
export const getPlatformDescription = (platform: Platform): string => {
  return PLATFORM_INFO[platform]?.description || ''
}
