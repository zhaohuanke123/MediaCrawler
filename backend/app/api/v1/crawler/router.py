# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Crawler endpoints router"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.app.models.database import get_db
from backend.app.models.task import Task
from backend.app.schemas.common import ApiResponse, PaginatedResponse
from backend.app.schemas.crawler import (
    StartCrawlerRequest,
    StartCrawlerResponse,
    PlatformInfo
)
from backend.app.schemas.task import (
    TaskResponse,
    TaskDetail,
    TaskListItem,
    TaskProgress
)
from backend.app.services.crawler_service import CrawlerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/crawler")


@router.get("/platforms", response_model=ApiResponse[list[PlatformInfo]])
async def get_platforms():
    """Get list of supported platforms"""
    platforms = [
        {
            "id": "xhs",
            "name": "小红书",
            "icon": "📕",
            "description": "小红书笔记和评论爬虫",
            "features": ["search", "detail", "comment"],
            "config": {
                "fields": [
                    {"name": "keyword", "type": "string", "required": True, "description": "搜索关键词"},
                    {"name": "pages", "type": "number", "default": 10, "description": "爬取页数"},
                    {"name": "sort", "type": "select", "options": ["latest", "popularity"], "default": "latest"}
                ]
            }
        },
        {
            "id": "douyin",
            "name": "抖音",
            "icon": "🎵",
            "description": "抖音视频和评论爬虫",
            "features": ["search", "detail", "comment"],
            "config": {
                "fields": [
                    {"name": "keyword", "type": "string", "required": True},
                    {"name": "pages", "type": "number", "default": 10}
                ]
            }
        },
        {
            "id": "kuaishou",
            "name": "快手",
            "icon": "⚡",
            "description": "快手视频和评论爬虫",
            "features": ["search", "detail", "comment"],
            "config": {
                "fields": [
                    {"name": "keyword", "type": "string", "required": True},
                    {"name": "pages", "type": "number", "default": 10}
                ]
            }
        },
        {
            "id": "bilibili",
            "name": "B站",
            "icon": "📺",
            "description": "B站视频和评论爬虫",
            "features": ["search", "detail", "comment"],
            "config": {
                "fields": [
                    {"name": "keyword", "type": "string", "required": True},
                    {"name": "pages", "type": "number", "default": 10}
                ]
            }
        },
        {
            "id": "weibo",
            "name": "微博",
            "icon": "🐦",
            "description": "微博内容和评论爬虫",
            "features": ["search", "detail", "comment"],
            "config": {
                "fields": [
                    {"name": "keyword", "type": "string", "required": True},
                    {"name": "pages", "type": "number", "default": 10}
                ]
            }
        },
        {
            "id": "tieba",
            "name": "百度贴吧",
            "icon": "💬",
            "description": "百度贴吧帖子和评论爬虫",
            "features": ["search", "detail", "comment"],
            "config": {
                "fields": [
                    {"name": "keyword", "type": "string", "required": True},
                    {"name": "pages", "type": "number", "default": 10}
                ]
            }
        },
        {
            "id": "zhihu",
            "name": "知乎",
            "icon": "🔍",
            "description": "知乎问答和评论爬虫",
            "features": ["search", "detail", "comment"],
            "config": {
                "fields": [
                    {"name": "keyword", "type": "string", "required": True},
                    {"name": "pages", "type": "number", "default": 10}
                ]
            }
        }
    ]
    
    return ApiResponse(success=True, data=platforms)


