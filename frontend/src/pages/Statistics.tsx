import React, { useEffect, useState } from 'react'
import { Card, Row, Col } from 'antd'
import ReactECharts from 'echarts-for-react'
import { 
  getPlatformStatistics, 
  getTimelineStatistics,
  PlatformStatistics,
  TimelineStatistics
} from '@/services/statisticsService'

const Statistics: React.FC = () => {
  const [platformData, setPlatformData] = useState<PlatformStatistics[]>([])
  const [timelineData, setTimelineData] = useState<TimelineStatistics[]>([])

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      const [platformResponse, timelineResponse] = await Promise.all([
        getPlatformStatistics(),
        getTimelineStatistics(),
      ])

      if (platformResponse.data) {
        setPlatformData(platformResponse.data)
      }

      if (timelineResponse.data) {
        setTimelineData(timelineResponse.data)
      }
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const platformChartOption = {
    title: {
      text: '平台数据分布',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: platformData.map(item => ({
          name: item.platform,
          value: item.count,
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }

  const timelineChartOption = {
    title: {
      text: '数据趋势',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['数量', '点赞', '评论'],
      bottom: 0,
    },
    xAxis: {
      type: 'category',
      data: timelineData.map(item => item.date),
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '数量',
        type: 'line',
        data: timelineData.map(item => item.count),
      },
      {
        name: '点赞',
        type: 'line',
        data: timelineData.map(item => item.likes),
      },
      {
        name: '评论',
        type: 'line',
        data: timelineData.map(item => item.comments),
      },
    ],
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>统计分析</h1>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts option={platformChartOption} style={{ height: 400 }} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts option={timelineChartOption} style={{ height: 400 }} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Statistics
