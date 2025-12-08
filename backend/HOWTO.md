# MediaCrawler Backend API - How To Guide

## Quick Start Guide

### 1. Start the Backend Server

From the project root directory:

```bash
cd /home/path/to/MediaCrawler
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Or with auto-reload for development:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- Base URL: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs
- Health Check: http://localhost:8000/health

### 2. Test the API

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Get Supported Platforms
```bash
curl http://localhost:8000/api/v1/crawler/platforms
```

#### Start a Crawler Task
```bash
curl -X POST http://localhost:8000/api/v1/crawler/start \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xhs",
    "type": "search",
    "config": {
      "keyword": "编程",
      "pages": 10,
      "sort": "latest"
    }
  }'
```

#### Get Task List
```bash
curl "http://localhost:8000/api/v1/crawler/tasks?page=1&pageSize=20"
```

#### Get Task Details
```bash
curl "http://localhost:8000/api/v1/crawler/task/{task_id}"
```

### 3. WebSocket Connection

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/task/YOUR_TASK_ID');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  // Handle different event types
  switch (data.type) {
    case 'task_progress':
      console.log(`Progress: ${data.data.progress}%`);
      break;
    case 'task_completed':
      console.log('Task completed!');
      break;
    case 'task_error':
      console.error('Error:', data.data.message);
      break;
  }
};
```

### 4. Export Results

#### Export as JSON
```bash
curl "http://localhost:8000/api/v1/results/export?format=json&platform=xhs" > results.json
```

#### Export as CSV
```bash
curl "http://localhost:8000/api/v1/results/export?format=csv" > results.csv
```

## Database Configuration

### Using SQLite (Default)

SQLite is used by default for development. The database file is created automatically at:
```
/path/to/MediaCrawler/media_crawler.db
```

No additional configuration needed!

### Using MySQL

To use MySQL instead:

1. Create a `.env` file in the `backend` directory:
```env
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=media_crawler
```

2. Create the database:
```sql
CREATE DATABASE media_crawler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Start the server - tables will be created automatically.

## Common Tasks

### View All Tasks
```bash
curl http://localhost:8000/api/v1/crawler/tasks | jq .
```

### Pause a Running Task
```bash
curl -X POST http://localhost:8000/api/v1/crawler/pause/TASK_ID
```

### Resume a Paused Task
```bash
curl -X POST http://localhost:8000/api/v1/crawler/resume/TASK_ID
```

### Cancel a Task
```bash
curl -X POST http://localhost:8000/api/v1/crawler/cancel/TASK_ID
```

### Get Statistics Summary
```bash
curl "http://localhost:8000/api/v1/statistics/summary?startDate=2025-12-01&endDate=2025-12-08" | jq .
```

### Delete a Result
```bash
curl -X DELETE http://localhost:8000/api/v1/results/RESULT_ID
```

### Batch Delete Results
```bash
curl -X POST http://localhost:8000/api/v1/results/batch-delete \
  -H "Content-Type: application/json" \
  -d '{"ids": ["id1", "id2", "id3"]}'
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, specify a different port:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

### Module Not Found Errors
Make sure you're running from the project root directory:
```bash
cd /path/to/MediaCrawler
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Database Errors
Delete the database file and restart to recreate:
```bash
rm media_crawler.db
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Integration with Frontend

The React frontend expects the backend at http://localhost:8000. Make sure:

1. Backend is running on port 8000
2. CORS is properly configured (it is by default)
3. Frontend proxy is configured in `frontend/vite.config.ts`

To start both:

```bash
# Terminal 1 - Backend
cd /path/to/MediaCrawler
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd /path/to/MediaCrawler/frontend
npm run dev
```

Then access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

## API Response Format

All API responses follow this format:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": null,
  "error": null
}
```

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "message": "Error message",
  "error": "ERROR_CODE"
}
```

## Next Steps

1. Check the interactive API documentation at http://localhost:8000/api/v1/docs
2. Test all endpoints using the Swagger UI
3. Connect the frontend and test the full integration
4. Monitor WebSocket events for real-time updates

For more details, see:
- `backend/README.md` - Full backend documentation
- `frontend/INTEGRATION.md` - Frontend integration guide
