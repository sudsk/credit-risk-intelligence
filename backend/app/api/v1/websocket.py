"""
WebSocket endpoint for real-time updates
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint handler"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            msg_type = message.get("type")
            
            if msg_type == "ping":
                # Respond to heartbeat
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": message.get("timestamp")},
                    websocket
                )
            
            elif msg_type == "subscribe":
                # Handle subscription (future implementation)
                await manager.send_personal_message(
                    {"type": "subscribed", "channels": message.get("channels", [])},
                    websocket
                )
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Utility function to broadcast updates from services
async def broadcast_update(update_type: str, data: dict):
    """
    Broadcast update to all connected clients
    Called by services when data changes
    """
    await manager.broadcast({
        "type": update_type,
        "data": data
    })
