import { apiClient } from './api'
import { Task, TaskStatistics, TaskProgress, CreateTaskRequest, PaginationParams } from '@/types'

// Get task list
export const getTasks = async (params?: PaginationParams & { status?: string }) => {
  const response = await apiClient.get('/crawler/tasks', { params })
  return response.data
}

// Get task by ID
export const getTask = async (taskId: string) => {
  const response = await apiClient.get<Task>(`/crawler/task/${taskId}`)
  return response.data
}

// Create new task
export const createTask = async (request: CreateTaskRequest) => {
  const response = await apiClient.post<Task>('/crawler/tasks', request)
  return response.data
}

// Delete task
export const deleteTask = async (taskId: string) => {
  const response = await apiClient.delete(`/crawler/task/${taskId}`)
  return response.data
}

// Get task progress
export const getTaskProgress = async (taskId: string) => {
  const response = await apiClient.get<TaskProgress>(`/crawler/progress/${taskId}`)
  return response.data
}

// Get task logs
export const getTaskLogs = async (taskId: string, params?: { limit?: number; offset?: number }) => {
  const response = await apiClient.get(`/crawler/task/${taskId}/logs`, { params })
  return response.data
}

// Get task statistics
export const getTaskStatistics = async () => {
  const response = await apiClient.get<TaskStatistics>('/crawler/tasks/statistics')
  return response.data
}

// Batch delete tasks
export const batchDeleteTasks = async (taskIds: string[]) => {
  const response = await apiClient.post('/crawler/tasks/batch-delete', { taskIds })
  return response.data
}

export default {
  getTasks,
  getTask,
  createTask,
  deleteTask,
  getTaskProgress,
  getTaskLogs,
  getTaskStatistics,
  batchDeleteTasks,
}
