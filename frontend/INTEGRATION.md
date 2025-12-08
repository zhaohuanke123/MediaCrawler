# MediaCrawler Frontend Integration Guide

This guide explains how to integrate the React frontend with the MediaCrawler Python backend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  Port: 3000                                                 │
│  - User Interface                                           │
│  - State Management (Zustand)                               │
│  - API Client (Axios)                                       │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (Python)                        │
│  Port: 8000                                                 │
│  - FastAPI REST API                                         │
│  - WebSocket Support                                        │
│  - Crawler Logic                                            │
│  - Database (MySQL/SQLite)                                  │
└─────────────────────────────────────────────────────────────┘
```

## Backend API Requirements

The frontend expects the following API endpoints to be available:

### Crawler Endpoints
- `POST /api/v1/crawler/start` - Start a crawler task
- `POST /api/v1/crawler/pause/:task_id` - Pause a task
- `POST /api/v1/crawler/resume/:task_id` - Resume a task
- `POST /api/v1/crawler/cancel/:task_id` - Cancel a task
- `GET /api/v1/crawler/platforms` - Get supported platforms
- `GET /api/v1/crawler/tasks` - Get task list
- `GET /api/v1/crawler/task/:task_id` - Get task details
- `GET /api/v1/crawler/progress/:task_id` - Get task progress

### Results Endpoints
- `GET /api/v1/results` - Get results list (with pagination)
- `GET /api/v1/results/:id` - Get result details
- `DELETE /api/v1/results/:id` - Delete a result
- `POST /api/v1/results/batch-delete` - Batch delete results
- `GET /api/v1/results/export` - Export results

### Statistics Endpoints
- `GET /api/v1/statistics/summary` - Get statistics summary
- `GET /api/v1/statistics/platform` - Get platform statistics
- `GET /api/v1/statistics/timeline` - Get timeline statistics
- `GET /api/v1/statistics/keywords` - Get keyword statistics

### WebSocket
- `ws://localhost:8000/ws/task/:task_id` - Real-time task updates

## Running Frontend with Backend

### Option 1: Development Mode (Recommended for Development)

1. **Start the Backend**
   ```bash
   cd /path/to/MediaCrawler
   uv run main.py --platform xhs --lt qrcode --type search
   ```

2. **Start the Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

The Vite dev server is configured to proxy API requests to the backend automatically.

### Option 2: Production Build

1. **Build the Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve the Frontend**
   - Option A: Use Vite preview
     ```bash
     npm run preview
     ```
   
   - Option B: Serve with Python backend
     Configure FastAPI to serve the `dist` folder as static files:
     ```python
     from fastapi.staticfiles import StaticFiles
     app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
     ```

### Option 3: Docker Compose (Recommended for Production)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:password@db:3306/mediacrawler
    depends_on:
      - db
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_DATABASE=mediacrawler
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql

volumes:
  mysql-data:
```

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Run with Docker Compose:
```bash
docker-compose up -d
```

## Environment Configuration

### Frontend Environment Variables

Create `frontend/.env` file:

```env
# API Configuration
VITE_API_BASE_URL=/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws

# Application Settings
VITE_APP_NAME=MediaCrawler
VITE_APP_VERSION=1.0.0
```

### Backend CORS Configuration

Ensure the backend allows requests from the frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## API Response Format

The frontend expects responses in the following format:

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "message": "User-friendly error message"
}
```

### Paginated Response
```json
{
  "success": true,
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  }
}
```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend has CORS middleware configured
   - Check that `allow_origins` includes the frontend URL

2. **API Connection Failed**
   - Verify backend is running on port 8000
   - Check Vite proxy configuration in `vite.config.ts`
   - Ensure no firewall blocking the connection

3. **WebSocket Connection Failed**
   - Verify WebSocket endpoint is accessible
   - Check browser console for connection errors
   - Ensure backend supports WebSocket connections

4. **Build Failures**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Clear Vite cache: `rm -rf node_modules/.vite`
   - Check TypeScript errors: `npm run build`

### Development Tips

- Use browser DevTools Network tab to inspect API calls
- Check browser console for React errors
- Use Redux DevTools for state debugging
- Enable Vite debug mode: `DEBUG=vite:* npm run dev`

## Next Steps

1. Implement the backend API endpoints
2. Set up database migrations
3. Configure authentication and authorization
4. Add WebSocket support for real-time updates
5. Deploy to production environment

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Docker Documentation](https://docs.docker.com/)
