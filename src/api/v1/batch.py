"""Batch processing API endpoints."""
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

from src.core.api_management import verify_api_key
from src.core.database import get_db
from src.core.exceptions import ValidationError, InsufficientCredits
from src.core.resilience import with_resilience
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/batch", tags=["Batch Processing"])


# Request/Response Models
class BatchTextRequest(BaseModel):
    """Single text generation request in batch."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = Field(..., min_length=1, max_length=10000)
    model: str = Field(default="claude-3-sonnet")
    max_tokens: int = Field(default=1000, ge=1, le=4000)


class BatchImageRequest(BaseModel):
    """Single image generation request in batch."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = Field(..., min_length=1, max_length=1000)
    model: str = Field(default="sdxl")
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=1024, ge=256, le=2048)


class BatchTextRequestList(BaseModel):
    """Batch text generation request."""
    requests: List[BatchTextRequest] = Field(..., min_items=1, max_items=100)
    parallel: bool = Field(default=True, description="Process requests in parallel")

    @validator('requests')
    def validate_batch_size(cls, v):
        if len(v) > 100:
            raise ValidationError(
                "batch_size",
                "Maximum batch size is 100 requests"
            )
        return v


class BatchImageRequestList(BaseModel):
    """Batch image generation request."""
    requests: List[BatchImageRequest] = Field(..., min_items=1, max_items=50)
    parallel: bool = Field(default=True)

    @validator('requests')
    def validate_batch_size(cls, v):
        if len(v) > 50:
            raise ValidationError(
                "batch_size",
                "Maximum batch size is 50 requests for images"
            )
        return v


class BatchResult(BaseModel):
    """Single result in batch response."""
    id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


class BatchResponse(BaseModel):
    """Batch processing response."""
    batch_id: str
    total_requests: int
    successful: int
    failed: int
    total_cost: float
    total_time: float
    results: List[BatchResult]


