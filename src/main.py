"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import strawberry
from strawberry.fastapi import GraphQLRouter

from src.config import get_settings
from src.api.v1 import text, image, audio, document, management, webhooks, admin, streaming, analytics, teams, batch, fine_tuning, ml_predictions
from src.graphql.schema import schema
from src.graphql.context import get_graphql_context
from src.websocket import router as websocket_router
from src.core.database import init_db, close_db
from src.core.redis_client import init_redis, close_redis
from src.middleware.logging import LoggingMiddleware
from src.middleware.error_handler import ErrorHandlerMiddleware
from src.middleware.rate_limit_headers import RateLimitHeadersMiddleware
from src.middleware.security_headers import SecurityHeadersMiddleware
from src.middleware.metrics import MetricsMiddleware
from src.middleware.audit_log import AuditLogMiddleware
from src.api.v1 import metrics
from src.utils.logging_config import setup_logging

settings = get_settings()

# Setup logging
setup_logging(log_level=settings.app_env == "development" and "DEBUG" or "INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    await init_redis()
    yield
    # Shutdown
    await close_db()
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    description="AI API Service Platform for Developers",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware (order matters - first added is outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(AuditLogMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# GraphQL Router
graphql_app = GraphQLRouter(schema, context_getter=get_graphql_context)
app.include_router(graphql_app, prefix="/graphql")

# WebSocket Router
app.include_router(websocket_router)

# Include routers
app.include_router(text.router, prefix="/api")
app.include_router(image.router, prefix="/api")
app.include_router(audio.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(management.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(streaming.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(batch.router, prefix="/api")
app.include_router(fine_tuning.router, prefix="/api")
app.include_router(ml_predictions.router, prefix="/api")

# Metrics endpoint
app.include_router(metrics.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "2.0.0",
        "docs": "/docs",
        "status": "operational",
        "features": [
            "Text & Image Generation",
            "Batch Processing (up to 100 requests)",
            "AI Model Fine-Tuning",
            "ML-based Cost Prediction",
            "Real-time WebSocket Updates",
            "GraphQL API",
            "Usage Analytics & Insights"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development"
    )
