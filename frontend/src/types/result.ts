import { Platform } from './common'

export interface Result {
  id: string
  platform: Platform
  title: string
  content: string
  author: string
  authorAvatar?: string
  authorId?: string
  likes: number
  comments: number
  shares: number
  views?: number
  url: string
  mediaUrls: string[]
  thumbnailUrl?: string
  tags?: string[]
  location?: string
  publishedAt: string
  crawledAt: string
}

export interface Comment {
  id: string
  postId: string
  content: string
  author: string
  authorAvatar?: string
  likes: number
  replies: number
  createdAt: string
  parentId?: string
  subComments?: Comment[]
}

export interface ResultDetail extends Omit<Result, 'comments'> {
  commentCount: number
  commentList?: Comment[]
  statistics?: {
    totalComments: number
    totalLikes: number
    totalShares: number
    totalViews: number
  }
}

export interface ResultsFilter {
  platform?: Platform
  keyword?: string
  minLikes?: number
  maxLikes?: number
  startDate?: string
  endDate?: string
  sortBy?: 'likes' | 'comments' | 'shares' | 'views' | 'publishedAt' | 'crawledAt'
  sortOrder?: 'asc' | 'desc'
}
