# MediaCrawler Backend API Reference

Complete API reference for MediaCrawler backend services.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently no authentication is required. Future versions will support JWT token authentication.

## Response Format

All API responses follow this standard format:

### Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": null,
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "data": null,
  "message": "User-friendly error message",
  "error": "ERROR_CODE"
}
```

### Paginated Response
```json
{
  "success": true,
  "data": {
    "items": [ /* array of items */ ],
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_PLATFORM` | Unsupported platform |
| `INVALID_CONFIG` | Invalid configuration |
| `TASK_NOT_FOUND` | Task not found |
| `TASK_IN_PROGRESS` | Task is already running |
| `DATABASE_ERROR` | Database operation failed |
| `CRAWLER_ERROR` | Crawler execution error |
| `NETWORK_ERROR` | Network connectivity error |
| `TIMEOUT` | Operation timeout |
| `RATE_LIMITED` | Rate limit exceeded |

---

## Crawler Management

### Get Supported Platforms

Get list of all supported platforms and their configurations.

**Endpoint:** `GET /crawler/platforms`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "xhs",
      "name": "小红书",
      "icon": "📕",
      "description": "小红书笔记和评论爬虫",
      "features": ["search", "detail", "comment"],
      "config": {
        "fields": [
          {
            "name": "keyword",
            "type": "string",
            "required": true,
            "description": "搜索关键词"
          },
          {
            "name": "pages",
            "type": "number",
            "default": 10,
            "description": "爬取页数"
          }
        ]
      }
    }
  ]
}
```

### Start Crawler Task

Start a new crawler task.

**Endpoint:** `POST /crawler/start`

**Request Body:**
```json
{
  "platform": "xhs",
  "type": "search",
  "config": {
    "keyword": "编程",
    "pages": 10,
    "sort": "latest"
  },
  "crawlerOptions": {
    "headless": true,
    "timeout": 30000,
    "proxy": null,
    "useCache": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "taskId": "uuid-here",
    "platform": "xhs",
    "status": "running",
    "startTime": "2025-12-08T10:00:00Z",
    "progress": 0
  }
}
```

### Pause Task

Pause a running task.

**Endpoint:** `POST /crawler/pause/{task_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "task-id",
    "status": "paused",
    "progress": 45
  }
}
```

### Resume Task

Resume a paused task.

**Endpoint:** `POST /crawler/resume/{task_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "task-id",
    "status": "running",
    "progress": 45
  }
}
```

### Cancel Task

Cancel a running or paused task.

**Endpoint:** `POST /crawler/cancel/{task_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "task-id",
    "status": "cancelled",
    "itemsCollected": 45
  }
}
```

### List Tasks

Get paginated list of tasks with optional filters.

**Endpoint:** `GET /crawler/tasks`

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `pageSize` (integer, default: 20, max: 100) - Items per page
- `status` (string, optional) - Filter by status: running|completed|failed|cancelled
- `platform` (string, optional) - Filter by platform

**Example:** `GET /crawler/tasks?page=1&pageSize=20&status=running`

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "task-id",
        "platform": "xhs",
        "type": "search",
        "status": "running",
        "startTime": "2025-12-08T10:00:00",
        "progress": 45,
        "itemsCollected": 45,
        "config": { /* task config */ }
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  }
}
```

### Get Task Details

Get detailed information about a specific task.

**Endpoint:** `GET /crawler/task/{task_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "task-id",
    "platform": "xhs",
    "type": "search",
    "status": "running",
    "startTime": "2025-12-08T10:00:00",
    "endTime": null,
    "duration": 120,
    "progress": 45,
    "itemsCollected": 45,
    "config": { /* task config */ },
    "logs": [
      {
        "timestamp": "2025-12-08T10:00:00",
        "level": "INFO",
        "message": "Task started"
      }
    ],
    "errors": []
  }
}
```

### Get Task Progress

Get current progress of a task.

**Endpoint:** `GET /crawler/progress/{task_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "taskId": "task-id",
    "progress": 45,
    "status": "running",
    "itemsCollected": 45,
    "speed": 10,
    "currentPage": 5
  }
}
```

---

## Results Management

### List Results

Get paginated list of results with filters.

**Endpoint:** `GET /results`

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `pageSize` (integer, default: 20, max: 100) - Items per page
- `platform` (string, optional) - Filter by platform
- `keyword` (string, optional) - Search in content
- `sortBy` (string, default: "timestamp") - Sort field
- `order` (string, default: "desc") - Sort order: asc|desc

**Example:** `GET /results?page=1&pageSize=20&platform=xhs`

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "result-id",
        "platform": "xhs",
        "type": "note",
        "title": "Example Title",
        "content": "Content...",
        "author": "username",
        "likes": 100,
        "comments": 20,
        "shares": 10,
        "url": "https://...",
        "imageUrls": ["url1", "url2"],
        "timestamp": "2025-12-08T10:00:00",
        "taskId": "task-id",
        "tags": ["tag1", "tag2"]
      }
    ],
    "total": 1000,
    "page": 1,
    "pageSize": 20,
    "totalPages": 50
  }
}
```

### Get Result Details

Get detailed information about a specific result.

