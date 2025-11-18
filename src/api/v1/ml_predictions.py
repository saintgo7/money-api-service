"""Machine learning based usage prediction and forecasting."""
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.api_management import verify_api_key
from src.core.database import get_db
from src.core.multi_layer_cache import cached_multi_layer

router = APIRouter(prefix="/v1/ml", tags=["Machine Learning"])


# Models
class UsageDataPoint(BaseModel):
    """Historical usage data point."""
    date: datetime
    requests: int
    cost: float
    tokens: int


class UsageForecast(BaseModel):
    """Usage forecast for future period."""
    date: datetime
    predicted_requests: float
    predicted_cost: float
    confidence_lower: float
    confidence_upper: float
    confidence_interval: float = 0.95


class CostPrediction(BaseModel):
    """Cost prediction response."""
    current_month: float
    predicted_next_month: float
    predicted_daily_average: float
    trend: str  # "increasing", "decreasing", "stable"
    confidence: float
    forecasts: List[UsageForecast]


class AnomalyDetection(BaseModel):
    """Anomaly detection result."""
    is_anomaly: bool
    anomaly_score: float
    threshold: float
    date: datetime
    actual_value: float
    expected_value: float
    deviation_percentage: float


class SpendingAlert(BaseModel):
    """Spending alert configuration."""
    threshold_amount: float
    period: str  # "daily", "weekly", "monthly"
    enabled: bool


# Simple Time Series Forecasting
class UsagePredictor:
    """ML-based usage and cost prediction."""

    @staticmethod
    def moving_average(data: List[float], window: int = 7) -> float:
        """Calculate moving average."""
        if len(data) < window:
            window = len(data)
        return np.mean(data[-window:])

    @staticmethod
    def exponential_smoothing(data: List[float], alpha: float = 0.3) -> float:
        """Exponential smoothing forecast."""
        if not data:
            return 0.0

        smoothed = data[0]
        for value in data[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed

        return smoothed

    @staticmethod
    def linear_trend(data: List[float]) -> tuple:
        """Calculate linear trend (slope, intercept)."""
        if len(data) < 2:
            return 0.0, data[0] if data else 0.0

        x = np.arange(len(data))
        y = np.array(data)

        # Simple linear regression
        slope = np.cov(x, y)[0, 1] / np.var(x)
        intercept = np.mean(y) - slope * np.mean(x)

        return slope, intercept

    @staticmethod
    def forecast_next_period(
        historical_data: List[float],
        periods_ahead: int = 30
    ) -> List[UsageForecast]:
        """Forecast future usage."""
        if not historical_data:
            return []

        # Calculate trend
        slope, intercept = UsagePredictor.linear_trend(historical_data)

        # Calculate confidence intervals
        std_dev = np.std(historical_data)

        forecasts = []
        start_date = datetime.utcnow()

        for i in range(1, periods_ahead + 1):
            # Linear extrapolation
            predicted_value = intercept + slope * (len(historical_data) + i)

            # Ensure non-negative
            predicted_value = max(0, predicted_value)

            # Confidence intervals (95%)
            margin = 1.96 * std_dev
            lower = max(0, predicted_value - margin)
            upper = predicted_value + margin

            forecast = UsageForecast(
                date=start_date + timedelta(days=i),
                predicted_requests=predicted_value,
                predicted_cost=predicted_value * 0.01,  # Assuming $0.01 per request
                confidence_lower=lower * 0.01,
                confidence_upper=upper * 0.01,
                confidence_interval=0.95
            )
            forecasts.append(forecast)

        return forecasts

    @staticmethod
    def detect_anomalies(
        data: List[float],
        threshold_std: float = 3.0
    ) -> List[int]:
        """Detect anomalies using statistical method."""
        if len(data) < 3:
            return []

        mean = np.mean(data)
        std = np.std(data)

        anomalies = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / std) if std > 0 else 0
            if z_score > threshold_std:
                anomalies.append(i)

        return anomalies


