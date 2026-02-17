from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_personal_message(websocket, {
            "type": "connected",
            "data": {"message": "Connected to AITeam WebSocket"}
        })

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

    async def handle_message(self, websocket: WebSocket, data: str):
        try:
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "ping":
                await self.send_personal_message(websocket, {"type": "pong"})
            elif msg_type == "chat":
                # Handle chat message - will be processed by task system
                await self.broadcast({
                    "type": "chat",
                    "data": message.get("data", {})
                })
            else:
                # Echo unknown message types
                await self.send_personal_message(websocket, {
                    "type": "echo",
                    "data": message
                })
        except json.JSONDecodeError:
            await self.send_personal_message(websocket, {
                "type": "error",
                "data": {"message": "Invalid JSON format"}
            })


# Global WebSocket manager
ws_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        ws_manager.disconnect(websocket)
