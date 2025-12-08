# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Statistics-related schemas"""

from typing import Optional
from pydantic import BaseModel, Field


class StatisticsSummary(BaseModel):
    """Statistics summary schema"""
    total_tasks: int = Field(alias="totalTasks")
    successful_tasks: int = Field(alias="successfulTasks")
    failed_tasks: int = Field(alias="failedTasks")
    total_results: int = Field(alias="totalResults")
    avg_results_per_task: float = Field(alias="avgResultsPerTask")
    total_crawl_time: int = Field(alias="totalCrawlTime", description="Total time in seconds")
    platforms: dict[str, int] = Field(description="Results count per platform")
    
    class Config:
        populate_by_name = True


class PlatformStatistics(BaseModel):
    """Platform-specific statistics"""
    platform: str
    tasks: int
    results: int
    avg_engagement: float = Field(alias="avgEngagement")
    top_keywords: list[str] = Field(alias="topKeywords", default_factory=list)
    growth: float = Field(description="Growth percentage")
    
    class Config:
        populate_by_name = True


class TimelineStatistics(BaseModel):
    """Timeline statistics entry"""
    timestamp: str
    tasks_completed: int = Field(alias="tasksCompleted")
    results_collected: int = Field(alias="resultsCollected")
    avg_processing_time: float = Field(alias="avgProcessingTime")
    
    class Config:
        populate_by_name = True


class KeywordStatistics(BaseModel):
    """Keyword statistics"""
    keyword: str
    frequency: int
    sentiment: str
    trend: str = Field(description="up|down|stable")
    platforms: list[str] = Field(default_factory=list)
    related_keywords: list[str] = Field(alias="relatedKeywords", default_factory=list)
    
    class Config:
        populate_by_name = True
