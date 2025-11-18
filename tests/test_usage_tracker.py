"""Tests for usage tracking."""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from src.core.usage_tracker import UsageTracker


@pytest.mark.asyncio
class TestUsageTracker:
    """Test usage tracker."""

    async def test_record_usage(self, db_session, test_user, test_api_key):
        """Test recording usage."""
        _, api_key = test_api_key
        tracker = UsageTracker(db_session)

        usage = await tracker.record_usage(
            user_id=str(test_user.id),
            api_key_id=str(api_key.id),
            endpoint="/v1/text/completions",
            method="POST",
            tokens=150,
            duration_ms=500,
            status_code=200,
            cost=Decimal("0.00045"),
            metadata={"model": "claude-sonnet"}
        )

        assert usage.tokens == 150
        assert usage.cost == Decimal("0.00045")
        assert usage.endpoint == "/v1/text/completions"

    async def test_get_usage_stats(self, db_session, test_user, test_api_key):
        """Test getting usage statistics."""
        _, api_key = test_api_key
        tracker = UsageTracker(db_session)

        # Record some usage
        for i in range(5):
            await tracker.record_usage(
                user_id=str(test_user.id),
                api_key_id=str(api_key.id),
                endpoint="/v1/text/completions",
                method="POST",
                tokens=100,
                duration_ms=300,
                status_code=200,
                cost=Decimal("0.0003")
            )

        # Get stats
        start_date = datetime.utcnow() - timedelta(days=1)
        stats = await tracker.get_usage_stats(
            user_id=str(test_user.id),
            start_date=start_date
        )

        assert stats["total_requests"] >= 5
        assert stats["total_tokens"] >= 500
        assert "/v1/text/completions" in stats["by_endpoint"]

    async def test_check_credit_balance(self, db_session, test_user):
        """Test checking credit balance."""
        tracker = UsageTracker(db_session)

        # User has 100.00 credits
        has_enough = await tracker.check_credit_balance(
            str(test_user.id),
            Decimal("50.00")
        )
        assert has_enough is True

        has_enough = await tracker.check_credit_balance(
            str(test_user.id),
            Decimal("150.00")
        )
        assert has_enough is False

    async def test_deduct_credits(self, db_session, test_user):
        """Test deducting credits."""
        tracker = UsageTracker(db_session)

        initial_balance = test_user.credit_balance

        await tracker.deduct_credits(
            str(test_user.id),
            Decimal("10.00")
        )

        await db_session.refresh(test_user)
        assert test_user.credit_balance == initial_balance - Decimal("10.00")
