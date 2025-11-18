"""Streaming response utilities."""
import json
from typing import AsyncGenerator, Dict, Any
from fastapi.responses import StreamingResponse


async def stream_response(
    generator: AsyncGenerator[str, None],
    event_type: str = "message"
) -> StreamingResponse:
    """Create a streaming response using Server-Sent Events (SSE).

    Args:
        generator: Async generator yielding chunks
        event_type: SSE event type

    Returns:
        StreamingResponse with SSE format
    """
    async def event_stream():
        try:
            async for chunk in generator:
                # SSE format: data: {json}\n\n
                event_data = json.dumps({"data": chunk, "type": event_type})
                yield f"data: {event_data}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            # Send error event
            error_data = json.dumps({"error": str(e), "type": "error"})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


async def stream_text_generation(
    prompt: str,
    model: str,
    max_tokens: int,
    temperature: float,
    anthropic_client: Any = None,
    openai_client: Any = None
) -> AsyncGenerator[str, None]:
    """Stream text generation from AI models.

    Args:
        prompt: Input prompt
        model: Model name
        max_tokens: Maximum tokens
        temperature: Temperature
        anthropic_client: Anthropic client
        openai_client: OpenAI client

    Yields:
        Text chunks
    """
    if "claude" in model.lower() and anthropic_client:
        # Claude streaming
        async with anthropic_client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            async for text in stream.text_stream:
                yield text

    elif "gpt" in model.lower() and openai_client:
        # OpenAI streaming
        stream = await openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    else:
        raise ValueError(f"Unsupported model for streaming: {model}")
