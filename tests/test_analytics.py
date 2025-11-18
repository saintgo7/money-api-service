"""Tests for analytics API."""
import pytest
from httpx import AsyncClient
from fastapi import status
from datetime import datetime, timedelta


class TestAnalyticsAPI:
    """Test analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_usage_analytics_24h(self, client: AsyncClient, api_key: str):
        """Test getting 24h usage analytics."""
        response = await client.get(
            "/api/v1/analytics/usage?period=24h",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "period" in data
        assert data["period"] == "24h"
        assert "usage_over_time" in data
        assert "endpoint_breakdown" in data
        assert "cost_breakdown" in data
        assert "performance_metrics" in data

    @pytest.mark.asyncio
    async def test_get_usage_analytics_7d(self, client: AsyncClient, api_key: str):
        """Test getting 7 days usage analytics."""
        response = await client.get(
            "/api/v1/analytics/usage?period=7d",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["period"] == "7d"

    @pytest.mark.asyncio
    async def test_get_usage_analytics_30d(self, client: AsyncClient, api_key: str):
        """Test getting 30 days usage analytics."""
        response = await client.get(
            "/api/v1/analytics/usage?period=30d",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["period"] == "30d"

    @pytest.mark.asyncio
    async def test_get_usage_analytics_invalid_period(self, client: AsyncClient, api_key: str):
        """Test invalid period parameter."""
        response = await client.get(
            "/api/v1/analytics/usage?period=90d",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_usage_over_time_structure(self, client: AsyncClient, api_key: str):
        """Test usage over time data structure."""
        response = await client.get(
            "/api/v1/analytics/usage?period=7d",
            headers={"X-API-Key": api_key}
        )

        data = response.json()
        usage_over_time = data["usage_over_time"]

        if len(usage_over_time) > 0:
            point = usage_over_time[0]
            assert "timestamp" in point
            assert "requests" in point
            assert "cost" in point
            assert "tokens" in point

    @pytest.mark.asyncio
    async def test_endpoint_breakdown_structure(self, client: AsyncClient, api_key: str):
        """Test endpoint breakdown data structure."""
        response = await client.get(
            "/api/v1/analytics/usage?period=7d",
            headers={"X-API-Key": api_key}
        )

        data = response.json()
        endpoint_breakdown = data["endpoint_breakdown"]

        if len(endpoint_breakdown) > 0:
            item = endpoint_breakdown[0]
            assert "endpoint" in item
            assert "requests" in item
            assert "cost" in item
            assert "percentage" in item
            assert 0 <= item["percentage"] <= 100

    @pytest.mark.asyncio
    async def test_cost_breakdown_structure(self, client: AsyncClient, api_key: str):
        """Test cost breakdown data structure."""
        response = await client.get(
            "/api/v1/analytics/usage?period=7d",
            headers={"X-API-Key": api_key}
        )

        data = response.json()
        cost_breakdown = data["cost_breakdown"]

        if len(cost_breakdown) > 0:
            item = cost_breakdown[0]
            assert "category" in item
            assert "text" in item
            assert "image" in item
            assert "audio" in item
            assert "document" in item
            assert "total" in item
            # Total should equal sum of parts
            assert item["total"] == item["text"] + item["image"] + item["audio"] + item["document"]

    @pytest.mark.asyncio
    async def test_performance_metrics_structure(self, client: AsyncClient, api_key: str):
        """Test performance metrics data structure."""
        response = await client.get(
            "/api/v1/analytics/usage?period=7d",
            headers={"X-API-Key": api_key}
        )

        data = response.json()
        performance_metrics = data["performance_metrics"]

        if len(performance_metrics) > 0:
            metric = performance_metrics[0]
            assert "timestamp" in metric
            assert "requests" in metric
            assert "avg_latency" in metric
            assert "p95_latency" in metric
            assert "p99_latency" in metric
            assert "error_rate" in metric
            assert 0 <= metric["error_rate"] <= 1

    @pytest.mark.asyncio
    async def test_get_analytics_summary(self, client: AsyncClient, api_key: str):
        """Test analytics summary endpoint."""
        response = await client.get(
            "/api/v1/analytics/summary",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_requests" in data
        assert "total_cost" in data
        assert "avg_latency" in data
        assert "error_rate" in data
        assert "period" in data
        assert data["period"] == "24h"

    @pytest.mark.asyncio
    async def test_analytics_unauthorized(self, client: AsyncClient):
        """Test analytics without authentication."""
        response = await client.get("/api/v1/analytics/usage")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_analytics_with_usage_data(self, client: AsyncClient, api_key: str, db_session):
        """Test analytics with actual usage data."""
        from src.models.usage import Usage
        from src.models.user import User
        import uuid

        # Get user
        user_id = api_key_data["user_id"]  # Would need to extract from fixture

        # Create sample usage data
        for i in range(10):
            usage = Usage(
                id=uuid.uuid4(),
                user_id=user_id,
                endpoint="/api/v1/text/completions",
                method="POST",
                tokens=100,
                cost=0.01,
                latency=150,
                status_code=200,
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            db_session.add(usage)

        await db_session.commit()

        # Get analytics
        response = await client.get(
            "/api/v1/analytics/usage?period=24h",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["usage_over_time"]) > 0
        assert len(data["endpoint_breakdown"]) > 0

    @pytest.mark.asyncio
    async def test_analytics_performance(self, client: AsyncClient, api_key: str):
        """Test analytics endpoint performance."""
        import time

        start_time = time.time()
        response = await client.get(
            "/api/v1/analytics/usage?period=30d",
            headers={"X-API-Key": api_key}
        )
        elapsed_time = time.time() - start_time

        assert response.status_code == status.HTTP_200_OK
        # Should respond in less than 2 seconds
        assert elapsed_time < 2.0

    @pytest.mark.asyncio
    async def test_analytics_caching(self, client: AsyncClient, api_key: str):
        """Test that analytics results are cached."""
        # First request
        response1 = await client.get(
            "/api/v1/analytics/usage?period=7d",
            headers={"X-API-Key": api_key}
        )

        # Second request (should be faster due to cache)
        import time
        start_time = time.time()
        response2 = await client.get(
            "/api/v1/analytics/usage?period=7d",
            headers={"X-API-Key": api_key}
        )
        elapsed_time = time.time() - start_time

        assert response1.json() == response2.json()
        # Cached response should be very fast
        assert elapsed_time < 0.5
