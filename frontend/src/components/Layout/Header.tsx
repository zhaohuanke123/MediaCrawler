import React from 'react'
import { Layout, Button, Space, Typography } from 'antd'
import { MenuFoldOutlined, MenuUnfoldOutlined, BulbOutlined } from '@ant-design/icons'
import { useUIStore } from '@/store'

const { Header: AntHeader } = Layout
const { Title } = Typography

const Header: React.FC = () => {
  const { sidebarCollapsed, toggleSidebar, theme, setTheme } = useUIStore()

  return (
    <AntHeader
      style={{
        padding: '0 24px',
        background: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
      }}
    >
      <Space>
        <Button
          type="text"
          icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={toggleSidebar}
          style={{ fontSize: '16px', width: 64, height: 64 }}
        />
        <Title level={3} style={{ margin: 0 }}>
          🕷️ MediaCrawler
        </Title>
      </Space>
      
      <Space>
        <Button
          type="text"
          icon={<BulbOutlined />}
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        >
          {theme === 'light' ? '暗色' : '亮色'}
        </Button>
      </Space>
    </AntHeader>
  )
}

export default Header
