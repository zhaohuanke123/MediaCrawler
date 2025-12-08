# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""WebSocket endpoints"""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/task/{task_id}")
async def websocket_task_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time task updates"""
    await websocket_manager.connect(task_id, websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "data": {
                "taskId": task_id,
                "message": "Connected to task updates"
            }
        })
        
        # Keep connection alive
        while True:
            # Wait for messages from client (if any)
            try:
                data = await websocket.receive_text()
                # Echo back for testing
                logger.debug(f"Received message from client: {data}")
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
    finally:
        websocket_manager.disconnect(task_id, websocket)
