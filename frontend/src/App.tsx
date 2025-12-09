import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout, ConfigProvider, theme as antTheme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import Header from '@/components/Layout/Header'
import Sidebar from '@/components/Layout/Sidebar'
import Footer from '@/components/Layout/Footer'
import Dashboard from '@/pages/Dashboard'
import Crawler from '@/pages/Crawler'
import Results from '@/pages/Results'
import Statistics from '@/pages/Statistics'
import TaskList from '@/pages/TaskList'
import Settings from '@/pages/Settings'
import { useUIStore } from '@/store'
import './styles/index.css'

const { Content } = Layout

const App: React.FC = () => {
  const { sidebarCollapsed, theme: appTheme } = useUIStore()

  return (
    <ConfigProvider 
      locale={zhCN}
      theme={{
        algorithm: appTheme === 'dark' ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm,
      }}
    >
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          <Sidebar />
          <Layout style={{ marginLeft: sidebarCollapsed ? 80 : 200, transition: 'all 0.2s' }}>
            <Header />
            <Content style={{ 
              margin: '24px 16px', 
              padding: 24, 
              minHeight: 280 
            }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/crawler" element={<Crawler />} />
                <Route path="/results" element={<Results />} />
                <Route path="/statistics" element={<Statistics />} />
                <Route path="/tasks" element={<TaskList />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Content>
            <Footer />
          </Layout>
        </Layout>
      </Router>
    </ConfigProvider>
  )
}

export default App
