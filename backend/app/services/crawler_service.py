# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Crawler service for managing crawler tasks"""

import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.app.models.task import Task
from backend.app.models.result import Result
from backend.app.services.task_manager import task_manager
from backend.app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class CrawlerService:
    """Service for managing crawler operations"""
    
    # Platform mapping
    PLATFORM_MAP = {
        "xhs": "xhs",
        "douyin": "dy",
        "kuaishou": "ks",
        "bilibili": "bili",
        "weibo": "wb",
        "tieba": "tieba",
        "zhihu": "zhihu"
    }
    
    @staticmethod
    async def start_crawler(
        db: AsyncSession,
        platform: str,
        crawler_type: str,
        config: dict
    ) -> Task:
        """Start a new crawler task"""
        # Create task record
        task_id = str(uuid4())
        task = Task(
            id=task_id,
            platform=platform,
            type=crawler_type,
            status="pending",
            config=str(config),
            start_time=None,
            items_collected=0,
            progress=0
        )
        task.set_config(config)
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        # Start crawler in background
        asyncio.create_task(
            CrawlerService._run_crawler_task(task_id, platform, crawler_type, config)
        )
        
        return task
    
    @staticmethod
    async def _run_crawler_task(
        task_id: str,
        platform: str,
        crawler_type: str,
        config: dict
    ):
        """Run crawler task in background"""
        from backend.app.models.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                # Update task status to running
                await db.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(
                        status="running",
                        start_time=datetime.utcnow()
                    )
                )
                await db.commit()
                
                # Broadcast task started
                await websocket_manager.broadcast_task_event(
                    task_id,
                    "task_started",
                    {"taskId": task_id, "status": "running"}
                )
                
                # Simulate crawler execution
                # In production, this would integrate with actual crawler implementations
                logger.info(f"Starting crawler task {task_id} for {platform}")
                
                items_collected = 0
                for progress in range(0, 101, 10):
                    # Check if task is paused
                    while task_manager.is_paused(task_id):
                        await asyncio.sleep(1)
                    
                    # Simulate work
                    await asyncio.sleep(2)
                    
                    # Create sample results for this progress step (1-2 results per step)
                    if progress > 0 and progress < 100:
                        num_results = 2 if progress % 20 == 0 else 1
                        for i in range(num_results):
                            result = Result(
                                id=str(uuid4()),
                                task_id=task_id,
                                platform=platform,
                                type="note" if platform == "xhs" else "video",
                                title=f"Sample {platform} content #{items_collected + i + 1}",
                                content=f"This is sample content from {platform} crawler task {task_id}. Progress: {progress}%",
                                author=f"user_{items_collected + i + 1}",
                                author_id=f"uid_{items_collected + i + 1}",
                                url=f"https://{platform}.com/content/{task_id}_{items_collected + i + 1}",
                                image_urls='[]',
                                video_url=None,
                                metrics=json.dumps({
                                    "likes": 100 + items_collected * 10,
                                    "comments": 20 + items_collected * 2,
                                    "shares": 10 + items_collected,
                                    "views": 1000 + items_collected * 100
                                }),
                                timestamp=datetime.utcnow(),
                                tags=json.dumps(["sample", "test", platform]),
                                sentiment="positive"
                            )
                            db.add(result)
                            items_collected += 1
                        
                        await db.commit()
                    
                    # Update progress
                    await db.execute(
                        update(Task)
                        .where(Task.id == task_id)
                        .values(
                            progress=progress,
                            items_collected=items_collected
                        )
                    )
                    await db.commit()
                    
                    # Broadcast progress
                    await websocket_manager.broadcast_task_event(
                        task_id,
                        "task_progress",
                        {
                            "progress": progress,
                            "itemsCollected": items_collected,
                            "status": "running",
                            "speed": 5.0
                        }
                    )
                    
                    logger.info(f"Task {task_id} progress: {progress}%")
                
                # Mark as completed
                await db.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(
                        status="completed",
                        end_time=datetime.utcnow(),
                        progress=100
                    )
                )
                await db.commit()
                
                # Broadcast completion
                await websocket_manager.broadcast_task_event(
                    task_id,
                    "task_completed",
                    {"taskId": task_id, "status": "completed", "itemsCollected": items_collected}
                )
                
                logger.info(f"Task {task_id} completed successfully")
                
            except asyncio.CancelledError:
                # Task was cancelled
                await db.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(
                        status="cancelled",
                        end_time=datetime.utcnow()
                    )
                )
                await db.commit()
                
                await websocket_manager.broadcast_task_event(
                    task_id,
                    "task_completed",
                    {"taskId": task_id, "status": "cancelled"}
                )
                
                logger.info(f"Task {task_id} was cancelled")
                raise
                
            except Exception as e:
                # Task failed
                logger.error(f"Task {task_id} failed: {e}")
                
                await db.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(
                        status="failed",
                        end_time=datetime.utcnow()
                    )
                )
                await db.commit()
                
                # Add error to task
                result = await db.execute(select(Task).where(Task.id == task_id))
                task = result.scalar_one_or_none()
                if task:
                    task.add_error(str(e))
                    await db.commit()
                
                await websocket_manager.broadcast_task_event(
                    task_id,
                    "task_error",
                    {
                        "taskId": task_id,
                        "errorCode": "CRAWLER_ERROR",
                        "message": str(e),
                        "retrying": False
                    }
                )
    
    @staticmethod
    async def pause_task(db: AsyncSession, task_id: str) -> Task:
        """Pause a running task"""
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if task.status != "running":
            raise ValueError(f"Task {task_id} is not running")
        
        await task_manager.pause_task(task_id)
        
        task.status = "paused"
        await db.commit()
        await db.refresh(task)
        
        return task
    
    @staticmethod
    async def resume_task(db: AsyncSession, task_id: str) -> Task:
        """Resume a paused task"""
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if task.status != "paused":
            raise ValueError(f"Task {task_id} is not paused")
        
        await task_manager.resume_task(task_id)
        
        task.status = "running"
        await db.commit()
        await db.refresh(task)
        
        return task
    
    @staticmethod
    async def cancel_task(db: AsyncSession, task_id: str) -> Task:
        """Cancel a running task"""
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if task.status not in ["running", "paused"]:
            raise ValueError(f"Task {task_id} cannot be cancelled")
        
        # Cancel the task
        if task_id in task_manager.running_tasks:
            await task_manager.cancel_task(task_id)
        
        task.status = "cancelled"
        task.end_time = datetime.utcnow()
        await db.commit()
        await db.refresh(task)
        
        return task