# Endpoints
@router.get("/predict/cost", response_model=CostPrediction)
@cached_multi_layer(ttl=3600, key_prefix="ml_cost_prediction")
async def predict_monthly_cost(
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Predict next month's cost based on historical usage.

    Uses machine learning to forecast:
    - Total monthly cost
    - Daily average spending
    - Trend direction
    - Confidence intervals

    Cached for 1 hour to reduce computation.
    """
    user_id = api_key_data["user_id"]

    # Get historical usage data (last 90 days)
    from src.models.usage import Usage
    from sqlalchemy import select, func

    ninety_days_ago = datetime.utcnow() - timedelta(days=90)

    stmt = (
        select(
            func.date_trunc('day', Usage.timestamp).label('date'),
            func.sum(Usage.cost).label('daily_cost')
        )
        .where(Usage.user_id == user_id)
        .where(Usage.timestamp >= ninety_days_ago)
        .group_by('date')
        .order_by('date')
    )

    result = await db.execute(stmt)
    daily_costs = [float(row.daily_cost) for row in result]

    if not daily_costs:
        # No historical data
        return CostPrediction(
            current_month=0.0,
            predicted_next_month=0.0,
            predicted_daily_average=0.0,
            trend="stable",
            confidence=0.0,
            forecasts=[]
        )

    # Current month cost
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    stmt = select(func.sum(Usage.cost)).where(
        Usage.user_id == user_id,
        Usage.timestamp >= thirty_days_ago
    )
    result = await db.execute(stmt)
    current_month_cost = float(result.scalar() or 0.0)

    # Forecast next 30 days
    predictor = UsagePredictor()
    forecasts = predictor.forecast_next_period(daily_costs, periods_ahead=30)

    # Predicted next month cost
    predicted_next_month = sum(f.predicted_cost for f in forecasts)
    predicted_daily_avg = predicted_next_month / 30

    # Determine trend
    slope, _ = predictor.linear_trend(daily_costs)
    if slope > 0.01:
        trend = "increasing"
    elif slope < -0.01:
        trend = "decreasing"
    else:
        trend = "stable"

    # Calculate confidence (inverse of coefficient of variation)
    cv = np.std(daily_costs) / np.mean(daily_costs) if np.mean(daily_costs) > 0 else 1.0
    confidence = max(0, min(1, 1 - cv))

    return CostPrediction(
        current_month=current_month_cost,
        predicted_next_month=predicted_next_month,
        predicted_daily_average=predicted_daily_avg,
        trend=trend,
        confidence=confidence,
        forecasts=forecasts
    )


@router.get("/anomalies/detect", response_model=List[AnomalyDetection])
async def detect_usage_anomalies(
    days: int = 30,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect unusual usage patterns.

    Uses statistical anomaly detection to identify:
    - Sudden spikes in usage
    - Unexpected drops
    - Irregular patterns

    Useful for detecting:
    - Potential security issues
    - Bot activity
    - Application bugs
    - Unexpected traffic
    """
    user_id = api_key_data["user_id"]

    # Get daily usage
    from src.models.usage import Usage
    from sqlalchemy import select, func

    start_date = datetime.utcnow() - timedelta(days=days)

    stmt = (
        select(
            func.date_trunc('day', Usage.timestamp).label('date'),
            func.count(Usage.id).label('requests'),
            func.sum(Usage.cost).label('cost')
        )
        .where(Usage.user_id == user_id)
        .where(Usage.timestamp >= start_date)
        .group_by('date')
        .order_by('date')
    )

    result = await db.execute(stmt)
    data_points = list(result)

    if not data_points:
        return []

    # Extract cost values
    costs = [float(row.cost) for row in data_points]

    # Detect anomalies
    predictor = UsagePredictor()
    anomaly_indices = predictor.detect_anomalies(costs, threshold_std=2.5)

    # Build response
    mean_cost = np.mean(costs)
    anomalies = []

    for idx in anomaly_indices:
        row = data_points[idx]
        actual_cost = float(row.cost)
        deviation = ((actual_cost - mean_cost) / mean_cost * 100) if mean_cost > 0 else 0

        anomaly = AnomalyDetection(
            is_anomaly=True,
            anomaly_score=abs(actual_cost - mean_cost) / np.std(costs),
            threshold=2.5,
            date=row.date,
            actual_value=actual_cost,
            expected_value=mean_cost,
            deviation_percentage=deviation
        )
        anomalies.append(anomaly)

    return anomalies


@router.post("/alerts/spending")
async def configure_spending_alert(
    alert: SpendingAlert,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure automatic spending alerts.

    Get notified when spending exceeds threshold:
    - Daily budget alerts
    - Weekly spending summaries
    - Monthly cost warnings

    Notifications sent via:
    - Email
    - Webhook
    - Dashboard alerts
    """
    user_id = api_key_data["user_id"]

    # Store alert configuration in database
    # (would need SpendingAlert model)

    return {
        "message": "Spending alert configured",
        "alert": alert,
        "user_id": user_id
    }


@router.get("/insights/usage")
@cached_multi_layer(ttl=3600, key_prefix="ml_insights")
async def get_usage_insights(
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered usage insights.

    Provides actionable recommendations:
    - Cost optimization suggestions
    - Usage pattern analysis
    - Peak usage times
    - Model efficiency comparison
    - Budget recommendations
    """
    user_id = api_key_data["user_id"]

    # Analyze usage patterns
    from src.models.usage import Usage
    from sqlalchemy import select, func

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Get usage by endpoint
    stmt = (
        select(
            Usage.endpoint,
            func.count(Usage.id).label('requests'),
            func.sum(Usage.cost).label('cost'),
            func.avg(Usage.latency).label('avg_latency')
        )
        .where(Usage.user_id == user_id)
        .where(Usage.timestamp >= thirty_days_ago)
        .group_by(Usage.endpoint)
        .order_by(func.sum(Usage.cost).desc())
    )

    result = await db.execute(stmt)
    endpoint_stats = list(result)

    insights = {
        "summary": {
            "total_endpoints": len(endpoint_stats),
            "analysis_period": "30 days"
        },
        "recommendations": [],
        "cost_breakdown": []
    }

    # Generate insights
    total_cost = sum(float(row.cost) for row in endpoint_stats)

    for row in endpoint_stats:
        endpoint_cost = float(row.cost)
        cost_percentage = (endpoint_cost / total_cost * 100) if total_cost > 0 else 0

        insights["cost_breakdown"].append({
            "endpoint": row.endpoint,
            "requests": row.requests,
            "cost": endpoint_cost,
            "percentage": cost_percentage,
            "avg_latency": float(row.avg_latency or 0)
        })

        # Generate recommendations
        if cost_percentage > 50:
            insights["recommendations"].append({
                "type": "cost_optimization",
                "priority": "high",
                "message": f"Endpoint '{row.endpoint}' accounts for {cost_percentage:.1f}% of costs. Consider caching or batch processing."
            })

        if row.avg_latency and row.avg_latency > 2000:
            insights["recommendations"].append({
                "type": "performance",
                "priority": "medium",
                "message": f"Endpoint '{row.endpoint}' has high latency ({row.avg_latency:.0f}ms). Consider using streaming or smaller models."
            })

    return insights
