import { Platform, CrawlerType, Priority, FilterOptions } from './common'

export interface CrawlerConfig {
  platforms: Platform[]
  keywords: string
  crawlerType: CrawlerType
  limit: number
  filters: FilterOptions
  priority: Priority
  enableProxy?: boolean
  enableComments?: boolean
}

export interface PlatformInfo {
  id: Platform
  name: string
  displayName: string
  description: string
  icon: string
  supportedTypes: CrawlerType[]
}

export const PLATFORM_INFO: Record<Platform, PlatformInfo> = {
  xiaohongshu: {
    id: 'xiaohongshu',
    name: 'xhs',
    displayName: '小红书',
    description: '小红书平台内容爬取',
    icon: '📕',
    supportedTypes: ['search', 'detail', 'creator', 'note', 'comment'],
  },
  douyin: {
    id: 'douyin',
    name: 'dy',
    displayName: '抖音',
    description: '抖音短视频平台爬取',
    icon: '🎵',
    supportedTypes: ['search', 'detail', 'creator', 'video', 'comment'],
  },
  kuaishou: {
    id: 'kuaishou',
    name: 'ks',
    displayName: '快手',
    description: '快手短视频平台爬取',
    icon: '⚡',
    supportedTypes: ['search', 'detail', 'creator', 'video', 'comment'],
  },
  bilibili: {
    id: 'bilibili',
    name: 'bili',
    displayName: 'B站',
    description: 'B站视频平台爬取',
    icon: '📺',
    supportedTypes: ['search', 'detail', 'creator', 'video', 'comment'],
  },
  weibo: {
    id: 'weibo',
    name: 'wb',
    displayName: '微博',
    description: '微博社交平台爬取',
    icon: '🔥',
    supportedTypes: ['search', 'detail', 'creator', 'comment'],
  },
  tieba: {
    id: 'tieba',
    name: 'tieba',
    displayName: '百度贴吧',
    description: '百度贴吧内容爬取',
    icon: '💬',
    supportedTypes: ['search', 'detail', 'comment'],
  },
  zhihu: {
    id: 'zhihu',
    name: 'zhihu',
    displayName: '知乎',
    description: '知乎问答平台爬取',
    icon: '🎓',
    supportedTypes: ['search', 'detail', 'creator', 'comment'],
  },
}
