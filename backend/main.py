# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
FastAPI Backend Main Application Entry Point
"""

import sys
import logging
import asyncio
import platform
from pathlib import Path
from contextlib import asynccontextmanager

# Fix for Windows: Set WindowsSelectorEventLoopPolicy to support subprocess
# This is required for Playwright to work on Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add parent directory to sys.path to allow imports from project root
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.api.v1 import crawler, results, statistics, tasks
from backend.app.api.websocket import websocket as ws_router
from backend.app.models.database import init_db, close_db
from backend.app.services.task_manager import task_manager


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting MediaCrawler API...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MediaCrawler API...")
    await task_manager.shutdown()
    await close_db()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.VERSION,
            "service": settings.PROJECT_NAME
        }
    )


# Include routers
app.include_router(
    crawler.router,
    prefix=settings.API_PREFIX,
    tags=["Crawler"]
)
app.include_router(
    results.router,
    prefix=settings.API_PREFIX,
    tags=["Results"]
)
app.include_router(
    statistics.router,
    prefix=settings.API_PREFIX,
    tags=["Statistics"]
)
app.include_router(
    tasks.router,
    prefix=settings.API_PREFIX,
    tags=["Tasks"]
)
app.include_router(
    ws_router.router,
    tags=["WebSocket"]
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
