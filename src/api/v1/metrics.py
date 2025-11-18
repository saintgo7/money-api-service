"""Metrics endpoint for Prometheus."""
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Exposes application metrics in Prometheus format.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