**Endpoint:** `GET /results/{result_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "result-id",
    "platform": "xhs",
    "type": "note",
    "title": "Example Title",
    "content": "Content...",
    "author": "username",
    "authorId": "user-id",
    "url": "https://...",
    "imageUrls": ["url1", "url2"],
    "videoUrl": null,
    "metrics": {
      "likes": 100,
      "comments": 20,
      "shares": 10,
      "views": 1000
    },
    "timestamp": "2025-12-08T10:00:00",
    "taskId": "task-id",
    "tags": ["tag1", "tag2"],
    "sentiment": "positive",
    "createdAt": "2025-12-08T10:00:00"
  }
}
```

### Delete Result

Delete a single result.

**Endpoint:** `DELETE /results/{result_id}`

**Response:**
```json
{
  "success": true,
  "message": "Result deleted successfully",
  "data": {
    "resultId": "result-id"
  }
}
```

### Batch Delete Results

Delete multiple results at once.

**Endpoint:** `POST /results/batch-delete`

**Request Body:**
```json
{
  "ids": ["id1", "id2", "id3"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "deleted": 10,
    "failed": 0
  }
}
```

### Export Results

Export results in various formats.

**Endpoint:** `GET /results/export`

**Query Parameters:**
- `format` (string, required) - Export format: csv|json|excel
- `ids` (string, optional) - Comma-separated list of result IDs
- `platform` (string, optional) - Filter by platform
- `keyword` (string, optional) - Search keyword

**Example:** `GET /results/export?format=csv&platform=xhs`

**Response:** File download (CSV, JSON, or Excel format)

---

## Statistics & Analytics

### Get Statistics Summary

Get overall statistics summary.

**Endpoint:** `GET /statistics/summary`

**Query Parameters:**
- `startDate` (string, optional) - Start date (ISO 8601)
- `endDate` (string, optional) - End date (ISO 8601)

**Example:** `GET /statistics/summary?startDate=2025-12-01&endDate=2025-12-08`

**Response:**
```json
{
  "success": true,
  "data": {
    "totalTasks": 50,
    "successfulTasks": 48,
    "failedTasks": 2,
    "totalResults": 10000,
    "avgResultsPerTask": 200,
    "totalCrawlTime": 3600,
    "platforms": {
      "xhs": 3000,
      "douyin": 2500,
      "bilibili": 1200
    }
  }
}
```

### Get Platform Statistics

Get platform-specific statistics.

**Endpoint:** `GET /statistics/platform`

**Query Parameters:**
- `startDate` (string, optional) - Start date
- `endDate` (string, optional) - End date

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "platform": "xhs",
      "tasks": 10,
      "results": 3000,
      "avgEngagement": 250,
      "topKeywords": ["keyword1", "keyword2"],
      "growth": 15
    }
  ]
}
```

### Get Timeline Statistics

Get time-series statistics.

**Endpoint:** `GET /statistics/timeline`

**Query Parameters:**
- `startDate` (string, optional) - Start date
- `endDate` (string, optional) - End date
- `interval` (string, default: "day") - Time interval: day|hour

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2025-12-08T00:00:00Z",
      "tasksCompleted": 5,
      "resultsCollected": 500,
      "avgProcessingTime": 120
    }
  ]
}
```

### Get Keyword Statistics

Get keyword analysis and trends.

**Endpoint:** `GET /statistics/keywords`

**Query Parameters:**
- `limit` (integer, default: 50, max: 100) - Number of keywords
- `startDate` (string, optional) - Start date

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "keyword": "编程",
      "frequency": 100,
      "sentiment": "positive",
      "trend": "up",
      "platforms": ["xhs", "douyin"],
      "relatedKeywords": ["python", "java"]
    }
  ]
}
```

---

## WebSocket Events

### Connection

**Endpoint:** `WS /ws/task/{task_id}`

Connect to receive real-time updates for a specific task.

### Event Types

#### task_started
```json
{
  "type": "task_started",
  "timestamp": "2025-12-08T10:00:00Z",
  "data": {
    "taskId": "task-id",
    "status": "running"
  }
}
```

#### task_progress
```json
{
  "type": "task_progress",
  "timestamp": "2025-12-08T10:00:00Z",
  "data": {
    "progress": 45,
    "itemsCollected": 45,
    "status": "running",
    "speed": 10.0
  }
}
```

#### task_completed
```json
{
  "type": "task_completed",
  "timestamp": "2025-12-08T10:00:00Z",
  "data": {
    "taskId": "task-id",
    "status": "completed",
    "itemsCollected": 100
  }
}
```

#### task_error
```json
{
  "type": "task_error",
  "timestamp": "2025-12-08T10:00:00Z",
  "data": {
    "errorCode": "TIMEOUT",
    "message": "Request timeout",
    "retrying": true
  }
}
```

#### task_log
```json
{
  "type": "task_log",
  "timestamp": "2025-12-08T10:00:00Z",
  "data": {
    "level": "INFO",
    "message": "Processing page 5"
  }
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Future versions will include:
- Per-IP rate limiting
- Per-user rate limiting
- Configurable limits

---

## Versioning

The API uses URL versioning. The current version is `v1`.

All endpoints are prefixed with `/api/v1`.

---

## Support

For issues and questions:
- Check the interactive documentation at `/api/v1/docs`
- Review the README files in the backend directory
- Create an issue on GitHub

---

*Last Updated: 2025-12-08*