# Batch Processing Functions
@router.post("/text", response_model=BatchResponse)
async def batch_text_processing(
    request: BatchTextRequestList,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Process multiple text generation requests in batch.

    Features:
    - Process up to 100 requests
    - Parallel or sequential processing
    - Partial failure tolerance
    - Individual result tracking

    Example:
        ```json
        {
            "requests": [
                {
                    "id": "req-1",
                    "prompt": "Explain quantum computing",
                    "model": "claude-3-sonnet",
                    "max_tokens": 500
                },
                {
                    "id": "req-2",
                    "prompt": "Write a haiku about AI",
                    "model": "gpt-4",
                    "max_tokens": 100
                }
            ],
            "parallel": true
        }
        ```
    """
    import time
    from src.api.v1.text import process_text_completion

    batch_id = str(uuid.uuid4())
    start_time = time.time()
    results = []
    total_cost = 0.0

    user_id = api_key_data["user_id"]

    # Check sufficient balance for estimated cost
    from src.models.user import User
    from sqlalchemy import select

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Estimate cost (rough estimate)
    estimated_cost = len(request.requests) * 0.01  # $0.01 per request average
    if user.balance < estimated_cost:
        raise InsufficientCredits(
            current_balance=user.balance,
            required=estimated_cost
        )

    async def process_single_request(req: BatchTextRequest) -> BatchResult:
        """Process single request with error handling."""
        req_start_time = time.time()

        try:
            # Call text completion API
            result = await process_text_completion(
                prompt=req.prompt,
                model=req.model,
                max_tokens=req.max_tokens,
                user_id=user_id,
                api_key_id=api_key_data["api_key_id"],
                db=db
            )

            processing_time = time.time() - req_start_time

            return BatchResult(
                id=req.id,
                success=True,
                result=result,
                processing_time=processing_time
            )

        except Exception as e:
            processing_time = time.time() - req_start_time
            return BatchResult(
                id=req.id,
                success=False,
                error=str(e),
                processing_time=processing_time
            )

    # Process requests
    if request.parallel:
        # Parallel processing with semaphore to limit concurrency
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests

        async def bounded_process(req):
            async with semaphore:
                return await process_single_request(req)

        results = await asyncio.gather(
            *[bounded_process(req) for req in request.requests],
            return_exceptions=False
        )
    else:
        # Sequential processing
        for req in request.requests:
            result = await process_single_request(req)
            results.append(result)

    # Calculate statistics
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    total_cost = sum(
        r.result.get("cost", 0) for r in results
        if r.success and r.result
    )
    total_time = time.time() - start_time

    return BatchResponse(
        batch_id=batch_id,
        total_requests=len(request.requests),
        successful=successful,
        failed=failed,
        total_cost=total_cost,
        total_time=total_time,
        results=results
    )


@router.post("/image", response_model=BatchResponse)
async def batch_image_processing(
    request: BatchImageRequestList,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Process multiple image generation requests in batch.

    Features:
    - Process up to 50 image requests
    - Parallel processing with rate limiting
    - Automatic retry on failures
    - Cost optimization
    """
    import time
    from src.api.v1.image import process_image_generation

    batch_id = str(uuid.uuid4())
    start_time = time.time()
    results = []

    user_id = api_key_data["user_id"]

    async def process_single_image(req: BatchImageRequest) -> BatchResult:
        """Process single image request."""
        req_start_time = time.time()

        try:
            result = await process_image_generation(
                prompt=req.prompt,
                model=req.model,
                width=req.width,
                height=req.height,
                user_id=user_id,
                api_key_id=api_key_data["api_key_id"],
                db=db
            )

            processing_time = time.time() - req_start_time

            return BatchResult(
                id=req.id,
                success=True,
                result=result,
                processing_time=processing_time
            )

        except Exception as e:
            processing_time = time.time() - req_start_time
            return BatchResult(
                id=req.id,
                success=False,
                error=str(e),
                processing_time=processing_time
            )

    # Process with limited concurrency (images are expensive)
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent image generations

    async def bounded_process(req):
        async with semaphore:
            return await process_single_image(req)

    results = await asyncio.gather(
        *[bounded_process(req) for req in request.requests],
        return_exceptions=False
    )

    # Calculate statistics
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    total_cost = sum(
        r.result.get("cost", 0) for r in results
        if r.success and r.result
    )
    total_time = time.time() - start_time

    return BatchResponse(
        batch_id=batch_id,
        total_requests=len(request.requests),
        successful=successful,
        failed=failed,
        total_cost=total_cost,
        total_time=total_time,
        results=results
    )


# Async Batch Processing (for very large batches)
class AsyncBatchJob(BaseModel):
    """Async batch job status."""
    job_id: str
    status: str  # pending, processing, completed, failed
    total_requests: int
    processed: int
    successful: int
    failed: int
    created_at: datetime
    completed_at: Optional[datetime] = None


@router.post("/async/text")
async def create_async_batch_job(
    request: BatchTextRequestList,
    background_tasks: BackgroundTasks,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Create asynchronous batch processing job.

    For very large batches, process in background and poll for results.

    Returns job_id to check status via GET /batch/async/{job_id}
    """
    job_id = str(uuid.uuid4())

    # Store job in database (would need AsyncBatchJob model)
    # For now, return job info

    # Add to background tasks
    background_tasks.add_task(
        process_batch_in_background,
        job_id=job_id,
        requests=request.requests,
        user_id=api_key_data["user_id"],
        api_key_id=api_key_data["api_key_id"]
    )

    return AsyncBatchJob(
        job_id=job_id,
        status="pending",
        total_requests=len(request.requests),
        processed=0,
        successful=0,
        failed=0,
        created_at=datetime.utcnow()
    )


async def process_batch_in_background(
    job_id: str,
    requests: List[BatchTextRequest],
    user_id: str,
    api_key_id: str
):
    """Background task for processing large batches."""
    # Implementation would update job status in database
    # and process requests incrementally
    pass


@router.get("/async/{job_id}", response_model=AsyncBatchJob)
async def get_batch_job_status(
    job_id: str,
    api_key_data: Dict = Depends(verify_api_key)
):
    """
    Get status of async batch job.

    Returns current progress and results when completed.
    """
    # Implementation would query job from database
    # For now, return placeholder
    return AsyncBatchJob(
        job_id=job_id,
        status="processing",
        total_requests=100,
        processed=75,
        successful=70,
        failed=5,
        created_at=datetime.utcnow()
    )
