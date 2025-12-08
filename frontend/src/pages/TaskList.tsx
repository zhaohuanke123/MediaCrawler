import React, { useEffect } from 'react'
import { Table, Card, Button, Space, Tag, Progress, message } from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  CloseCircleOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import { useTaskStore } from '@/store'
import { getTasks, deleteTask } from '@/services/taskService'
import { pauseCrawler, resumeCrawler, cancelCrawler } from '@/services/crawlerService'
import { formatDate, formatTaskStatus } from '@/utils/formatters'
import { Task, TaskStatus } from '@/types'

const TaskList: React.FC = () => {
  const { tasks, loading, setTasks, setLoading, removeTask } = useTaskStore()

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    setLoading(true)
    try {
      const response = await getTasks()
      if (response.data) {
        setTasks(response.data.items || [])
      }
    } catch (error) {
      console.error('Failed to load tasks:', error)
      message.error('加载任务列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handlePause = async (taskId: string) => {
    try {
      await pauseCrawler(taskId)
      message.success('任务已暂停')
      loadTasks()
    } catch (error) {
      message.error('暂停任务失败')
    }
  }

  const handleResume = async (taskId: string) => {
    try {
      await resumeCrawler(taskId)
      message.success('任务已恢复')
      loadTasks()
    } catch (error) {
      message.error('恢复任务失败')
    }
  }

  const handleCancel = async (taskId: string) => {
    try {
      await cancelCrawler(taskId)
      message.success('任务已取消')
      loadTasks()
    } catch (error) {
      message.error('取消任务失败')
    }
  }

  const handleDelete = async (taskId: string) => {
    try {
      await deleteTask(taskId)
      message.success('任务已删除')
      removeTask(taskId)
    } catch (error) {
      message.error('删除任务失败')
    }
  }

  const getStatusColor = (status: TaskStatus): string => {
    const colors: Record<TaskStatus, string> = {
      pending: 'default',
      running: 'processing',
      paused: 'warning',
      completed: 'success',
      failed: 'error',
      cancelled: 'default',
    }
    return colors[status] || 'default'
  }

  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      width: 100,
      render: (platform: string) => <Tag color="blue">{platform}</Tag>,
    },
    {
      title: '类型',
      dataIndex: 'crawlerType',
      key: 'crawlerType',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: TaskStatus) => (
        <Tag color={getStatusColor(status)}>{formatTaskStatus(status)}</Tag>
      ),
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 200,
      render: (progress: any) => (
        <Progress
          percent={progress?.percentage || 0}
          size="small"
          status={progress?.percentage === 100 ? 'success' : 'active'}
        />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: any, record: Task) => (
        <Space size="small">
          {record.status === 'running' && (
            <Button
              type="link"
              size="small"
              icon={<PauseCircleOutlined />}
              onClick={() => handlePause(record.id)}
            >
              暂停
            </Button>
          )}
          {record.status === 'paused' && (
            <Button
              type="link"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => handleResume(record.id)}
            >
              继续
            </Button>
          )}
          {(record.status === 'running' || record.status === 'paused') && (
            <Button
              type="link"
              size="small"
              danger
              icon={<CloseCircleOutlined />}
              onClick={() => handleCancel(record.id)}
            >
              取消
            </Button>
          )}
          {(record.status === 'completed' || record.status === 'failed' || record.status === 'cancelled') && (
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id)}
            >
              删除
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>任务列表</h1>

      <Card>
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
    </div>
  )
}

export default TaskList
