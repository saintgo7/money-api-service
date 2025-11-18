"""WebSocket connection manager."""
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        # Map of user_id to set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket client.

        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a WebSocket client.

        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        logger.info(f"WebSocket disconnected: {user_id}")

    async def send_personal_message(
        self,
        message: dict,
        user_id: str
    ):
        """Send message to specific user's connections.

        Args:
            message: Message to send
            user_id: User identifier
        """
        if user_id not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                disconnected.add(connection)

        # Clean up disconnected sockets
        for connection in disconnected:
            self.disconnect(connection, user_id)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
        """
        for user_id, connections in self.active_connections.items():
            for connection in list(connections):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting: {str(e)}")
                    self.disconnect(connection, user_id)

    async def send_usage_update(
        self,
        user_id: str,
        usage_data: dict
    ):
        """Send real-time usage update to user.

        Args:
            user_id: User identifier
            usage_data: Usage data to send
        """
        message = {
            "type": "usage_update",
            "data": usage_data,
            "timestamp": usage_data.get("timestamp")
        }
        await self.send_personal_message(message, user_id)

    async def send_credit_alert(
        self,
        user_id: str,
        balance: float,
        threshold: float
    ):
        """Send credit balance alert.

        Args:
            user_id: User identifier
            balance: Current balance
            threshold: Alert threshold
        """
        message = {
            "type": "credit_alert",
            "data": {
                "balance": balance,
                "threshold": threshold,
                "severity": "warning" if balance > 1.0 else "critical"
            }
        }
        await self.send_personal_message(message, user_id)

    async def send_api_key_event(
        self,
        user_id: str,
        event: str,
        api_key_data: dict
    ):
        """Send API key event notification.

        Args:
            user_id: User identifier
            event: Event type (created, revoked, etc.)
            api_key_data: API key data
        """
        message = {
            "type": "api_key_event",
            "event": event,
            "data": api_key_data
        }
        await self.send_personal_message(message, user_id)

    def get_connection_count(self, user_id: str = None) -> int:
        """Get number of active connections.

        Args:
            user_id: Optional user ID to get count for specific user

        Returns:
            Connection count
        """
        if user_id:
            return len(self.active_connections.get(user_id, set()))

        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()
