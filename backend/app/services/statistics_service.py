# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Statistics service"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.task import Task
from app.models.result import Result

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for generating statistics"""
    
    @staticmethod
    async def get_summary(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get statistics summary"""
        # Default to last 7 days if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # Get task statistics
        task_query = select(
            func.count(Task.id).label("total"),
            func.sum(func.case((Task.status == "completed", 1), else_=0)).label("successful"),
            func.sum(func.case((Task.status == "failed", 1), else_=0)).label("failed"),
            func.sum(func.case(
                (Task.end_time.isnot(None), func.extract('epoch', Task.end_time - Task.start_time)),
                else_=0
            )).label("total_time")
        ).where(
            and_(
                Task.created_at >= start_date,
                Task.created_at <= end_date
            )
        )
        
        task_result = await db.execute(task_query)
        task_stats = task_result.first()
        
        # Get result statistics
        result_query = select(
            func.count(Result.id).label("total")
        ).join(Task, Result.task_id == Task.id).where(
            and_(
                Task.created_at >= start_date,
                Task.created_at <= end_date
            )
        )
        
        result_result = await db.execute(result_query)
        total_results = result_result.scalar() or 0
        
        # Get results per platform
        platform_query = select(
            Result.platform,
            func.count(Result.id).label("count")
        ).join(Task, Result.task_id == Task.id).where(
            and_(
                Task.created_at >= start_date,
                Task.created_at <= end_date
            )
        ).group_by(Result.platform)
        
        platform_result = await db.execute(platform_query)
        platforms = {row.platform: row.count for row in platform_result}
        
        total_tasks = task_stats.total or 0
        successful_tasks = task_stats.successful or 0
        failed_tasks = task_stats.failed or 0
        total_crawl_time = int(task_stats.total_time or 0)
        
        return {
            "totalTasks": total_tasks,
            "successfulTasks": successful_tasks,
            "failedTasks": failed_tasks,
            "totalResults": total_results,
            "avgResultsPerTask": total_results / total_tasks if total_tasks > 0 else 0,
            "totalCrawlTime": total_crawl_time,
            "platforms": platforms
        }
    
    @staticmethod
    async def get_platform_statistics(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get platform-specific statistics"""
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # Query for platform stats
        query = select(
            Task.platform,
            func.count(Task.id).label("tasks"),
            func.count(Result.id).label("results"),
            func.avg(
                func.coalesce(
                    func.json_extract(Result.metrics, '$.likes'),
                    0
                )
            ).label("avg_engagement")
        ).outerjoin(Result, Task.id == Result.task_id).where(
            and_(
                Task.created_at >= start_date,
                Task.created_at <= end_date
            )
        ).group_by(Task.platform)
        
        result = await db.execute(query)
        rows = result.all()
        
        stats = []
        for row in rows:
            stats.append({
                "platform": row.platform,
                "tasks": row.tasks,
                "results": row.results or 0,
                "avgEngagement": float(row.avg_engagement or 0),
                "topKeywords": [],  # TODO: Implement keyword extraction
                "growth": 0.0  # TODO: Calculate growth
            })
        
        return stats
    
    @staticmethod
    async def get_timeline_statistics(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "day"
    ) -> List[dict]:
        """Get timeline statistics"""
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # For simplicity, return daily aggregates
        # In production, this would use proper date truncation based on interval
        timeline = []
        
        # Get completed tasks per day
        query = select(
            func.date(Task.end_time).label("date"),
            func.count(Task.id).label("tasks_completed"),
            func.count(Result.id).label("results_collected")
        ).outerjoin(Result, Task.id == Result.task_id).where(
            and_(
                Task.end_time.isnot(None),
                Task.end_time >= start_date,
                Task.end_time <= end_date,
                Task.status == "completed"
            )
        ).group_by(func.date(Task.end_time))
        
        result = await db.execute(query)
        rows = result.all()
        
        for row in rows:
            timeline.append({
                "timestamp": row.date.isoformat() if row.date else datetime.utcnow().date().isoformat(),
                "tasksCompleted": row.tasks_completed,
                "resultsCollected": row.results_collected or 0,
                "avgProcessingTime": 120  # TODO: Calculate actual processing time
            })
        
        return timeline
    
    @staticmethod
    async def get_keyword_statistics(
        db: AsyncSession,
        limit: int = 50,
        start_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get keyword statistics"""
        # This is a placeholder implementation
        # In production, this would analyze content and extract keywords
        return [
            {
                "keyword": "example",
                "frequency": 100,
                "sentiment": "positive",
                "trend": "up",
                "platforms": ["xhs", "douyin"],
                "relatedKeywords": ["related1", "related2"]
            }
        ]
