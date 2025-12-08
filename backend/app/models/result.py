# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Result model for crawler results"""

import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from backend.app.models.database import Base

# Use Text for JSON storage in SQLite
JSONType = Text


class Result(Base):
    """Crawler result model"""
    __tablename__ = "crawler_results"
    
    id = Column(String(36), primary_key=True)  # UUID
    task_id = Column(String(36), ForeignKey("crawler_tasks.id"), nullable=False, index=True)
    platform = Column(String(20), nullable=False, index=True)
    type = Column(String(20), nullable=False, comment="note|video|comment|post")
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    author = Column(String(255), nullable=True, index=True)
    author_id = Column(String(255), nullable=True)
    url = Column(Text, nullable=False)
    image_urls = Column(Text, nullable=True, comment="JSON array of image URLs")
    video_url = Column(Text, nullable=True)
    metrics = Column(Text, nullable=False, comment="JSON object with likes, comments, shares, views")
    timestamp = Column(DateTime, nullable=False, index=True, comment="Content publish timestamp")
    tags = Column(Text, nullable=True, comment="JSON array of tags")
    sentiment = Column(String(20), nullable=True, comment="positive|neutral|negative")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_platform_timestamp", "platform", "timestamp"),
        Index("idx_task_platform", "task_id", "platform"),
    )
    
    def __repr__(self):
        return f"<Result(id={self.id}, platform={self.platform}, type={self.type})>"
    
    def get_image_urls(self):
        """Get image URLs as list"""
        if not self.image_urls:
            return []
        if isinstance(self.image_urls, str):
            return json.loads(self.image_urls)
        return self.image_urls
    
    def set_image_urls(self, urls: list):
        """Set image URLs from list"""
        self.image_urls = json.dumps(urls)
    
    def get_metrics(self):
        """Get metrics as dict"""
        if isinstance(self.metrics, str):
            return json.loads(self.metrics)
        return self.metrics or {}
    
    def set_metrics(self, metrics_dict: dict):
        """Set metrics from dict"""
        self.metrics = json.dumps(metrics_dict)
    
    def get_tags(self):
        """Get tags as list"""
        if not self.tags:
            return []
        if isinstance(self.tags, str):
            return json.loads(self.tags)
        return self.tags
    
    def set_tags(self, tags_list: list):
        """Set tags from list"""
        self.tags = json.dumps(tags_list)
