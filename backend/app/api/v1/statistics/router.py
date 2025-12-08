# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Statistics endpoints router"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.database import get_db
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.statistics import (
    StatisticsSummary,
    PlatformStatistics,
    TimelineStatistics,
    KeywordStatistics
)
from backend.app.services.statistics_service import StatisticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/statistics")


@router.get("/summary", response_model=ApiResponse[StatisticsSummary])
async def get_statistics_summary(
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics summary"""
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
        
        summary = await StatisticsService.get_summary(db, start, end)
        
        summary_data = StatisticsSummary(**summary)
        return ApiResponse(success=True, data=summary_data)
        
    except Exception as e:
        logger.error(f"Error getting statistics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platform", response_model=ApiResponse[list[PlatformStatistics]])
async def get_platform_statistics(
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    db: AsyncSession = Depends(get_db)
):
    """Get platform-specific statistics"""
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
        
        stats = await StatisticsService.get_platform_statistics(db, start, end)
        
        platform_stats = [PlatformStatistics(**stat) for stat in stats]
        return ApiResponse(success=True, data=platform_stats)
        
    except Exception as e:
        logger.error(f"Error getting platform statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline", response_model=ApiResponse[list[TimelineStatistics]])
async def get_timeline_statistics(
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    interval: str = Query("day"),
    db: AsyncSession = Depends(get_db)
):
    """Get timeline statistics"""
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
        
        timeline = await StatisticsService.get_timeline_statistics(db, start, end, interval)
        
        timeline_stats = [TimelineStatistics(**stat) for stat in timeline]
        return ApiResponse(success=True, data=timeline_stats)
        
    except Exception as e:
        logger.error(f"Error getting timeline statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keywords", response_model=ApiResponse[list[KeywordStatistics]])
async def get_keyword_statistics(
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[str] = Query(None, alias="startDate"),
    db: AsyncSession = Depends(get_db)
):
    """Get keyword statistics"""
    try:
        # Parse date
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        
        keywords = await StatisticsService.get_keyword_statistics(db, limit, start)
        
        keyword_stats = [KeywordStatistics(**kw) for kw in keywords]
        return ApiResponse(success=True, data=keyword_stats)
        
    except Exception as e:
        logger.error(f"Error getting keyword statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
