import { Platform, CrawlerType, TaskStatus } from './common'
import { CrawlerConfig } from './crawler'

export interface Task {
  id: string
  name: string
  platform: Platform
  crawlerType: CrawlerType
  status: TaskStatus
  config: CrawlerConfig
  progress: TaskProgress
  createdAt: string
  startedAt?: string
  completedAt?: string
  errorMessage?: string
  logs?: TaskLog[]
}

export interface TaskProgress {
  current: number
  total: number
  percentage: number
  speed?: number // items per second
  eta?: number // estimated time remaining in seconds
}

export interface TaskLog {
  timestamp: string
  level: 'info' | 'warning' | 'error' | 'success'
  message: string
}

export interface TaskStatistics {
  totalTasks: number
  runningTasks: number
  completedTasks: number
  failedTasks: number
  pendingTasks: number
}

export interface CreateTaskRequest {
  name: string
  platform: Platform
  crawlerType: CrawlerType
  config: CrawlerConfig
}

export interface TaskActionRequest {
  action: 'start' | 'pause' | 'resume' | 'cancel'
}

// WebSocket event types
export interface WebSocketEvent {
  type: 'task_started' | 'task_progress' | 'task_completed' | 'task_error' | 'task_log'
  taskId: string
  data: any
  timestamp: string
}

export interface TaskProgressEvent extends WebSocketEvent {
  type: 'task_progress'
  data: TaskProgress
}

export interface TaskLogEvent extends WebSocketEvent {
  type: 'task_log'
  data: TaskLog
}
