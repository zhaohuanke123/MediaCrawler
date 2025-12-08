import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import duration from 'dayjs/plugin/duration'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.extend(duration)
dayjs.locale('zh-cn')

// Format number with K, M, B suffixes
export const formatNumber = (num: number): string => {
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1) + 'B'
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// Format percentage
export const formatPercentage = (value: number, total: number): string => {
  if (total === 0) return '0%'
  return ((value / total) * 100).toFixed(1) + '%'
}

// Format file size
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Format date
export const formatDate = (date: string | Date, format = 'YYYY-MM-DD HH:mm:ss'): string => {
  return dayjs(date).format(format)
}

// Format relative time
export const formatRelativeTime = (date: string | Date): string => {
  return dayjs(date).fromNow()
}

// Format duration (seconds to human readable)
export const formatDuration = (seconds: number): string => {
  const dur = dayjs.duration(seconds, 'seconds')
  const hours = Math.floor(dur.asHours())
  const minutes = dur.minutes()
  const secs = dur.seconds()

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`
  }
  return `${secs}s`
}

// Format ETA (estimated time of arrival)
export const formatETA = (seconds: number): string => {
  if (seconds < 60) return `${Math.round(seconds)}秒`
  if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
  return `${Math.round(seconds / 3600)}小时`
}

// Truncate text
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

// Format URL
export const formatUrl = (url: string): string => {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname + urlObj.pathname
  } catch {
    return url
  }
}

// Format platform name
export const formatPlatformName = (platform: string): string => {
  const platformMap: Record<string, string> = {
    xiaohongshu: '小红书',
    douyin: '抖音',
    kuaishou: '快手',
    bilibili: 'B站',
    weibo: '微博',
    tieba: '百度贴吧',
    zhihu: '知乎',
  }
  return platformMap[platform] || platform
}

// Format task status
export const formatTaskStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return statusMap[status] || status
}

// Format crawler type
export const formatCrawlerType = (type: string): string => {
  const typeMap: Record<string, string> = {
    search: '关键词搜索',
    detail: '帖子详情',
    creator: '创作者主页',
    video: '视频',
    note: '笔记',
    comment: '评论',
  }
  return typeMap[type] || type
}
