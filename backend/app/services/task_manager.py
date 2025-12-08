# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Task manager for handling concurrent crawler tasks"""

import asyncio
import logging
from typing import Dict, Optional, Set
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class TaskManager:
    """Manages concurrent crawler tasks"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_status: Dict[str, dict] = {}
        self.paused_tasks: Set[str] = set()
        self._shutdown = False
        
    async def start_task(self, task_id: str, crawler_func, *args, **kwargs):
        """Start a new crawler task"""
        if len(self.running_tasks) >= self.max_concurrent:
            raise RuntimeError(f"Maximum concurrent tasks ({self.max_concurrent}) reached")
        
        if task_id in self.running_tasks:
            raise ValueError(f"Task {task_id} is already running")
        
        # Create asyncio task
        task = asyncio.create_task(self._run_task(task_id, crawler_func, *args, **kwargs))
        self.running_tasks[task_id] = task
        self.task_status[task_id] = {
            "status": "running",
            "start_time": datetime.utcnow(),
            "progress": 0
        }
        
        logger.info(f"Task {task_id} started")
        return task
    
    async def _run_task(self, task_id: str, crawler_func, *args, **kwargs):
        """Internal task runner"""
        try:
            await crawler_func(task_id, *args, **kwargs)
            self.task_status[task_id]["status"] = "completed"
        except asyncio.CancelledError:
            self.task_status[task_id]["status"] = "cancelled"
            logger.info(f"Task {task_id} was cancelled")
        except Exception as e:
            self.task_status[task_id]["status"] = "failed"
            self.task_status[task_id]["error"] = str(e)
            logger.error(f"Task {task_id} failed: {e}")
        finally:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def pause_task(self, task_id: str):
        """Pause a running task"""
        if task_id not in self.running_tasks:
            raise ValueError(f"Task {task_id} is not running")
        
        self.paused_tasks.add(task_id)
        self.task_status[task_id]["status"] = "paused"
        logger.info(f"Task {task_id} paused")
    
    async def resume_task(self, task_id: str):
        """Resume a paused task"""
        if task_id not in self.paused_tasks:
            raise ValueError(f"Task {task_id} is not paused")
        
        self.paused_tasks.remove(task_id)
        self.task_status[task_id]["status"] = "running"
        logger.info(f"Task {task_id} resumed")
    
    async def cancel_task(self, task_id: str):
        """Cancel a running task"""
        if task_id not in self.running_tasks:
            raise ValueError(f"Task {task_id} is not running")
        
        task = self.running_tasks[task_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        if task_id in self.paused_tasks:
            self.paused_tasks.remove(task_id)
        
        logger.info(f"Task {task_id} cancelled")
    
    def is_paused(self, task_id: str) -> bool:
        """Check if a task is paused"""
        return task_id in self.paused_tasks
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get task status"""
        return self.task_status.get(task_id)
    
    def update_progress(self, task_id: str, progress: int, items_collected: int = 0):
        """Update task progress"""
        if task_id in self.task_status:
            self.task_status[task_id]["progress"] = progress
            self.task_status[task_id]["items_collected"] = items_collected
    
    async def shutdown(self):
        """Shutdown task manager and cancel all running tasks"""
        self._shutdown = True
        logger.info(f"Shutting down task manager. Cancelling {len(self.running_tasks)} tasks...")
        
        for task_id, task in list(self.running_tasks.items()):
            task.cancel()
        
        # Wait for all tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        logger.info("Task manager shutdown complete")


# Global task manager instance
task_manager = TaskManager(max_concurrent=3)
