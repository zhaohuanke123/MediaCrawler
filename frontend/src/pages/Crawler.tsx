import React from 'react'
import CrawlerForm from '@/components/Form/CrawlerForm'

const Crawler: React.FC = () => {
  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>爬虫管理</h1>
      <CrawlerForm />
    </div>
  )
}

export default Crawler
