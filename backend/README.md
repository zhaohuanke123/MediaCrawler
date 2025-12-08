# MediaCrawler Backend API

FastAPI-based backend API for MediaCrawler multi-platform content crawler system.

## Features

- **RESTful API** - Complete REST API for crawler management, results, and statistics
- **WebSocket Support** - Real-time task progress updates
- **Multi-Database** - Support for both SQLite (development) and MySQL (production)
- **Async Operations** - Built with FastAPI and SQLAlchemy async
- **Auto Documentation** - Interactive API docs at `/api/v1/docs`
- **CORS Enabled** - Ready for frontend integration

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r ../requirements.txt
```

Or using the root requirements.txt:

```bash
cd /path/to/MediaCrawler
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the `backend` directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` to configure your database and other settings.

### 3. Run the Server

```bash
cd backend
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API Endpoints

### Crawler Management

- `GET /api/v1/crawler/platforms` - Get supported platforms
- `POST /api/v1/crawler/start` - Start a crawler task
- `POST /api/v1/crawler/pause/{task_id}` - Pause a task
- `POST /api/v1/crawler/resume/{task_id}` - Resume a task
- `POST /api/v1/crawler/cancel/{task_id}` - Cancel a task
- `GET /api/v1/crawler/tasks` - List tasks (paginated)
- `GET /api/v1/crawler/task/{task_id}` - Get task details
- `GET /api/v1/crawler/progress/{task_id}` - Get task progress

### Results Management

- `GET /api/v1/results` - List results (paginated, with filters)
- `GET /api/v1/results/{result_id}` - Get result details
- `DELETE /api/v1/results/{result_id}` - Delete a result
- `POST /api/v1/results/batch-delete` - Batch delete results
- `GET /api/v1/results/export` - Export results (CSV, JSON)

### Statistics

- `GET /api/v1/statistics/summary` - Get statistics summary
- `GET /api/v1/statistics/platform` - Get platform statistics
- `GET /api/v1/statistics/timeline` - Get timeline statistics
- `GET /api/v1/statistics/keywords` - Get keyword statistics

### WebSocket

- `WS /ws/task/{task_id}` - Real-time task updates

### Health Check

- `GET /health` - Health check endpoint

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── crawler/      # Crawler management endpoints
│   │   │   ├── results/      # Results management endpoints
│   │   │   ├── statistics/   # Statistics endpoints
│   │   │   └── tasks/        # Task management endpoints
│   │   └── websocket/        # WebSocket endpoints
│   ├── models/               # SQLAlchemy models
│   │   ├── database.py       # Database connection
│   │   ├── task.py           # Task model
│   │   ├── result.py         # Result model
│   │   └── statistics.py     # Statistics model
│   ├── schemas/              # Pydantic schemas
│   │   ├── common.py         # Common schemas
│   │   ├── task.py           # Task schemas
│   │   ├── result.py         # Result schemas
│   │   ├── statistics.py     # Statistics schemas
│   │   └── crawler.py        # Crawler schemas
│   ├── services/             # Business logic
│   │   ├── task_manager.py   # Task queue manager
│   │   ├── crawler_service.py # Crawler service
│   │   ├── result_service.py  # Result service
│   │   ├── statistics_service.py # Statistics service
│   │   └── websocket_manager.py # WebSocket manager
│   ├── config.py             # Configuration
│   └── __init__.py
├── main.py                   # Application entry point
├── .env.example              # Environment variables example
└── README.md                 # This file
```

## Database

### SQLite (Default for Development)

The application uses SQLite by default. The database file will be created automatically in the backend directory as `media_crawler.db`.

### MySQL (Production)

To use MySQL, update your `.env` file:

```env
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=media_crawler
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

The project follows PEP 8 style guidelines. Use tools like `black` and `flake8` for formatting and linting.

## Integration with Frontend

The backend is designed to work with the React frontend located in the `frontend/` directory.

1. Start the backend server (default port 8000)
2. Start the frontend dev server (default port 3000)
3. The frontend is configured to proxy API requests to the backend

See `frontend/INTEGRATION.md` for more details.

## WebSocket Events

The WebSocket endpoint sends the following event types:

- `task_started` - Task has started
- `task_progress` - Progress update
- `task_completed` - Task completed
- `task_error` - Error occurred
- `task_log` - Log message

Example event:

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

## Error Handling

All endpoints return responses in a consistent format:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "User-friendly error message",
  "details": { ... }
}
```

## License

This project is licensed under NON-COMMERCIAL LEARNING LICENSE 1.1. See LICENSE file for details.

## Support

For issues and questions, please refer to the main project README or create an issue on GitHub.
