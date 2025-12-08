import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Platform, CrawlerType, Priority, FilterOptions, Task, Result } from '@/types'

// Crawler State
interface CrawlerState {
  platforms: Platform[]
  selectedPlatforms: Platform[]
  keywords: string
  crawlerType: CrawlerType
  limit: number
  priority: Priority
  filters: FilterOptions
  enableProxy: boolean
  enableComments: boolean
  loading: boolean
  error: string | null
  setSelectedPlatforms: (platforms: Platform[]) => void
  setKeywords: (keywords: string) => void
  setCrawlerType: (type: CrawlerType) => void
  setLimit: (limit: number) => void
  setPriority: (priority: Priority) => void
  setFilters: (filters: FilterOptions) => void
  setEnableProxy: (enabled: boolean) => void
  setEnableComments: (enabled: boolean) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  resetConfig: () => void
}

// Result State
interface ResultState {
  results: Result[]
  selectedResults: string[]
  total: number
  page: number
  pageSize: number
  filters: Record<string, any>
  sorting: { field: string; order: 'asc' | 'desc' }
  loading: boolean
  error: string | null
  setResults: (results: Result[]) => void
  setSelectedResults: (ids: string[]) => void
  setTotal: (total: number) => void
  setPage: (page: number) => void
  setPageSize: (pageSize: number) => void
  setFilters: (filters: Record<string, any>) => void
  setSorting: (field: string, order: 'asc' | 'desc') => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearSelection: () => void
}

// Task State
interface TaskState {
  tasks: Task[]
  activeTaskId: string | null
  taskProgress: Record<string, { current: number; total: number; percentage: number }>
  loading: boolean
  error: string | null
  setTasks: (tasks: Task[]) => void
  addTask: (task: Task) => void
  updateTask: (taskId: string, updates: Partial<Task>) => void
  removeTask: (taskId: string) => void
  setActiveTaskId: (taskId: string | null) => void
  updateTaskProgress: (taskId: string, progress: { current: number; total: number; percentage: number }) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

// UI State
interface UIState {
  sidebarCollapsed: boolean
  theme: 'light' | 'dark'
  modalVisible: boolean
  modalContent: any
  notifications: Array<{ id: string; type: 'success' | 'error' | 'warning' | 'info'; message: string }>
  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
  showModal: (content: any) => void
  hideModal: () => void
  addNotification: (notification: { type: 'success' | 'error' | 'warning' | 'info'; message: string }) => void
  removeNotification: (id: string) => void
}

// Default values
const defaultCrawlerState = {
  platforms: ['xiaohongshu', 'douyin', 'kuaishou', 'bilibili', 'weibo', 'tieba', 'zhihu'] as Platform[],
  selectedPlatforms: [] as Platform[],
  keywords: '',
  crawlerType: 'search' as CrawlerType,
  limit: 50,
  priority: 'medium' as Priority,
  filters: {},
  enableProxy: false,
  enableComments: false,
  loading: false,
  error: null,
}

// Create stores
export const useCrawlerStore = create<CrawlerState>()(
  devtools(
    (set) => ({
      ...defaultCrawlerState,
      setSelectedPlatforms: (platforms) => set({ selectedPlatforms: platforms }),
      setKeywords: (keywords) => set({ keywords }),
      setCrawlerType: (type) => set({ crawlerType: type }),
      setLimit: (limit) => set({ limit }),
      setPriority: (priority) => set({ priority }),
      setFilters: (filters) => set({ filters }),
      setEnableProxy: (enabled) => set({ enableProxy: enabled }),
      setEnableComments: (enabled) => set({ enableComments: enabled }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      resetConfig: () => set(defaultCrawlerState),
    }),
    { name: 'crawler-store' }
  )
)

export const useResultStore = create<ResultState>()(
  devtools(
    (set) => ({
      results: [],
      selectedResults: [],
      total: 0,
      page: 1,
      pageSize: 20,
      filters: {},
      sorting: { field: 'crawledAt', order: 'desc' },
      loading: false,
      error: null,
      setResults: (results) => set({ results }),
      setSelectedResults: (ids) => set({ selectedResults: ids }),
      setTotal: (total) => set({ total }),
      setPage: (page) => set({ page }),
      setPageSize: (pageSize) => set({ pageSize }),
      setFilters: (filters) => set({ filters }),
      setSorting: (field, order) => set({ sorting: { field, order } }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      clearSelection: () => set({ selectedResults: [] }),
    }),
    { name: 'result-store' }
  )
)

export const useTaskStore = create<TaskState>()(
  devtools(
    (set) => ({
      tasks: [],
      activeTaskId: null,
      taskProgress: {},
      loading: false,
      error: null,
      setTasks: (tasks) => set({ tasks }),
      addTask: (task) => set((state) => ({ tasks: [...state.tasks, task] })),
      updateTask: (taskId, updates) =>
        set((state) => ({
          tasks: state.tasks.map((task) => (task.id === taskId ? { ...task, ...updates } : task)),
        })),
      removeTask: (taskId) =>
        set((state) => ({
          tasks: state.tasks.filter((task) => task.id !== taskId),
        })),
      setActiveTaskId: (taskId) => set({ activeTaskId: taskId }),
      updateTaskProgress: (taskId, progress) =>
        set((state) => ({
          taskProgress: { ...state.taskProgress, [taskId]: progress },
        })),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
    }),
    { name: 'task-store' }
  )
)

export const useUIStore = create<UIState>()(
  devtools(
    (set) => ({
      sidebarCollapsed: false,
      theme: 'light',
      modalVisible: false,
      modalContent: null,
      notifications: [],
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setTheme: (theme) => set({ theme }),
      showModal: (content) => set({ modalVisible: true, modalContent: content }),
      hideModal: () => set({ modalVisible: false, modalContent: null }),
      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            ...state.notifications,
            { ...notification, id: `${Date.now()}-${Math.random()}` },
          ],
        })),
      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),
    }),
    { name: 'ui-store' }
  )
)
