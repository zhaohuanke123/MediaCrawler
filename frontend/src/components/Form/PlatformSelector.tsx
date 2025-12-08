import React from 'react'
import { Card, Checkbox, Row, Col, Space, Tag } from 'antd'
import { Platform } from '@/types'
import { PLATFORM_INFO } from '@/types/crawler'
import { getPlatformColor } from '@/utils/platform'

interface PlatformSelectorProps {
  value?: Platform[]
  onChange?: (platforms: Platform[]) => void
}

const PlatformSelector: React.FC<PlatformSelectorProps> = ({ value = [], onChange }) => {
  const platforms = Object.values(PLATFORM_INFO)

  const handlePlatformToggle = (platform: Platform) => {
    const newPlatforms = value.includes(platform)
      ? value.filter(p => p !== platform)
      : [...value, platform]
    onChange?.(newPlatforms)
  }

  return (
    <div>
      <Row gutter={[16, 16]}>
        {platforms.map(platform => (
          <Col key={platform.id} xs={24} sm={12} md={8} lg={6}>
            <Card
              hoverable
              size="small"
              style={{
                border: value.includes(platform.id)
                  ? `2px solid ${getPlatformColor(platform.id)}`
                  : '1px solid #d9d9d9',
                cursor: 'pointer',
              }}
              onClick={() => handlePlatformToggle(platform.id)}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Space>
                    <span style={{ fontSize: 24 }}>{platform.icon}</span>
                    <strong>{platform.displayName}</strong>
                  </Space>
                  <Checkbox checked={value.includes(platform.id)} />
                </div>
                <div style={{ fontSize: 12, color: '#666' }}>{platform.description}</div>
                <div>
                  {platform.supportedTypes.slice(0, 3).map(type => (
                    <Tag key={type} color="blue" style={{ fontSize: 10, marginBottom: 4 }}>
                      {type}
                    </Tag>
                  ))}
                </div>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  )
}

export default PlatformSelector
