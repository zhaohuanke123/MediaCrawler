# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Statistics model"""

import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey

from .database import Base


class Statistics(Base):
    """Statistics model"""
    __tablename__ = "crawler_statistics"
    
    id = Column(String(36), primary_key=True)  # UUID
    task_id = Column(String(36), ForeignKey("crawler_tasks.id"), nullable=False, index=True)
    platform = Column(String(20), nullable=False, index=True)
    tasks_completed = Column(Integer, default=0)
    results_collected = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)
    top_keywords = Column(Text, nullable=True, comment="JSON array of top keywords")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<Statistics(id={self.id}, platform={self.platform}, results={self.results_collected})>"
    
    def get_top_keywords(self):
        """Get top keywords as list"""
        if not self.top_keywords:
            return []
        if isinstance(self.top_keywords, str):
            return json.loads(self.top_keywords)
        return self.top_keywords
    
    def set_top_keywords(self, keywords: list):
        """Set top keywords from list"""
        self.top_keywords = json.dumps(keywords)
