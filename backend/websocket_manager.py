"""
WebSocket Connection Manager
Manages real-time connections for progress updates
"""

from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"✅ Client {client_id} connected via WebSocket")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"👋 Client {client_id} disconnected")
    
    async def send_personal_message(self, message: str, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                print(f"❌ Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"❌ Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_progress_update(
        self,
        client_id: str,
        project_id: int,
        progress: int,
        status: str,
        message: str = ""
    ):
        """Send progress update to client"""
        update = {
            "type": "progress",
            "project_id": project_id,
            "progress": progress,
            "status": status,
            "message": message
        }
        await self.send_personal_message(json.dumps(update), client_id)
    
    async def send_completion_notification(
        self,
        client_id: str,
        project_id: int,
        output_path: str
    ):
        """Send completion notification"""
        notification = {
            "type": "completed",
            "project_id": project_id,
            "output_path": output_path
        }
        await self.send_personal_message(json.dumps(notification), client_id)
    
    async def send_error_notification(
        self,
        client_id: str,
        project_id: int,
        error: str
    ):
        """Send error notification"""
        notification = {
            "type": "error",
            "project_id": project_id,
            "error": error
        }
        await self.send_personal_message(json.dumps(notification), client_id)


# Global connection manager instance
manager = ConnectionManager()

