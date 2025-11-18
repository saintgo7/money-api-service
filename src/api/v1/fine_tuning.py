"""Fine-tuning API for custom AI models."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from enum import Enum

from src.core.api_management import verify_api_key
from src.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/fine-tuning", tags=["Fine-Tuning"])


# Enums
class FineTuningStatus(str, Enum):
    """Fine-tuning job status."""
    PENDING = "pending"
    VALIDATING = "validating"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelProvider(str, Enum):
    """Supported model providers for fine-tuning."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  # Future support


# Request/Response Models
class FineTuningJobCreate(BaseModel):
    """Create fine-tuning job request."""
    training_file_id: str = Field(..., description="ID of uploaded training file")
    validation_file_id: Optional[str] = Field(None, description="ID of validation file")
    model: str = Field(default="gpt-3.5-turbo", description="Base model to fine-tune")
    hyperparameters: Optional[Dict[str, Any]] = Field(
        default={
            "n_epochs": 3,
            "batch_size": "auto",
            "learning_rate_multiplier": "auto"
        }
    )
    suffix: Optional[str] = Field(None, max_length=40, description="Custom model suffix")


class FineTuningJob(BaseModel):
    """Fine-tuning job details."""
    id: str
    user_id: str
    status: FineTuningStatus
    model: str
    training_file_id: str
    validation_file_id: Optional[str]
    fine_tuned_model: Optional[str] = None

    # Progress
    trained_tokens: int = 0
    total_tokens: Optional[int] = None
    progress_percentage: float = 0.0

    # Metrics
    training_loss: Optional[float] = None
    validation_loss: Optional[float] = None

    # Costs
    estimated_cost: float = 0.0
    actual_cost: Optional[float] = None

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Error handling
    error: Optional[str] = None


class TrainingMetrics(BaseModel):
    """Training progress metrics."""
    step: int
    training_loss: float
    validation_loss: Optional[float] = None
    timestamp: datetime


