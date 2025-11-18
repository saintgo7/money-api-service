"""Text AI API endpoints."""
from typing import Optional, Dict, List
from decimal import Decimal
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import anthropic
import openai

from src.config import get_settings
from src.core.database import get_db
from src.core.usage_tracker import UsageTracker
from src.api.dependencies import verify_and_check_rate_limit

settings = get_settings()
router = APIRouter(prefix="/v1/text", tags=["Text AI"])


# Request/Response Models
class CompletionRequest(BaseModel):
    """Text completion request."""
    prompt: str = Field(..., description="Input prompt for text generation")
    model: str = Field(default="claude-sonnet", description="Model to use (claude-sonnet, gpt-4)")
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    system: Optional[str] = Field(None, description="System prompt")
    stream: bool = Field(default=False, description="Stream response")


class CompletionResponse(BaseModel):
    """Text completion response."""
    id: str
    content: str
    usage: Dict
    model: str
    cost: float


class SummarizeRequest(BaseModel):
    """Text summarization request."""
    text: str = Field(..., min_length=1)
    length: str = Field(default="medium", pattern="^(short|medium|long)$")


class TranslateRequest(BaseModel):
    """Translation request."""
    text: str = Field(..., min_length=1)
    source_lang: str = Field(..., min_length=2, max_length=5)
    target_lang: str = Field(..., min_length=2, max_length=5)


class SentimentResponse(BaseModel):
    """Sentiment analysis response."""
    sentiment: str
    score: float
    confidence: float


class Entity(BaseModel):
    """Named entity."""
    text: str
    type: str
    confidence: float


class EntitiesResponse(BaseModel):
    """Entity extraction response."""
    entities: List[Entity]


# Helper Functions
async def call_claude(
    prompt: str,
    max_tokens: int,
    temperature: float,
    system: Optional[str] = None
) -> tuple[str, int]:
    """Call Claude API."""
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=500, detail="Claude API key not configured")

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    messages = [{"role": "user", "content": prompt}]
    kwargs = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages
    }

    if system:
        kwargs["system"] = system

    response = await client.messages.create(**kwargs)

    content = response.content[0].text
    total_tokens = response.usage.input_tokens + response.usage.output_tokens

    return content, total_tokens


async def call_gpt4(
    prompt: str,
    max_tokens: int,
    temperature: float,
    system: Optional[str] = None
) -> tuple[str, int]:
    """Call GPT-4 API."""
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )

    content = response.choices[0].message.content
    total_tokens = response.usage.total_tokens

    return content, total_tokens


