# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Task-related schemas"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class TaskProgress(BaseModel):
    """Task progress information"""
    task_id: str = Field(alias="taskId")
    progress: int = Field(description="Progress percentage 0-100")
    status: str = Field(description="Current task status")
    items_collected: int = Field(alias="itemsCollected")
    estimated_remaining: Optional[int] = Field(alias="estimatedRemaining", default=None)
    speed: Optional[float] = Field(default=None, description="Items per minute")
    current_page: Optional[int] = Field(alias="currentPage", default=None)
    
    class Config:
        populate_by_name = True


class TaskLog(BaseModel):
    """Task log entry"""
    timestamp: str
    level: str = Field(description="INFO|WARNING|ERROR|SUCCESS")
    message: str


class TaskBase(BaseModel):
    """Base task schema"""
    platform: str = Field(description="Platform: xhs|douyin|kuaishou|bilibili|weibo|tieba|zhihu")
    type: str = Field(description="Crawler type: search|detail|creator|comment")
    config: dict = Field(description="Task configuration")


class TaskCreate(TaskBase):
    """Task creation schema"""
    pass


class TaskResponse(TaskBase):
    """Task response schema"""
    id: str
    status: str
    start_time: Optional[datetime] = Field(alias="startTime", default=None)
    end_time: Optional[datetime] = Field(alias="endTime", default=None)
    items_collected: int = Field(alias="itemsCollected", default=0)
    progress: int = Field(default=0)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class TaskDetail(TaskResponse):
    """Detailed task response with logs and errors"""
    duration: Optional[int] = Field(default=None, description="Duration in seconds")
    logs: list[TaskLog] = Field(default_factory=list)
    errors: list[dict] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        from_attributes = True


class TaskListItem(BaseModel):
    """Task list item schema"""
    id: str
    name: Optional[str] = None
    platform: str
    type: str = Field(alias="crawlerType")
    status: str
    start_time: Optional[datetime] = Field(alias="startTime", default=None)
    estimated_time: Optional[int] = Field(alias="estimatedTime", default=None)
    progress: int
    items_collected: int = Field(alias="itemsCollected")
    config: dict
    created_at: datetime = Field(alias="createdAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True
