import React, { useEffect, useState } from 'react'
import { Table, Card, Button, Space, Tag, Input, Select, message } from 'antd'
import { DownloadOutlined, DeleteOutlined } from '@ant-design/icons'
import { useResultStore } from '@/store'
import { getResults, exportResults, batchDeleteResults } from '@/services/resultService'
import { formatNumber, formatDate } from '@/utils/formatters'
import { getPlatformDisplayName } from '@/utils/platform'
import { Result } from '@/types'

const { Search } = Input
const { Option } = Select

const Results: React.FC = () => {
  const {
    results,
    selectedResults,
    total,
    page,
    pageSize,
    loading,
    setResults,
    setSelectedResults,
    setTotal,
    setPage,
    setPageSize,
    setLoading,
  } = useResultStore()

  const [keyword, setKeyword] = useState('')
  const [platformFilter, setPlatformFilter] = useState<string>()

  useEffect(() => {
    loadResults()
  }, [page, pageSize, platformFilter])

  const loadResults = async () => {
    setLoading(true)
    try {
      const response = await getResults({
        page,
        pageSize,
        platform: platformFilter as any,
        keyword,
      })
      
      if (response.data) {
        setResults(response.data.items || [])
        setTotal(response.data.total || 0)
      }
    } catch (error) {
      console.error('Failed to load results:', error)
      message.error('加载结果失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(1)
    loadResults()
  }

  const handleExport = async () => {
    try {
      const response = await exportResults({ format: 'json' })
      // response is already a blob from the API service
      const blob = response as unknown as Blob
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `results_${Date.now()}.json`
      link.click()
      message.success('导出成功')
    } catch (error) {
      console.error('Failed to export:', error)
      message.error('导出失败')
    }
  }

  const handleDelete = async () => {
    if (selectedResults.length === 0) {
      message.warning('请先选择要删除的结果')
      return
    }

    try {
      await batchDeleteResults(selectedResults)
      message.success('删除成功')
      setSelectedResults([])
      loadResults()
    } catch (error) {
      console.error('Failed to delete:', error)
      message.error('删除失败')
    }
  }

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: 300,
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      width: 100,
      render: (platform: string) => (
        <Tag color="blue">{getPlatformDisplayName(platform as any)}</Tag>
      ),
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120,
    },
    {
      title: '点赞',
      dataIndex: 'likes',
      key: 'likes',
      width: 80,
      render: (likes: number) => formatNumber(likes),
      sorter: (a: Result, b: Result) => a.likes - b.likes,
    },
    {
      title: '评论',
      dataIndex: 'comments',
      key: 'comments',
      width: 80,
      render: (comments: number) => formatNumber(comments),
      sorter: (a: Result, b: Result) => a.comments - b.comments,
    },
    {
      title: '分享',
      dataIndex: 'shares',
      key: 'shares',
      width: 80,
      render: (shares: number) => formatNumber(shares),
    },
    {
      title: '爬取时间',
      dataIndex: 'crawledAt',
      key: 'crawledAt',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: Result) => (
        <Space>
          <Button type="link" size="small" href={record.url} target="_blank">
            查看
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>结果展示</h1>

      <Card>
        <Space style={{ marginBottom: 16, width: '100%' }} direction="vertical">
          <Space>
            <Search
              placeholder="搜索关键词"
              value={keyword}
              onChange={e => setKeyword(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 300 }}
              enterButton
            />
            <Select
              placeholder="选择平台"
              style={{ width: 150 }}
              value={platformFilter}
              onChange={setPlatformFilter}
              allowClear
            >
              <Option value="xiaohongshu">小红书</Option>
              <Option value="douyin">抖音</Option>
              <Option value="kuaishou">快手</Option>
              <Option value="bilibili">B站</Option>
              <Option value="weibo">微博</Option>
              <Option value="tieba">贴吧</Option>
              <Option value="zhihu">知乎</Option>
            </Select>
          </Space>

          <Space>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              导出
            </Button>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleDelete}
              disabled={selectedResults.length === 0}
            >
              删除选中 ({selectedResults.length})
            </Button>
          </Space>
        </Space>

        <Table
          columns={columns}
          dataSource={results}
          rowKey="id"
          loading={loading}
          rowSelection={{
            selectedRowKeys: selectedResults,
            onChange: (keys) => setSelectedResults(keys as string[]),
          }}
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPage(page)
              setPageSize(pageSize)
            },
          }}
        />
      </Card>
    </div>
  )
}

export default Results