# Endpoints
@router.post("/completions", response_model=CompletionResponse)
async def create_completion(
    request: CompletionRequest,
    api_key_data: Dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate text completions using various LLMs.

    Supports Claude and GPT-4 models for high-quality text generation.
    Usage is tracked and billed based on token consumption.
    """
    start_time = time.time()

    # Route to appropriate model
    try:
        if "claude" in request.model.lower():
            content, tokens = await call_claude(
                request.prompt,
                request.max_tokens,
                request.temperature,
                request.system
            )
            cost_per_1k = settings.price_text_claude
            model_name = "claude-3-5-sonnet"
        elif "gpt" in request.model.lower():
            content, tokens = await call_gpt4(
                request.prompt,
                request.max_tokens,
                request.temperature,
                request.system
            )
            cost_per_1k = settings.price_text_gpt4
            model_name = "gpt-4-turbo"
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")

    # Calculate cost
    cost = Decimal(str((tokens / 1000) * cost_per_1k))

    # Check credit balance
    tracker = UsageTracker(db)
    if not await tracker.check_credit_balance(api_key_data["user_id"], cost):
        raise HTTPException(status_code=402, detail="Insufficient credits")

    # Record usage
    duration_ms = int((time.time() - start_time) * 1000)
    await tracker.record_usage(
        user_id=api_key_data["user_id"],
        api_key_id=api_key_data["api_key_id"],
        endpoint="/v1/text/completions",
        method="POST",
        tokens=tokens,
        duration_ms=duration_ms,
        status_code=200,
        cost=cost,
        metadata={"model": model_name}
    )

    return CompletionResponse(
        id=f"comp_{int(time.time())}",
        content=content,
        usage={"total_tokens": tokens},
        model=model_name,
        cost=float(cost)
    )


@router.post("/summarize")
async def summarize_text(
    request: SummarizeRequest,
    api_key_data: Dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Summarize text to specified length.

    Uses Claude for intelligent text summarization.
    """
    length_map = {
        "short": "in 1-2 sentences",
        "medium": "in 1 paragraph",
        "long": "in 2-3 paragraphs"
    }

    prompt = f"Summarize the following text {length_map[request.length]}:\n\n{request.text}"

    start_time = time.time()
    content, tokens = await call_claude(prompt, 500, 0.5)
    cost = Decimal(str((tokens / 1000) * settings.price_text_claude))

    tracker = UsageTracker(db)
    if not await tracker.check_credit_balance(api_key_data["user_id"], cost):
        raise HTTPException(status_code=402, detail="Insufficient credits")

    duration_ms = int((time.time() - start_time) * 1000)
    await tracker.record_usage(
        user_id=api_key_data["user_id"],
        api_key_id=api_key_data["api_key_id"],
        endpoint="/v1/text/summarize",
        method="POST",
        tokens=tokens,
        duration_ms=duration_ms,
        status_code=200,
        cost=cost
    )

    return {
        "summary": content,
        "usage": {"tokens": tokens},
        "cost": float(cost)
    }


@router.post("/translate")
async def translate_text(
    request: TranslateRequest,
    api_key_data: Dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Translate text between languages.

    Supports 100+ languages using advanced AI translation.
    """
    prompt = f"Translate the following text from {request.source_lang} to {request.target_lang}. Only output the translation, no explanations:\n\n{request.text}"

    start_time = time.time()
    content, tokens = await call_claude(prompt, 2000, 0.3)
    cost = Decimal(str((tokens / 1000) * settings.price_text_claude))

    tracker = UsageTracker(db)
    if not await tracker.check_credit_balance(api_key_data["user_id"], cost):
        raise HTTPException(status_code=402, detail="Insufficient credits")

    duration_ms = int((time.time() - start_time) * 1000)
    await tracker.record_usage(
        user_id=api_key_data["user_id"],
        api_key_id=api_key_data["api_key_id"],
        endpoint="/v1/text/translate",
        method="POST",
        tokens=tokens,
        duration_ms=duration_ms,
        status_code=200,
        cost=cost
    )

    return {
        "translated_text": content.strip(),
        "source_lang": request.source_lang,
        "target_lang": request.target_lang,
        "usage": {"tokens": tokens},
        "cost": float(cost)
    }


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(
    text: str,
    api_key_data: Dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze sentiment of text.

    Returns sentiment (positive/negative/neutral) with confidence score.
    """
    prompt = f"""Analyze the sentiment of the following text. Respond with ONLY a JSON object in this exact format:
{{"sentiment": "positive|negative|neutral", "score": 0.0-1.0, "confidence": 0.0-1.0}}

Text: {text}"""

    start_time = time.time()
    content, tokens = await call_claude(prompt, 100, 0.1)
    cost = Decimal(str((tokens / 1000) * settings.price_text_claude))

    tracker = UsageTracker(db)
    if not await tracker.check_credit_balance(api_key_data["user_id"], cost):
        raise HTTPException(status_code=402, detail="Insufficient credits")

    duration_ms = int((time.time() - start_time) * 1000)
    await tracker.record_usage(
        user_id=api_key_data["user_id"],
        api_key_id=api_key_data["api_key_id"],
        endpoint="/v1/text/sentiment",
        method="POST",
        tokens=tokens,
        duration_ms=duration_ms,
        status_code=200,
        cost=cost
    )

    import json
    try:
        result = json.loads(content.strip())
        return SentimentResponse(**result)
    except:
        return SentimentResponse(sentiment="neutral", score=0.5, confidence=0.5)


@router.post("/entities", response_model=EntitiesResponse)
async def extract_entities(
    text: str,
    api_key_data: Dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Extract named entities from text.

    Identifies people, organizations, locations, dates, etc.
    """
    prompt = f"""Extract named entities from the text. Return ONLY a JSON array of entities in this format:
[{{"text": "entity name", "type": "PERSON|ORG|LOCATION|DATE|OTHER", "confidence": 0.0-1.0}}]

Text: {text}"""

    start_time = time.time()
    content, tokens = await call_claude(prompt, 500, 0.1)
    cost = Decimal(str((tokens / 1000) * settings.price_text_claude))

    tracker = UsageTracker(db)
    if not await tracker.check_credit_balance(api_key_data["user_id"], cost):
        raise HTTPException(status_code=402, detail="Insufficient credits")

    duration_ms = int((time.time() - start_time) * 1000)
    await tracker.record_usage(
        user_id=api_key_data["user_id"],
        api_key_id=api_key_data["api_key_id"],
        endpoint="/v1/text/entities",
        method="POST",
        tokens=tokens,
        duration_ms=duration_ms,
        status_code=200,
        cost=cost
    )

    import json
    try:
        entities = json.loads(content.strip())
        return EntitiesResponse(entities=[Entity(**e) for e in entities])
    except:
        return EntitiesResponse(entities=[])
