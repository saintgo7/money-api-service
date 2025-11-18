"""Database query optimization utilities."""
from sqlalchemy import event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import joinedload, selectinload
import logging
import time

logger = logging.getLogger(__name__)


# Query performance monitoring
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Store query start time."""
    conn.info.setdefault("query_start_time", []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries."""
    total_time = time.time() - conn.info["query_start_time"].pop(-1)

    # Log slow queries (> 1 second)
    if total_time > 1.0:
        logger.warning(
            f"Slow query detected: {total_time:.4f}s",
            extra={
                "query": statement,
                "duration": total_time,
                "parameters": parameters
            }
        )


class QueryOptimizer:
    """Helper class for optimized database queries."""

    @staticmethod
    def eager_load_user_with_keys(stmt):
        """
        Eager load user with API keys to avoid N+1 queries.

        Example:
            stmt = select(User).where(User.id == user_id)
            stmt = QueryOptimizer.eager_load_user_with_keys(stmt)
        """
        return stmt.options(
            selectinload("api_keys")
        )

    @staticmethod
    def eager_load_usage_with_relations(stmt):
        """Eager load usage with user and API key."""
        return stmt.options(
            joinedload("user"),
            joinedload("api_key")
        )

    @staticmethod
    def optimize_pagination(stmt, page: int = 1, page_size: int = 50):
        """
        Add pagination with optimal offset/limit.

        Args:
            stmt: SQLAlchemy statement
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Optimized statement
        """
        offset = (page - 1) * page_size
        return stmt.limit(page_size).offset(offset)

    @staticmethod
    def add_count_query(stmt):
        """
        Create count query from select statement.

        Example:
            stmt = select(User)
            count_stmt = QueryOptimizer.add_count_query(stmt)
        """
        from sqlalchemy import func
        return select(func.count()).select_from(stmt.alias())


# Database connection pool monitoring
class ConnectionPoolMonitor:
    """Monitor database connection pool."""

    @staticmethod
    async def get_pool_status(engine):
        """Get connection pool statistics."""
        pool = engine.pool

        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow(),
        }

    @staticmethod
    async def log_pool_status(engine):
        """Log pool status for monitoring."""
        status = await ConnectionPoolMonitor.get_pool_status(engine)

        logger.info(
            "Connection pool status",
            extra={
                "pool_size": status["size"],
                "checked_in": status["checked_in"],
                "checked_out": status["checked_out"],
                "overflow": status["overflow"],
                "total": status["total"],
            }
        )

        # Warn if pool is nearly exhausted
        if status["checked_out"] / status["total"] > 0.9:
            logger.warning(
                "Connection pool nearly exhausted",
                extra=status
            )


# Index recommendations
RECOMMENDED_INDEXES = """
-- User table
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_plan ON users(plan);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at);

-- API Keys table
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_is_active ON api_keys(is_active);

-- Usage table
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_user_timestamp ON usage(user_id, timestamp);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_endpoint_timestamp ON usage(endpoint, timestamp);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_timestamp ON usage(timestamp);

-- Organizations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orgs_owner_id ON organizations(owner_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_org_members_org_user ON organization_members(organization_id, user_id);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_analytics ON usage(user_id, timestamp, endpoint);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_lookup ON api_keys(user_id, is_active);
"""
