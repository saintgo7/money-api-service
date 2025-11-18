"""Tests for WebSocket endpoints."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


class TestWebSocket:
    """Test WebSocket connections."""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, api_key: str):
        """Test basic WebSocket connection."""
        from src.main import app

        with TestClient(app) as client:
            with client.websocket_connect(f"/ws?api_key={api_key}") as websocket:
                # Send subscription message
                websocket.send_json({
                    "type": "subscribe",
                    "events": ["usage_update"]
                })

                # Should receive confirmation
                data = websocket.receive_json()
                assert data["type"] == "subscribed"

    @pytest.mark.asyncio
    async def test_websocket_usage_updates(self, api_key: str):
        """Test receiving usage updates via WebSocket."""
        from src.main import app
        from src.websocket.manager import manager

        with TestClient(app) as client:
            with client.websocket_connect(f"/ws?api_key={api_key}") as websocket:
                # Subscribe to usage updates
                websocket.send_json({
                    "type": "subscribe",
                    "events": ["usage_update"]
                })

                # Simulate usage update
                await manager.send_usage_update(
                    user_id="test-user-id",
                    usage_data={
                        "requests": 100,
                        "cost": 0.05,
                        "avg_latency": 150
                    }
                )

                # Should receive update
                data = websocket.receive_json()
                assert data["type"] == "usage_update"
                assert "requests" in data["data"]

    @pytest.mark.asyncio
    async def test_websocket_credit_alert(self, api_key: str):
        """Test credit alert via WebSocket."""
        from src.main import app
        from src.websocket.manager import manager

        with TestClient(app) as client:
            with client.websocket_connect(f"/ws?api_key={api_key}") as websocket:
                # Subscribe to alerts
                websocket.send_json({
                    "type": "subscribe",
                    "events": ["credit_alert"]
                })

                # Simulate low credit alert
                await manager.send_credit_alert(
                    user_id="test-user-id",
                    balance=5.0,
                    threshold=10.0
                )

                # Should receive alert
                data = websocket.receive_json()
                assert data["type"] == "credit_alert"
                assert data["data"]["balance"] == 5.0

    @pytest.mark.asyncio
    async def test_websocket_unauthorized(self):
        """Test WebSocket without API key."""
        from src.main import app

        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect):
                with client.websocket_connect("/ws"):
                    pass

    @pytest.mark.asyncio
    async def test_websocket_invalid_api_key(self):
        """Test WebSocket with invalid API key."""
        from src.main import app

        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect):
                with client.websocket_connect("/ws?api_key=invalid"):
                    pass

    @pytest.mark.asyncio
    async def test_websocket_ping_pong(self, api_key: str):
        """Test WebSocket keep-alive ping/pong."""
        from src.main import app

        with TestClient(app) as client:
            with client.websocket_connect(f"/ws?api_key={api_key}") as websocket:
                # Send ping
                websocket.send_json({"type": "ping"})

                # Should receive pong
                data = websocket.receive_json()
                assert data["type"] == "pong"

    @pytest.mark.asyncio
    async def test_websocket_unsubscribe(self, api_key: str):
        """Test unsubscribing from events."""
        from src.main import app

        with TestClient(app) as client:
            with client.websocket_connect(f"/ws?api_key={api_key}") as websocket:
                # Subscribe
                websocket.send_json({
                    "type": "subscribe",
                    "events": ["usage_update"]
                })

                # Unsubscribe
                websocket.send_json({
                    "type": "unsubscribe",
                    "events": ["usage_update"]
                })

                # Should receive confirmation
                data = websocket.receive_json()
                assert data["type"] == "unsubscribed"

    @pytest.mark.asyncio
    async def test_websocket_multiple_clients(self, api_key: str):
        """Test multiple WebSocket connections."""
        from src.main import app
        from src.websocket.manager import manager

        with TestClient(app) as client:
            # Connect two clients
            with client.websocket_connect(f"/ws?api_key={api_key}") as ws1:
                with client.websocket_connect(f"/ws?api_key={api_key}") as ws2:
                    # Both subscribe
                    ws1.send_json({"type": "subscribe", "events": ["usage_update"]})
                    ws2.send_json({"type": "subscribe", "events": ["usage_update"]})

                    # Send message to all
                    await manager.send_personal_message(
                        message={"type": "test", "data": "broadcast"},
                        user_id="test-user-id"
                    )

                    # Both should receive
                    data1 = ws1.receive_json()
                    data2 = ws2.receive_json()
                    assert data1["type"] == "test"
                    assert data2["type"] == "test"

    @pytest.mark.asyncio
    async def test_websocket_usage_stream(self, api_key: str):
        """Test dedicated usage stream endpoint."""
        from src.main import app

        with TestClient(app) as client:
            with client.websocket_connect(f"/ws/usage?api_key={api_key}") as websocket:
                # Should start receiving usage data
                data = websocket.receive_json()
                assert "usage" in data or "timestamp" in data

    @pytest.mark.asyncio
    async def test_websocket_reconnection(self, api_key: str):
        """Test WebSocket reconnection behavior."""
        from src.main import app

        with TestClient(app) as client:
            # First connection
            with client.websocket_connect(f"/ws?api_key={api_key}") as websocket:
                websocket.send_json({"type": "subscribe", "events": ["usage_update"]})
                websocket.close()

            # Reconnect
            with client.websocket_connect(f"/ws?api_key={api_key}") as websocket:
                # Should be able to subscribe again
                websocket.send_json({"type": "subscribe", "events": ["usage_update"]})
                data = websocket.receive_json()
                assert data["type"] == "subscribed"
