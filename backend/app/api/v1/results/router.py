# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Results endpoints router"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import json
import io

from backend.app.models.database import get_db
from backend.app.schemas.common import ApiResponse, PaginatedResponse
from backend.app.schemas.result import (
    ResultListItem,
    ResultDetail,
    BatchDeleteRequest,
    BatchDeleteResponse
)
from backend.app.services.result_service import ResultService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/results")


@router.get("", response_model=ApiResponse[PaginatedResponse[ResultListItem]])
async def get_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    platform: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = Query("timestamp", alias="sortBy"),
    order: str = Query("desc"),
    db: AsyncSession = Depends(get_db)
):
    """Get results with pagination and filtering"""
    try:
        items, total = await ResultService.get_results(
            db,
            page=page,
            page_size=page_size,
            platform=platform,
            keyword=keyword,
            sort_by=sort_by,
            order=order
        )
        
        # Convert to response format
        result_items = []
        for item in items:
            result_items.append(ResultListItem(
                id=item.id,
                platform=item.platform,
                type=item.type,
                title=item.title,
                content=item.content,
                author=item.author,
                likes=item.get_metrics().get("likes", 0),
                comments=item.get_metrics().get("comments", 0),
                shares=item.get_metrics().get("shares", 0),
                url=item.url,
                imageUrls=item.get_image_urls(),
                timestamp=item.timestamp,
                taskId=item.task_id,
                tags=item.get_tags()
            ))
        
        paginated_data = PaginatedResponse(
            items=result_items,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=(total + page_size - 1) // page_size
        )
        
        return ApiResponse(success=True, data=paginated_data)
        
    except Exception as e:
        logger.error(f"Error getting results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{result_id}", response_model=ApiResponse[ResultDetail])
async def get_result_detail(result_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific result"""
    try:
        result = await ResultService.get_result_by_id(db, result_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        detail = ResultDetail(
            id=result.id,
            platform=result.platform,
            type=result.type,
            title=result.title,
            content=result.content,
            author=result.author,
            authorId=result.author_id,
            likes=result.get_metrics().get("likes", 0),
            comments=result.get_metrics().get("comments", 0),
            shares=result.get_metrics().get("shares", 0),
            url=result.url,
            imageUrls=result.get_image_urls(),
            videoUrl=result.video_url,
            timestamp=result.timestamp,
            taskId=result.task_id,
            tags=result.get_tags(),
            metrics=result.get_metrics(),
            sentiment=result.sentiment,
            createdAt=result.created_at
        )
        
        return ApiResponse(success=True, data=detail)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting result detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{result_id}", response_model=ApiResponse[dict])
async def delete_result(result_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a single result"""
    try:
        success = await ResultService.delete_result(db, result_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return ApiResponse(
            success=True,
            message="Result deleted successfully",
            data={"resultId": result_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-delete", response_model=ApiResponse[BatchDeleteResponse])
async def batch_delete_results(
    request: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Batch delete results"""
    try:
        deleted, failed = await ResultService.batch_delete_results(db, request.ids)
        
        response_data = BatchDeleteResponse(deleted=deleted, failed=failed)
        return ApiResponse(success=True, data=response_data)
        
    except Exception as e:
        logger.error(f"Error batch deleting results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_results(
    format: str = Query("csv", regex="^(csv|json|excel)$"),
    ids: Optional[str] = None,
    platform: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Export results in various formats"""
    try:
        # Parse IDs if provided
        result_ids = ids.split(",") if ids else None
        
        # Get results
        if result_ids:
            # Fetch specific results
            items = []
            for result_id in result_ids:
                result = await ResultService.get_result_by_id(db, result_id)
                if result:
                    items.append(result)
        else:
            # Get all results matching filters
            items, _ = await ResultService.get_results(
                db,
                page=1,
                page_size=10000,  # Get many results for export
                platform=platform,
                keyword=keyword
            )
        
        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Platform", "Type", "Title", "Content", "Author",
                "URL", "Likes", "Comments", "Shares", "Timestamp"
            ])
            
            # Write data
            for item in items:
                metrics = item.get_metrics()
                writer.writerow([
                    item.id,
                    item.platform,
                    item.type,
                    item.title or "",
                    item.content,
                    item.author or "",
                    item.url,
                    metrics.get("likes", 0),
                    metrics.get("comments", 0),
                    metrics.get("shares", 0),
                    item.timestamp.isoformat()
                ])
            
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=results.csv"}
            )
            
        elif format == "json":
            # Generate JSON
            data = []
            for item in items:
                data.append({
                    "id": item.id,
                    "platform": item.platform,
                    "type": item.type,
                    "title": item.title,
                    "content": item.content,
                    "author": item.author,
                    "url": item.url,
                    "metrics": item.get_metrics(),
                    "imageUrls": item.get_image_urls(),
                    "videoUrl": item.video_url,
                    "timestamp": item.timestamp.isoformat(),
                    "tags": item.get_tags()
                })
            
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            return StreamingResponse(
                iter([json_str]),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=results.json"}
            )
        
        else:
            # Excel format would require openpyxl
            raise HTTPException(status_code=501, detail="Excel export not yet implemented")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        raise HTTPException(status_code=500, detail=str(e))
