# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""WebSocket connection manager"""

import logging
from typing import Dict, Set
from datetime import datetime, timezone
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Map of task_id to set of connected websockets
        self.connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        """Connect a websocket for a specific task"""
        await websocket.accept()
        
        if task_id not in self.connections:
            self.connections[task_id] = set()
        
        self.connections[task_id].add(websocket)
        logger.info(f"WebSocket connected for task {task_id}. Total: {len(self.connections[task_id])}")
    
    def disconnect(self, task_id: str, websocket: WebSocket):
        """Disconnect a websocket"""
        if task_id in self.connections:
            self.connections[task_id].discard(websocket)
            
            if not self.connections[task_id]:
                del self.connections[task_id]
            
            logger.info(f"WebSocket disconnected for task {task_id}")
    
    async def broadcast_task_event(self, task_id: str, event_type: str, data: dict):
        """Broadcast an event to all connected clients for a task"""
        if task_id not in self.connections:
            return
        
        message = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "data": data
        }
        
        # Send to all connected clients
        disconnected = set()
        for websocket in self.connections[task_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to websocket: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for websocket in disconnected:
            self.disconnect(task_id, websocket)
    
    async def send_log(self, task_id: str, level: str, message: str):
        """Send a log message to connected clients"""
        await self.broadcast_task_event(
            task_id,
            "task_log",
            {
                "level": level,
                "message": message
            }
        )


# Global websocket manager instance
websocket_manager = WebSocketManager()
