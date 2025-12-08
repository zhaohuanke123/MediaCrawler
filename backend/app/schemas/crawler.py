# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Crawler-related schemas"""

from typing import Optional, Any
from pydantic import BaseModel, Field


class CrawlerOptions(BaseModel):
    """Crawler execution options"""
    headless: bool = Field(default=True)
    timeout: int = Field(default=30000, description="Timeout in milliseconds")
    proxy: Optional[str] = Field(default=None)
    use_cache: bool = Field(alias="useCache", default=True)
    
    class Config:
        populate_by_name = True


class CrawlerConfig(BaseModel):
    """Crawler configuration"""
    keyword: Optional[str] = None
    pages: int = Field(default=10)
    sort: Optional[str] = Field(default="latest", description="latest|popularity")
    filters: dict = Field(default_factory=dict)


class StartCrawlerRequest(BaseModel):
    """Start crawler request"""
    platform: str = Field(description="xhs|douyin|kuaishou|bilibili|weibo|tieba|zhihu")
    type: str = Field(description="search|profile|video|comment")
    config: CrawlerConfig
    crawler_options: Optional[CrawlerOptions] = Field(alias="crawlerOptions", default=None)
    
    class Config:
        populate_by_name = True


class StartCrawlerResponse(BaseModel):
    """Start crawler response"""
    task_id: str = Field(alias="taskId")
    platform: str
    status: str
    start_time: str = Field(alias="startTime")
    progress: int
    
    class Config:
        populate_by_name = True


class PlatformConfigField(BaseModel):
    """Platform configuration field"""
    name: str
    type: str = Field(description="string|number|boolean|select")
    required: bool = Field(default=False)
    default: Optional[Any] = None
    options: Optional[list[Any]] = None
    description: Optional[str] = None


class PlatformInfo(BaseModel):
    """Platform information"""
    id: str
    name: str
    icon: Optional[str] = None
    description: str
    features: list[str] = Field(description="Supported features like note, comment, etc.")
    config: dict = Field(description="Configuration schema")


class PlatformsResponse(BaseModel):
    """Platforms list response"""
    platforms: list[PlatformInfo] = Field(alias="data")
    
    class Config:
        populate_by_name = True
