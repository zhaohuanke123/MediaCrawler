// Validation utilities

// Validate email
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Validate URL
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// Validate keyword (not empty, max length)
export const isValidKeyword = (keyword: string): boolean => {
  return keyword.trim().length > 0 && keyword.length <= 100
}

// Validate number range
export const isInRange = (value: number, min: number, max: number): boolean => {
  return value >= min && value <= max
}

// Validate positive number
export const isPositiveNumber = (value: number): boolean => {
  return value > 0 && !isNaN(value)
}

// Validate date format (YYYY-MM-DD)
export const isValidDate = (date: string): boolean => {
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!dateRegex.test(date)) return false
  
  const d = new Date(date)
  return d instanceof Date && !isNaN(d.getTime())
}

// Validate date range
export const isValidDateRange = (startDate: string, endDate: string): boolean => {
  if (!isValidDate(startDate) || !isValidDate(endDate)) return false
  return new Date(startDate) <= new Date(endDate)
}

// Validate required field
export const isRequired = (value: any): boolean => {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  if (Array.isArray(value)) return value.length > 0
  return true
}

// Validate array not empty
export const isNonEmptyArray = (arr: any[]): boolean => {
  return Array.isArray(arr) && arr.length > 0
}

// Validate object has properties
export const hasProperties = (obj: any, keys: string[]): boolean => {
  return keys.every(key => key in obj && obj[key] !== undefined)
}

// Validate crawler config
export const isValidCrawlerConfig = (config: any): { valid: boolean; errors: string[] } => {
  const errors: string[] = []

  if (!isNonEmptyArray(config.platforms)) {
    errors.push('请至少选择一个平台')
  }

  if (!isValidKeyword(config.keywords)) {
    errors.push('请输入有效的关键词')
  }

  if (!isRequired(config.crawlerType)) {
    errors.push('请选择爬取类型')
  }

  if (!isPositiveNumber(config.limit)) {
    errors.push('爬取数量必须大于0')
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}
