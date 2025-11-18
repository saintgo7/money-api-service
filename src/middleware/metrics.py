"""Prometheus metrics middleware."""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram, Gauge
import time


# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress',
    ['method', 'endpoint']
)

api_requests_total = Counter(
    'api_requests_total',
    'Total API requests by user',
    ['user_id', 'api_key_id', 'endpoint']
)

api_request_cost = Histogram(
    'api_request_cost',
    'API request cost in USD',
    ['user_id', 'endpoint']
)

db_pool_connections_in_use = Gauge(
    'db_pool_connections_in_use',
    'Database connections currently in use'
)

db_pool_connections_max = Gauge(
    'db_pool_connections_max',
    'Maximum database connections'
)

redis_cache_hits = Counter(
    'redis_cache_hits_total',
    'Total Redis cache hits',
    ['operation']
)

redis_cache_misses = Counter(
    'redis_cache_misses_total',
    'Total Redis cache misses',
    ['operation']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect Prometheus metrics for all requests."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get route pattern
        endpoint = request.url.path
        if request.path_params:
            # Replace path parameters with placeholders
            for key, value in request.path_params.items():
                endpoint = endpoint.replace(str(value), f"{{{key}}}")

        method = request.method

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)
            status = response.status_code

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()

            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Add custom header with request duration
            response.headers["X-Response-Time"] = f"{duration:.4f}s"

            return response

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