@router.post("/start", response_model=ApiResponse[StartCrawlerResponse])
async def start_crawler(
    request: StartCrawlerRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start a new crawler task"""
    try:
        # Validate platform
        valid_platforms = ["xhs", "douyin", "kuaishou", "bilibili", "weibo", "tieba", "zhihu"]
        if request.platform not in valid_platforms:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        # Create task
        task = await CrawlerService.start_crawler(
            db,
            request.platform,
            request.type,
            request.config.model_dump()
        )
        
        response_data = StartCrawlerResponse(
            taskId=task.id,
            platform=task.platform,
            status=task.status,
            startTime=datetime.utcnow().isoformat() + "Z",
            progress=0
        )
        
        return ApiResponse(success=True, data=response_data)
        
    except Exception as e:
        logger.error(f"Error starting crawler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause/{task_id}", response_model=ApiResponse[TaskResponse])
async def pause_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Pause a running task"""
    try:
        task = await CrawlerService.pause_task(db, task_id)
        
        response_data = TaskResponse(
            id=task.id,
            platform=task.platform,
            type=task.type,
            status=task.status,
            config=task.get_config(),
            startTime=task.start_time,
            endTime=task.end_time,
            itemsCollected=task.items_collected,
            progress=task.progress,
            createdAt=task.created_at,
            updatedAt=task.updated_at
        )
        
        return ApiResponse(success=True, data=response_data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error pausing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume/{task_id}", response_model=ApiResponse[TaskResponse])
async def resume_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Resume a paused task"""
    try:
        task = await CrawlerService.resume_task(db, task_id)
        
        response_data = TaskResponse(
            id=task.id,
            platform=task.platform,
            type=task.type,
            status=task.status,
            config=task.get_config(),
            startTime=task.start_time,
            endTime=task.end_time,
            itemsCollected=task.items_collected,
            progress=task.progress,
            createdAt=task.created_at,
            updatedAt=task.updated_at
        )
        
        return ApiResponse(success=True, data=response_data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel/{task_id}", response_model=ApiResponse[TaskResponse])
async def cancel_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel a running task"""
    try:
        task = await CrawlerService.cancel_task(db, task_id)
        
        response_data = TaskResponse(
            id=task.id,
            platform=task.platform,
            type=task.type,
            status=task.status,
            config=task.get_config(),
            startTime=task.start_time,
            endTime=task.end_time,
            itemsCollected=task.items_collected,
            progress=task.progress,
            createdAt=task.created_at,
            updatedAt=task.updated_at
        )
        
        return ApiResponse(success=True, data=response_data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", response_model=ApiResponse[PaginatedResponse[TaskListItem]])
async def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    status: Optional[str] = None,
    platform: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get list of tasks with pagination"""
    try:
        # Build query
        query = select(Task)
        
        # Apply filters
        conditions = []
        if status:
            conditions.append(Task.status == status)
        if platform:
            conditions.append(Task.platform == platform)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by created_at desc
        query = query.order_by(Task.created_at.desc())
        
        # Get total count
        count_query = select(func.count()).select_from(Task)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # Convert to response format
        items = []
        for task in tasks:
            items.append(TaskListItem(
                id=task.id,
                platform=task.platform,
                type=task.type,
                status=task.status,
                startTime=task.start_time,
                estimatedTime=None,
                progress=task.progress,
                itemsCollected=task.items_collected,
                config=task.get_config()
            ))
        
        paginated_data = PaginatedResponse(
            items=items,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=(total + page_size - 1) // page_size
        )
        
        return ApiResponse(success=True, data=paginated_data)
        
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=ApiResponse[TaskDetail])
async def get_task_detail(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific task"""
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Calculate duration
        duration = None
        if task.start_time and task.end_time:
            duration = int((task.end_time - task.start_time).total_seconds())
        
        task_detail = TaskDetail(
            id=task.id,
            platform=task.platform,
            type=task.type,
            status=task.status,
            config=task.get_config(),
            startTime=task.start_time,
            endTime=task.end_time,
            itemsCollected=task.items_collected,
            progress=task.progress,
            createdAt=task.created_at,
            updatedAt=task.updated_at,
            duration=duration,
            logs=task.get_logs(),
            errors=task.get_errors()
        )
        
        return ApiResponse(success=True, data=task_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{task_id}", response_model=ApiResponse[TaskProgress])
async def get_task_progress(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get task progress"""
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        progress_data = TaskProgress(
            taskId=task.id,
            progress=task.progress,
            status=task.status,
            itemsCollected=task.items_collected,
            estimatedRemaining=None,
            speed=None,
            currentPage=None
        )
        
        return ApiResponse(success=True, data=progress_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))
