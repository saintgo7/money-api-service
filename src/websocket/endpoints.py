"""WebSocket endpoints."""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.api_management import APIKeyManager
from src.websocket.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    api_key: str = Query(...)
):
    """
    WebSocket endpoint for real-time updates.

    Connect using your API key:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws?api_key=sk_...');

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('Received:', message);

        // Handle different message types
        switch(message.type) {
            case 'usage_update':
                updateUsageChart(message.data);
                break;
            case 'credit_alert':
                showCreditAlert(message.data);
                break;
            case 'api_key_event':
                refreshAPIKeys();
                break;
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket closed');
    };
    ```

    Message types:
    - usage_update: Real-time API usage updates
    - credit_alert: Low credit balance alerts
    - api_key_event: API key created/revoked events
    - system_message: System-wide announcements
    """
    user_id = None

    try:
        # Verify API key
        async for db in get_db():
            manager_api = APIKeyManager(db)
            key_data = await manager_api.verify_api_key(api_key)

            if not key_data:
                await websocket.close(code=1008, reason="Invalid API key")
                return

            user_id = key_data["user_id"]
            break

        # Connect WebSocket
        await manager.connect(websocket, user_id)

        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "user_id": user_id
        })

        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle ping/pong
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue

                # Handle subscription requests
                if message.get("type") == "subscribe":
                    events = message.get("events", [])
                    await websocket.send_json({
                        "type": "subscribed",
                        "events": events
                    })
                    continue

                # Echo for testing
                if message.get("type") == "echo":
                    await websocket.send_json({
                        "type": "echo",
                        "data": message.get("data")
                    })
                    continue

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected: {user_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if user_id:
            manager.disconnect(websocket, user_id)


@router.websocket("/ws/usage")
async def usage_stream_endpoint(
    websocket: WebSocket,
    api_key: str = Query(...)
):
    """
    WebSocket endpoint for real-time usage streaming.

    Provides live updates of API usage and costs.
    """
    user_id = None

    try:
        # Verify API key
        async for db in get_db():
            manager_api = APIKeyManager(db)
            key_data = await manager_api.verify_api_key(api_key)

            if not key_data:
                await websocket.close(code=1008, reason="Invalid API key")
                return

            user_id = key_data["user_id"]
            break

        await manager.connect(websocket, user_id)

        # Send initial usage stats
        from src.core.usage_tracker import UsageTracker
        from datetime import datetime, timedelta

        async for db in get_db():
            tracker = UsageTracker(db)
            stats = await tracker.get_usage_stats(
                user_id,
                start_date=datetime.utcnow() - timedelta(hours=24)
            )

            await websocket.send_json({
                "type": "initial_stats",
                "data": stats
            })
            break

        # Keep connection alive
        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)

    except Exception as e:
        logger.error(f"Usage stream error: {str(e)}")
        if user_id:
            manager.disconnect(websocket, user_id)
