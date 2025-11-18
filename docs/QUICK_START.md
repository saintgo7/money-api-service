# Quick Start Guide

Get started with Money API Service in 5 minutes.

## 1. Sign Up

Create your account:

```bash
curl -X POST https://api.moneyapi.example.com/api/v1/manage/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "your_secure_password",
    "full_name": "Your Name"
  }'
```

You'll receive **$5 in free credits** to get started!

## 2. Create API Key

Log into the [dashboard](https://dashboard.moneyapi.example.com) and create your first API key.

Or use the API:

```bash
curl -X POST https://api.moneyapi.example.com/api/v1/manage/api-keys \
  -H "Authorization: Bearer YOUR_TEMP_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My First Key"}'
```

Save the returned API key - you won't see it again!

## 3. Make Your First Request

### Text Generation

```bash
curl -X POST https://api.moneyapi.example.com/api/v1/text/completions \
  -H "Authorization: Bearer sk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a haiku about programming",
    "model": "claude-sonnet",
    "max_tokens": 100
  }'
```

Response:
```json
{
  "id": "comp_1234567890",
  "content": "Code flows like water\nBugs hide in silent shadows\nDebug with patience",
  "usage": {
    "total_tokens": 20
  },
  "model": "claude-3-5-sonnet",
  "cost": 0.00006
}
```

### Image Generation

```bash
curl -X POST https://api.moneyapi.example.com/api/v1/image/generate \
  -H "Authorization: Bearer sk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A serene mountain landscape at sunset",
    "model": "sdxl",
    "size": "1024x1024"
  }'
```

### Translation

```bash
curl -X POST https://api.moneyapi.example.com/api/v1/text/translate \
  -H "Authorization: Bearer sk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "source_lang": "en",
    "target_lang": "es"
  }'
```

## 4. Use SDK (Recommended)

### Python

```bash
pip install money-api-client
```

```python
from money_api import MoneyAPI

client = MoneyAPI(api_key="sk_your_api_key")

# Generate text
response = client.text.complete(
    prompt="Explain quantum computing",
    max_tokens=500
)
print(response["content"])

# Generate image
image = client.image.generate(
    prompt="A futuristic city"
)
print(image["images"][0])
```

### Node.js

```bash
npm install @money-api/client
```

```javascript
const { MoneyAPI } = require('@money-api/client');

const client = new MoneyAPI({ apiKey: 'sk_your_api_key' });

// Generate text
const response = await client.text.complete({
  prompt: 'Explain quantum computing',
  maxTokens: 500
});
console.log(response.content);

// Generate image
const image = await client.image.generate({
  prompt: 'A futuristic city'
});
console.log(image.images[0]);
```

## 5. Monitor Usage

Check your usage and costs:

```bash
curl -X GET "https://api.moneyapi.example.com/api/v1/manage/usage?period=30d" \
  -H "Authorization: Bearer sk_your_api_key"
```

Response:
```json
{
  "total_requests": 150,
  "total_cost": 2.45,
  "total_tokens": 15000,
  "by_endpoint": {
    "/v1/text/completions": {
      "requests": 100,
      "cost": 2.00,
      "tokens": 12000
    },
    "/v1/image/generate": {
      "requests": 50,
      "cost": 0.45,
      "tokens": 0
    }
  },
  "period": "30d"
}
```

## 6. Upgrade Your Plan

### Free Plan
- $5 free credits
- 10 requests/minute
- Perfect for testing

### Starter - $29/month
- $50 credits included
- 60 requests/minute
- Email support

### Pro - $99/month
- $200 credits included
- 300 requests/minute
- Priority support
- Advanced analytics

### Enterprise - Custom
- Volume discounts
- Dedicated infrastructure
- SLA guarantees

Upgrade in the [dashboard](https://dashboard.moneyapi.example.com/plans).

## Common Use Cases

### Chatbot
```python
# Simple chatbot
while True:
    user_input = input("You: ")
    response = client.text.complete(
        prompt=user_input,
        system="You are a helpful assistant"
    )
    print(f"Bot: {response['content']}")
```

### Content Generation
```python
# Generate marketing copy
headlines = client.text.complete(
    prompt="Generate 5 catchy headlines for a new AI product",
    max_tokens=200
)
```

### Batch Translation
```python
# Translate multiple texts
texts = ["Hello", "Thank you", "Goodbye"]
for text in texts:
    result = client.text.translate(
        text=text,
        source_lang="en",
        target_lang="es"
    )
    print(f"{text} -> {result['translated_text']}")
```

## Next Steps

1. **Read the [API Reference](API_REFERENCE.md)** - Complete API documentation
2. **Try [Examples](../examples/)** - Ready-to-run example apps
3. **Join our [Discord](https://discord.gg/moneyapi)** - Community support
4. **Set up [Webhooks](API_REFERENCE.md#webhooks)** - Get notified of events
5. **Explore [Use Cases](USE_CASES.md)** - Real-world applications

## Getting Help

- **Documentation**: https://docs.moneyapi.example.com
- **Email**: support@moneyapi.example.com
- **Discord**: https://discord.gg/moneyapi
- **Status**: https://status.moneyapi.example.com

## Rate Limits

| Plan | Requests/Minute | Burst |
|------|----------------|-------|
| Free | 10 | 20 |
| Starter | 60 | 100 |
| Pro | 300 | 500 |
| Enterprise | 1000+ | Custom |

Rate limit info is returned in response headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640000000
```

## Pricing Summary

**Text AI**
- Claude Sonnet: $0.003 / 1K tokens
- GPT-4: $0.006 / 1K tokens

**Image AI**
- SDXL: $0.02 / image
- DALL-E 3: $0.04 / image

**Audio AI**
- Transcription: $0.006 / minute
- TTS: $0.015 / 1K characters

See [full pricing](https://moneyapi.example.com/pricing).

## Tips for Success

1. **Cache results** - Don't make redundant API calls
2. **Use appropriate models** - Claude Sonnet for most tasks, GPT-4 for complex reasoning
3. **Set max_tokens** - Control costs by limiting output length
4. **Monitor usage** - Check dashboard regularly
5. **Use webhooks** - Get alerts when credits are low

Happy building! 🚀
