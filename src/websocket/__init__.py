"""WebSocket support."""
from src.websocket.manager import manager
from src.websocket.endpoints import router

__all__ = ["manager", "router"]
