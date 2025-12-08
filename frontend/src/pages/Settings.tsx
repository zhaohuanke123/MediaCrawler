import React from 'react'
import { Card, Form, Input, InputNumber, Switch, Button, Space, message } from 'antd'

const Settings: React.FC = () => {
  const [form] = Form.useForm()

  const handleSubmit = (values: any) => {
    console.log('Settings:', values)
    message.success('设置已保存')
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>系统设置</h1>

      <Card title="基础配置">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            apiBaseUrl: '/api/v1',
            defaultPageSize: 20,
            enableProxy: false,
            proxyUrl: '',
            maxRetries: 3,
            timeout: 30000,
          }}
        >
          <Form.Item
            label="API 基础地址"
            name="apiBaseUrl"
            rules={[{ required: true, message: '请输入 API 基础地址' }]}
          >
            <Input placeholder="例如: /api/v1" />
          </Form.Item>

          <Form.Item
            label="默认分页大小"
            name="defaultPageSize"
            rules={[{ required: true, message: '请输入分页大小' }]}
          >
            <InputNumber min={10} max={100} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="启用代理" name="enableProxy" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item
            label="代理地址"
            name="proxyUrl"
            rules={[{ type: 'url', message: '请输入有效的 URL' }]}
          >
            <Input placeholder="例如: http://proxy.example.com:8080" />
          </Form.Item>

          <Form.Item
            label="最大重试次数"
            name="maxRetries"
            rules={[{ required: true, message: '请输入最大重试次数' }]}
          >
            <InputNumber min={0} max={10} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="请求超时时间 (毫秒)"
            name="timeout"
            rules={[{ required: true, message: '请输入超时时间' }]}
          >
            <InputNumber min={1000} max={60000} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存设置
              </Button>
              <Button htmlType="reset">重置</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default Settings
