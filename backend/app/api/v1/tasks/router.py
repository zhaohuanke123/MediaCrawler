# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Tasks endpoints router (for task deletion)"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.app.models.database import get_db
from backend.app.models.task import Task
from backend.app.models.result import Result
from backend.app.schemas.common import ApiResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/crawler")


@router.delete("/task/{task_id}", response_model=ApiResponse[dict])
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a task and its associated results"""
    try:
        # Check if task exists
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Count associated results
        count_result = await db.execute(
            select(Result).where(Result.task_id == task_id)
        )
        results_count = len(count_result.scalars().all())
        
        # Delete associated results first
        await db.execute(delete(Result).where(Result.task_id == task_id))
        
        # Delete the task
        await db.execute(delete(Task).where(Task.id == task_id))
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="Task deleted successfully",
            data={
                "taskId": task_id,
                "resultsDeleted": results_count
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))
