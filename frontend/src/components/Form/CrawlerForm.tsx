import React, { useState } from 'react'
import { Form, Input, InputNumber, Select, Switch, Button, Space, Card, message } from 'antd'
import { ThunderboltOutlined } from '@ant-design/icons'
import PlatformSelector from './PlatformSelector'
import { useCrawlerStore } from '@/store'
import { startCrawler } from '@/services/crawlerService'
import { CrawlerType, Platform } from '@/types'

const { Option } = Select
const { TextArea } = Input

const CrawlerForm: React.FC = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const { setLoading: setStoreLoading } = useCrawlerStore()

  const crawlerTypes: { value: CrawlerType; label: string }[] = [
    { value: 'search', label: '关键词搜索' },
    { value: 'detail', label: '帖子详情' },
    { value: 'creator', label: '创作者主页' },
  ]

  interface CrawlerFormValues {
    platforms: Platform[]
    crawlerType: CrawlerType
    keywords: string
    limit: number
    enableProxy: boolean
    enableComments: boolean
  }

  const handleSubmit = async (values: CrawlerFormValues) => {
    if (!values.platforms || values.platforms.length === 0) {
      message.error('请至少选择一个平台')
      return
    }

    if (!values.keywords || values.keywords.trim() === '') {
      message.error('请输入关键词')
      return
    }

    setLoading(true)
    setStoreLoading(true)

    try {
      // For now, only using the first selected platform
      // In a real implementation, you might want to create multiple tasks
      const platform = values.platforms[0]
      
      await startCrawler({
        platform,
        crawlerType: values.crawlerType,
        keywords: values.keywords,
        limit: values.limit,
        enableProxy: values.enableProxy,
        enableComments: values.enableComments,
      })

      message.success('爬虫任务已启动！')
    } catch (error) {
      console.error('Failed to start crawler:', error)
      message.error('启动爬虫失败，请检查配置后重试')
    } finally {
      setLoading(false)
      setStoreLoading(false)
    }
  }

  return (
    <Card title="爬虫配置" bordered={false}>
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          platforms: [],
          crawlerType: 'search',
          limit: 50,
          enableProxy: false,
          enableComments: true,
        }}
        onFinish={handleSubmit}
      >
        <Form.Item
          label="选择平台"
          name="platforms"
          rules={[{ required: true, message: '请至少选择一个平台' }]}
        >
          <PlatformSelector />
        </Form.Item>

        <Form.Item
          label="爬取类型"
          name="crawlerType"
          rules={[{ required: true, message: '请选择爬取类型' }]}
        >
          <Select>
            {crawlerTypes.map(type => (
              <Option key={type.value} value={type.value}>
                {type.label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="关键词"
          name="keywords"
          rules={[{ required: true, message: '请输入关键词' }]}
          extra="多个关键词请用英文逗号分隔"
        >
          <TextArea
            rows={3}
            placeholder="例如: 编程副业,编程兼职,Python教程"
            showCount
            maxLength={200}
          />
        </Form.Item>

        <Form.Item
          label="爬取数量"
          name="limit"
          rules={[{ required: true, message: '请输入爬取数量' }]}
        >
          <InputNumber min={1} max={1000} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item label="启用代理" name="enableProxy" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Form.Item label="爬取评论" name="enableComments" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<ThunderboltOutlined />}
              loading={loading}
              size="large"
            >
              开始爬取
            </Button>
            <Button htmlType="reset" size="large">
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  )
}

export default CrawlerForm
