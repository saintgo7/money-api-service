"""Streaming endpoint for text generation."""
from typing import Dict
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import anthropic
import openai

from src.config import get_settings
from src.api.dependencies import verify_and_check_rate_limit
from src.api.v1.text import CompletionRequest
from src.core.streaming import stream_response, stream_text_generation

settings = get_settings()
router = APIRouter(prefix="/v1/stream", tags=["Streaming"])


@router.post("/text/completions")
async def stream_text_completion(
    request: CompletionRequest,
    api_key_data: Dict = Depends(verify_and_check_rate_limit)
) -> StreamingResponse:
    """
    Stream text completion in real-time.

    Returns chunks of text as they're generated using Server-Sent Events (SSE).

    Usage:
    ```javascript
    const eventSource = new EventSource('/api/v1/stream/text/completions', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer sk_...' },
        body: JSON.stringify({ prompt: 'Hello' })
    });

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.done) {
            eventSource.close();
        } else {
            console.log(data.data); // Text chunk
        }
    };
    ```
    """
    # Initialize clients
    anthropic_client = None
    openai_client = None

    if "claude" in request.model.lower():
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    elif "gpt" in request.model.lower():
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    # Create streaming generator
    generator = stream_text_generation(
        prompt=request.prompt,
        model=request.model,
        max_tokens=request.max_tokens or 1000,
        temperature=request.temperature or 0.7,
        anthropic_client=anthropic_client,
        openai_client=openai_client
    )

    # Return streaming response
    return await stream_response(generator, event_type="text_chunk")


@router.post("/text/translate")
async def stream_translation(
    text: str,
    source_lang: str,
    target_lang: str,
    api_key_data: Dict = Depends(verify_and_check_rate_limit)
) -> StreamingResponse:
    """
    Stream translation in real-time.

    Useful for translating long texts where you want to see results as they come.
    """
    prompt = f"Translate from {source_lang} to {target_lang}:\n\n{text}"

    anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    generator = stream_text_generation(
        prompt=prompt,
        model="claude-sonnet",
        max_tokens=2000,
        temperature=0.3,
        anthropic_client=anthropic_client
    )

    return await stream_response(generator, event_type="translation_chunk")