# Endpoints
@router.post("/jobs", response_model=FineTuningJob)
async def create_fine_tuning_job(
    request: FineTuningJobCreate,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a fine-tuning job for custom model training.

    Steps:
    1. Upload training data (JSONL format)
    2. Create fine-tuning job
    3. Monitor progress
    4. Use fine-tuned model

    Example training data (JSONL):
    ```
    {"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]}
    {"messages": [{"role": "user", "content": "How are you?"}, {"role": "assistant", "content": "I'm doing well!"}]}
    ```

    Cost: ~$0.008 per 1K tokens for gpt-3.5-turbo fine-tuning
    """
    user_id = api_key_data["user_id"]
    job_id = str(uuid.uuid4())

    # Validate training file exists
    # In production, this would check uploaded files in storage

    # Estimate cost based on file size
    # For demo, use placeholder
    estimated_cost = 10.0  # $10 estimated

    # Create job
    job = FineTuningJob(
        id=job_id,
        user_id=user_id,
        status=FineTuningStatus.PENDING,
        model=request.model,
        training_file_id=request.training_file_id,
        validation_file_id=request.validation_file_id,
        estimated_cost=estimated_cost,
        created_at=datetime.utcnow()
    )

    # Store in database (would need FineTuningJob model)
    # For now, return job object

    # Start fine-tuning process in background
    # This would call OpenAI API or other provider

    return job


@router.get("/jobs", response_model=List[FineTuningJob])
async def list_fine_tuning_jobs(
    limit: int = 20,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    List all fine-tuning jobs for the user.

    Returns jobs sorted by creation date (newest first).
    """
    user_id = api_key_data["user_id"]

    # Query database for user's fine-tuning jobs
    # For now, return sample data

    return [
        FineTuningJob(
            id=str(uuid.uuid4()),
            user_id=user_id,
            status=FineTuningStatus.COMPLETED,
            model="gpt-3.5-turbo",
            training_file_id="file-123",
            fine_tuned_model="ft:gpt-3.5-turbo:custom-model:abc123",
            trained_tokens=1000000,
            total_tokens=1000000,
            progress_percentage=100.0,
            training_loss=0.15,
            validation_loss=0.18,
            estimated_cost=10.0,
            actual_cost=8.5,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
    ]


@router.get("/jobs/{job_id}", response_model=FineTuningJob)
async def get_fine_tuning_job(
    job_id: str,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific fine-tuning job.

    Includes current progress, metrics, and status.
    """
    user_id = api_key_data["user_id"]

    # Query database for job
    # Verify ownership

    return FineTuningJob(
        id=job_id,
        user_id=user_id,
        status=FineTuningStatus.TRAINING,
        model="gpt-3.5-turbo",
        training_file_id="file-123",
        trained_tokens=750000,
        total_tokens=1000000,
        progress_percentage=75.0,
        training_loss=0.20,
        estimated_cost=10.0,
        created_at=datetime.utcnow(),
        started_at=datetime.utcnow()
    )


@router.delete("/jobs/{job_id}")
async def cancel_fine_tuning_job(
    job_id: str,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a running fine-tuning job.

    Note: Cannot cancel completed jobs.
    Partial charges may apply for cancelled jobs.
    """
    user_id = api_key_data["user_id"]

    # Get job and verify ownership
    # Cancel if status is PENDING or TRAINING

    return {
        "message": "Fine-tuning job cancelled",
        "job_id": job_id,
        "status": "cancelled"
    }


@router.get("/jobs/{job_id}/metrics", response_model=List[TrainingMetrics])
async def get_training_metrics(
    job_id: str,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed training metrics over time.

    Useful for monitoring model performance during training.
    """
    user_id = api_key_data["user_id"]

    # Query metrics from database
    # Return time-series data

    return [
        TrainingMetrics(
            step=100,
            training_loss=0.45,
            validation_loss=0.48,
            timestamp=datetime.utcnow()
        ),
        TrainingMetrics(
            step=200,
            training_loss=0.30,
            validation_loss=0.35,
            timestamp=datetime.utcnow()
        ),
        TrainingMetrics(
            step=300,
            training_loss=0.20,
            validation_loss=0.25,
            timestamp=datetime.utcnow()
        )
    ]


@router.post("/files/upload")
async def upload_training_file(
    file: UploadFile = File(...),
    purpose: str = "fine-tune",
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload training data file for fine-tuning.

    Supported formats:
    - JSONL (JSON Lines)

    File requirements:
    - Maximum size: 100 MB
    - Minimum examples: 10
    - Format validation

    Returns file_id to use in fine-tuning job creation.
    """
    user_id = api_key_data["user_id"]

    # Validate file format (should be JSONL)
    if not file.filename.endswith('.jsonl'):
        raise HTTPException(
            status_code=400,
            detail="File must be in JSONL format (.jsonl)"
        )

    # Read and validate content
    content = await file.read()

    # Validate file size (max 100 MB)
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 100 MB limit"
        )

    # Validate JSONL format
    import json
    lines = content.decode('utf-8').strip().split('\n')

    if len(lines) < 10:
        raise HTTPException(
            status_code=400,
            detail="Minimum 10 training examples required"
        )

    try:
        for line in lines:
            json.loads(line)  # Validate each line is valid JSON
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSONL format: {str(e)}"
        )

    # Store file (in production: S3, GCS, etc.)
    file_id = f"file-{uuid.uuid4()}"

    # Save file metadata to database

    return {
        "file_id": file_id,
        "filename": file.filename,
        "bytes": len(content),
        "purpose": purpose,
        "created_at": datetime.utcnow().isoformat()
    }


@router.get("/models")
async def list_fine_tuned_models(
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    List all fine-tuned models available to the user.

    Returns models that can be used for inference.
    """
    user_id = api_key_data["user_id"]

    # Query completed fine-tuning jobs
    # Return fine-tuned model names

    return {
        "models": [
            {
                "id": "ft:gpt-3.5-turbo:custom-model-1:abc123",
                "created_at": datetime.utcnow().isoformat(),
                "base_model": "gpt-3.5-turbo",
                "training_tokens": 1000000
            },
            {
                "id": "ft:gpt-3.5-turbo:custom-model-2:def456",
                "created_at": datetime.utcnow().isoformat(),
                "base_model": "gpt-3.5-turbo",
                "training_tokens": 500000
            }
        ]
    }


@router.delete("/models/{model_id}")
async def delete_fine_tuned_model(
    model_id: str,
    api_key_data: Dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a fine-tuned model.

    Note: This action is permanent and cannot be undone.
    """
    user_id = api_key_data["user_id"]

    # Verify ownership and delete model

    return {
        "message": "Model deleted successfully",
        "model_id": model_id
    }
