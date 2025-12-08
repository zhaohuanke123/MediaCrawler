# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Task model for crawler tasks"""

import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy import Text as JSONText

from .database import Base
from app.config import settings

# Use appropriate JSON type based on database
if settings.DATABASE_TYPE == "mysql":
    JSONType = MySQLJSON
else:
    # SQLite doesn't have native JSON, we'll use Text and serialize/deserialize
    JSONType = JSONText


class Task(Base):
    """Crawler task model"""
    __tablename__ = "crawler_tasks"
    
    id = Column(String(36), primary_key=True)  # UUID
    platform = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Platform: xhs|douyin|kuaishou|bilibili|weibo|tieba|zhihu"
    )
    type = Column(
        String(20),
        nullable=False,
        comment="Crawler type: search|detail|creator|comment"
    )
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="Task status: pending|running|paused|completed|failed|cancelled"
    )
    config = Column(JSONText, nullable=False, comment="Task configuration JSON")
    start_time = Column(DateTime, nullable=True, index=True)
    end_time = Column(DateTime, nullable=True)
    items_collected = Column(Integer, default=0, comment="Number of items collected")
    progress = Column(Integer, default=0, comment="Progress percentage 0-100")
    errors = Column(Text, nullable=True, comment="Error messages JSON array")
    logs = Column(Text, nullable=True, comment="Task logs JSON array")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Task(id={self.id}, platform={self.platform}, status={self.status})>"
    
    def get_config(self):
        """Get config as dict"""
        if isinstance(self.config, str):
            return json.loads(self.config)
        return self.config or {}
    
    def set_config(self, config_dict):
        """Set config from dict"""
        self.config = json.dumps(config_dict)
    
    def get_errors(self):
        """Get errors as list"""
        if not self.errors:
            return []
        if isinstance(self.errors, str):
            return json.loads(self.errors)
        return self.errors
    
    def add_error(self, error_msg: str):
        """Add an error message"""
        errors = self.get_errors()
        errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": error_msg
        })
        self.errors = json.dumps(errors)
    
    def get_logs(self):
        """Get logs as list"""
        if not self.logs:
            return []
        if isinstance(self.logs, str):
            return json.loads(self.logs)
        return self.logs
    
    def add_log(self, level: str, message: str):
        """Add a log entry"""
        logs = self.get_logs()
        logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message
        })
        # Keep only last 100 logs
        if len(logs) > 100:
            logs = logs[-100:]
        self.logs = json.dumps(logs)
