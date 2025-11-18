# API Playground

Interactive API documentation and testing environment for Money API Service.

## Features

- **Interactive Documentation**: Explore all API endpoints with live examples
- **Real-time Testing**: Test API calls directly from your browser
- **Code Generation**: Auto-generate code snippets in multiple languages
- **WebSocket Testing**: Test WebSocket connections with live data
- **GraphQL Playground**: Interactive GraphQL query builder

## Access

### Swagger UI
```
https://api.moneyapi.example.com/docs
```

### ReDoc
```
https://api.moneyapi.example.com/redoc
```

### GraphQL Playground
```
https://api.moneyapi.example.com/graphql
```

## Quick Start

### 1. Get Your API Key

```bash
curl -X POST https://api.moneyapi.example.com/api/v1/management/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "name": "Your Name",
    "plan": "starter"
  }'
```

### 2. Test Text Generation

```bash
curl -X POST https://api.moneyapi.example.com/api/v1/text/completions \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a haiku about programming",
    "model": "claude-3-sonnet",
    "max_tokens": 100
  }'
```

### 3. Test Streaming

```bash
curl -X POST https://api.moneyapi.example.com/api/v1/streaming/text/completions \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tell me a story",
    "model": "claude-3-sonnet",
    "max_tokens": 500
  }' \
  --no-buffer
```

### 4. Test WebSocket

```javascript
const ws = new WebSocket('wss://api.moneyapi.example.com/ws?api_key=YOUR_API_KEY');

ws.onopen = () => {
  console.log('Connected!');

  // Subscribe to events
  ws.send(JSON.stringify({
    type: 'subscribe',
    events: ['usage_update', 'credit_alert']
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### 5. Test GraphQL

```graphql
query {
  me {
    id
    email
    name
    plan
    balance
  }

  usageStats(period: "7d") {
    totalRequests
    totalCost
    avgLatency
  }
}
```

## Code Examples

### Python

```python
from money_api import MoneyAPI

# Initialize client
client = MoneyAPI(api_key="YOUR_API_KEY")

# Text generation
response = client.text.completions(
    prompt="Explain quantum computing",
    model="claude-3-sonnet",
    max_tokens=500
)
print(response.text)

# Streaming
for chunk in client.streaming.text_completions(
    prompt="Write a blog post",
    model="claude-3-sonnet",
    max_tokens=1000
):
    print(chunk, end='', flush=True)
```

### JavaScript/TypeScript

```typescript
import { MoneyAPI } from '@money-api/sdk';

// Initialize client
const client = new MoneyAPI({
  apiKey: 'YOUR_API_KEY'
});

// Text generation
const response = await client.text.completions({
  prompt: 'Explain quantum computing',
  model: 'claude-3-sonnet',
  maxTokens: 500
});
console.log(response.text);

// Streaming
const stream = await client.streaming.textCompletions({
  prompt: 'Write a blog post',
  model: 'claude-3-sonnet',
  maxTokens: 1000
});

for await (const chunk of stream) {
  process.stdout.write(chunk);
}
```

### cURL

```bash
# Text generation
curl -X POST https://api.moneyapi.example.com/api/v1/text/completions \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "model": "claude-3-sonnet",
    "max_tokens": 500
  }'

# Image generation
curl -X POST https://api.moneyapi.example.com/api/v1/image/generate \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic cityscape at sunset",
    "model": "sdxl",
    "width": 1024,
    "height": 1024
  }'
```

## Rate Limiting

All API endpoints are rate-limited based on your plan:

| Plan | Requests/minute |
|------|----------------|
| Free | 10 |
| Starter | 60 |
| Pro | 300 |
| Enterprise | 1000 |

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

## Error Handling

```python
from money_api import MoneyAPI, APIError, RateLimitError

client = MoneyAPI(api_key="YOUR_API_KEY")

try:
    response = client.text.completions(
        prompt="Hello",
        model="claude-3-sonnet"
    )
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after}s")
except APIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

## Advanced Features

### Batch Requests

```python
# Process multiple prompts efficiently
prompts = [
    "Summarize quantum mechanics",
    "Explain neural networks",
    "Describe blockchain technology"
]

responses = await client.batch.text_completions(
    prompts=prompts,
    model="claude-3-sonnet",
    max_tokens=200
)
```

### Webhooks

```python
# Configure webhook for real-time notifications
client.webhooks.create(
    url="https://your-app.com/webhooks/money-api",
    events=["usage.threshold", "credit.low", "api_key.revoked"]
)
```

### Analytics

```python
# Get detailed usage analytics
analytics = client.analytics.usage(period="30d")

print(f"Total requests: {analytics.total_requests}")
print(f"Total cost: ${analytics.total_cost}")
print(f"Avg latency: {analytics.avg_latency}ms")

# Endpoint breakdown
for endpoint in analytics.endpoint_breakdown:
    print(f"{endpoint.name}: {endpoint.requests} requests")
```

## Support

- **Documentation**: https://docs.moneyapi.example.com
- **Email**: support@moneyapi.example.com
- **Discord**: https://discord.gg/moneyapi
- **GitHub**: https://github.com/moneyapi/money-api-service
