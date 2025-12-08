# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Result-related schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ResultBase(BaseModel):
    """Base result schema"""
    platform: str
    type: str = Field(description="note|video|comment|post")
    title: Optional[str] = None
    content: str
    author: Optional[str] = None
    url: str


class ResultCreate(ResultBase):
    """Result creation schema"""
    task_id: str = Field(alias="taskId")
    author_id: Optional[str] = Field(alias="authorId", default=None)
    image_urls: list[str] = Field(alias="imageUrls", default_factory=list)
    video_url: Optional[str] = Field(alias="videoUrl", default=None)
    metrics: dict = Field(default_factory=dict)
    timestamp: datetime
    tags: list[str] = Field(default_factory=list)
    sentiment: Optional[str] = None
    
    class Config:
        populate_by_name = True


class ResultListItem(BaseModel):
    """Result list item schema"""
    id: str
    platform: str
    type: str
    title: Optional[str] = None
    content: str
    author: Optional[str] = None
    likes: int = 0
    comments: int = 0
    shares: int = 0
    url: str
    image_urls: list[str] = Field(alias="imageUrls", default_factory=list)
    timestamp: datetime
    task_id: str = Field(alias="taskId")
    tags: list[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        from_attributes = True


class ResultDetail(ResultListItem):
    """Detailed result schema"""
    author_id: Optional[str] = Field(alias="authorId", default=None)
    video_url: Optional[str] = Field(alias="videoUrl", default=None)
    metrics: dict = Field(default_factory=dict)
    sentiment: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class BatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: list[str] = Field(description="List of result IDs to delete")


class BatchDeleteResponse(BaseModel):
    """Batch delete response"""
    deleted: int = Field(description="Number of items deleted")
    failed: int = Field(description="Number of items that failed to delete")
