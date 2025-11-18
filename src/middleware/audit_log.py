"""Audit logging middleware."""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log all API requests for audit purposes."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

        # Sensitive endpoints that require audit logging
        self.audit_endpoints = [
            "/api/v1/management/api-keys",
            "/api/v1/admin",
            "/api/v1/teams",
            "/api/v1/billing",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if this endpoint requires audit logging
        should_audit = any(
            request.url.path.startswith(endpoint)
            for endpoint in self.audit_endpoints
        )

        if not should_audit:
            return await call_next(request)

        # Capture request details
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "api_key_prefix": None,
        }

        # Extract API key (first 10 chars only for security)
        api_key = request.headers.get("x-api-key")
        if api_key:
            audit_data["api_key_prefix"] = api_key[:10] + "..."

        # Process request
        response = await call_next(request)

        # Add response details
        audit_data["status_code"] = response.status_code
        audit_data["success"] = 200 <= response.status_code < 400

        # Log audit entry
        if audit_data["success"]:
            logger.info(
                "AUDIT_LOG",
                extra={
                    "audit": audit_data,
                    "event_type": "api_access"
                }
            )
        else:
            logger.warning(
                "AUDIT_LOG_FAILED",
                extra={
                    "audit": audit_data,
                    "event_type": "api_access_failed"
                }
            )

        return response
