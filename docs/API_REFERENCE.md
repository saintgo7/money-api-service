# API Reference

## Authentication

All API requests require authentication using a Bearer token in the Authorization header:

```bash
Authorization: Bearer sk_your_api_key_here
```

## Rate Limiting

API requests are rate-limited based on your subscription plan:

- **Free**: 10 requests/minute
- **Starter**: 60 requests/minute
- **Pro**: 300 requests/minute
- **Enterprise**: 1000 requests/minute

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640000000
```

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message here",
  "status_code": 400
}
```

Common status codes:

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid API key)
- `402` - Payment Required (insufficient credits)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## Text AI Endpoints

### POST /v1/text/completions

Generate text using AI models.

**Request:**
```json
{
  "prompt": "Your prompt here",
  "model": "claude-sonnet",
  "max_tokens": 1000,
  "temperature": 0.7,
  "system": "Optional system prompt"
}
```

**Response:**
```json
{
  "id": "comp_1234567890",
  "content": "Generated text...",
  "usage": {
    "total_tokens": 150
  },
  "model": "claude-3-5-sonnet",
  "cost": 0.00045
}
```

### POST /v1/text/summarize

Summarize text.

**Request:**
```json
{
  "text": "Long text to summarize...",
  "length": "short|medium|long"
}
```

### POST /v1/text/translate

Translate text between languages.

**Request:**
```json
{
  "text": "Hello world",
  "source_lang": "en",
  "target_lang": "es"
}
```

## Image AI Endpoints

### POST /v1/image/generate

Generate images from text.

**Request:**
```json
{
  "prompt": "A beautiful sunset",
  "model": "sdxl",
  "size": "1024x1024",
  "n": 1
}
```

**Response:**
```json
{
  "images": ["base64_encoded_image_or_url"],
  "prompt": "A beautiful sunset",
  "model": "sdxl",
  "cost": 0.02
}
```

## Audio AI Endpoints

### POST /v1/audio/transcribe

Transcribe audio to text.

**Request:** (multipart/form-data)
- `audio`: Audio file (mp3, wav, m4a)
- `language`: Language code (optional)
- `timestamps`: Include timestamps (optional)

**Response:**
```json
{
  "text": "Transcribed text...",
  "language": "en",
  "duration": 60.5,
  "cost": 0.0036
}
```

### POST /v1/audio/synthesize

Convert text to speech.

**Request:**
```json
{
  "text": "Hello, world!",
  "voice": "alloy",
  "speed": 1.0,
  "format": "mp3"
}
```

## Document AI Endpoints

### POST /v1/document/parse

Parse PDF/DOCX documents.

**Request:** (multipart/form-data)
- `document`: Document file
- `extract_tables`: Boolean
- `extract_images`: Boolean

**Response:**
```json
{
  "text": "Extracted text...",
  "tables": [],
  "images": [],
  "metadata": {
    "filename": "doc.pdf",
    "format": "pdf"
  },
  "page_count": 10
}
```

## Management Endpoints

### POST /v1/manage/users

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe",
  "company": "Acme Inc"
}
```

### GET /v1/manage/users/me

Get current user information.

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "plan": "pro",
  "credit_balance": 150.50,
  "is_active": true
}
```

### POST /v1/manage/api-keys

Create a new API key.

**Request:**
```json
{
  "name": "Production API",
  "permissions": ["*"],
  "rate_limit": 60
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Production API",
  "key": "sk_...",
  "key_prefix": "sk_abcd",
  "rate_limit": 60,
  "is_active": true
}
```

### GET /v1/manage/usage

Get usage statistics.

**Query Parameters:**
- `period`: 24h, 7d, 30d, 90d

**Response:**
```json
{
  "total_requests": 1500,
  "total_cost": 12.50,
  "total_tokens": 50000,
  "by_endpoint": {
    "/v1/text/completions": {
      "requests": 1000,
      "cost": 10.00,
      "tokens": 40000
    }
  },
  "period": "30d"
}
```

## SDKs

### Python

```python
from money_api import MoneyAPI

client = MoneyAPI(api_key="sk_...")

# Text completion
response = client.text.completions.create(
    prompt="Write a poem",
    model="claude-sonnet",
    max_tokens=500
)
print(response.content)

# Image generation
image = client.image.generate(
    prompt="A cat on Mars",
    model="sdxl"
)
```

### Node.js

```javascript
const { MoneyAPI } = require('money-api');

const client = new MoneyAPI({ apiKey: 'sk_...' });

// Text completion
const response = await client.text.completions.create({
  prompt: 'Write a poem',
  model: 'claude-sonnet',
  maxTokens: 500
});

console.log(response.content);
```

## Webhooks

Configure webhooks to receive notifications for events:

- `usage.threshold_reached` - When usage reaches a threshold
- `credit.low` - When credits are running low
- `api_key.created` - When a new API key is created
- `api_key.revoked` - When an API key is revoked

**Webhook Payload:**
```json
{
  "event": "usage.threshold_reached",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "user_id": "uuid",
    "threshold": 0.8,
    "current_usage": 0.85
  }
}
```
