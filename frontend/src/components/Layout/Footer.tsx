import React from 'react'
import { Layout } from 'antd'

const { Footer: AntFooter } = Layout

const Footer: React.FC = () => {
  return (
    <AntFooter style={{ textAlign: 'center' }}>
      MediaCrawler ©{new Date().getFullYear()} Created with ❤️ for learning purposes
    </AntFooter>
  )
}

export default Footer
