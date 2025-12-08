# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Result service for managing crawler results"""

import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_

from backend.app.models.result import Result

logger = logging.getLogger(__name__)


class ResultService:
    """Service for managing crawler results"""
    
    @staticmethod
    async def get_results(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        platform: Optional[str] = None,
        keyword: Optional[str] = None,
        sort_by: str = "timestamp",
        order: str = "desc"
    ) -> tuple[List[Result], int]:
        """Get paginated results"""
        # Build query
        query = select(Result)
        
        # Apply filters
        conditions = []
        if platform:
            conditions.append(Result.platform == platform)
        if keyword:
            conditions.append(Result.content.contains(keyword))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply sorting
        sort_column = getattr(Result, sort_by, Result.timestamp)
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get total count
        count_query = select(func.count()).select_from(Result)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    @staticmethod
    async def get_result_by_id(db: AsyncSession, result_id: str) -> Optional[Result]:
        """Get a single result by ID"""
        result = await db.execute(select(Result).where(Result.id == result_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_result(db: AsyncSession, result_id: str) -> bool:
        """Delete a result by ID"""
        result = await db.execute(delete(Result).where(Result.id == result_id))
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def batch_delete_results(db: AsyncSession, result_ids: List[str]) -> tuple[int, int]:
        """Batch delete results"""
        try:
            # Use bulk delete for efficiency
            result = await db.execute(delete(Result).where(Result.id.in_(result_ids)))
            await db.commit()
            deleted = result.rowcount
            failed = len(result_ids) - deleted
            return deleted, failed
        except Exception as e:
            logger.error(f"Failed to batch delete results: {e}")
            await db.rollback()
            return 0, len(result_ids)
