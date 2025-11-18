# Money API Node.js SDK

Official TypeScript/JavaScript client for Money API Service.

## Installation

```bash
npm install @money-api/client
# or
yarn add @money-api/client
```

## Quick Start

```typescript
import { MoneyAPI } from '@money-api/client';

const client = new MoneyAPI({
  apiKey: 'sk_your_api_key'
});

// Generate text
const response = await client.text.complete({
  prompt: 'Write a haiku about AI',
  max_tokens: 100
});

console.log(response.content);
console.log(`Cost: $${response.cost}`);
```

## Usage Examples

### Text Generation

```typescript
// Simple completion
const result = await client.text.complete({
  prompt: 'Explain quantum computing',
  model: 'claude-sonnet',
  max_tokens: 500,
  temperature: 0.7
});

// Summarization
const summary = await client.text.summarize({
  text: 'Long text here...',
  length: 'short'
});

// Translation
const translation = await client.text.translate({
  text: 'Hello, world!',
  source_lang: 'en',
  target_lang: 'es'
});

// Sentiment analysis
const sentiment = await client.text.analyzeSentiment(
  'I love this product!'
);
```

### Image Generation

```typescript
const image = await client.image.generate({
  prompt: 'A sunset over mountains',
  model: 'sdxl',
  size: '1024x1024',
  n: 1
});

console.log(image.images[0]); // Image URL or base64
```

### Audio Processing

```typescript
import fs from 'fs';

// Transcribe audio
const audioBuffer = fs.readFileSync('audio.mp3');
const transcription = await client.audio.transcribe(audioBuffer);

console.log(transcription.text);

// Text to speech
const speech = await client.audio.synthesize({
  text: 'Hello, world!',
  voice: 'alloy'
});
```

### Document Processing

```typescript
const docBuffer = fs.readFileSync('document.pdf');

// Parse document
const parsed = await client.document.parse(docBuffer, true, false);
console.log(parsed.text);

// Document Q&A
const qa = await client.document.qa(docBuffer, [
  'What is the main topic?',
  'Who are the key people mentioned?'
]);
```

### Account Management

```typescript
// Get user info
const user = await client.management.getCurrentUser();
console.log(`Balance: $${user.credit_balance}`);

// Get usage stats
const stats = await client.management.getUsage('30d');
console.log(`Total cost: $${stats.total_cost}`);

// Create API key
const apiKey = await client.management.createAPIKey('Production Key');
console.log(`New key: ${apiKey.key}`);
```

## Error Handling

```typescript
import {
  MoneyAPIError,
  RateLimitError,
  InsufficientCreditsError
} from '@money-api/client';

try {
  const result = await client.text.complete({ prompt: 'Hello' });
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(`Rate limited. Retry after: ${error.retryAfter}`);
  } else if (error instanceof InsufficientCreditsError) {
    console.log('Please add more credits');
  } else if (error instanceof MoneyAPIError) {
    console.log(`API error: ${error.message}`);
  }
}
```

## TypeScript Support

Full TypeScript support with type definitions included.

```typescript
import { MoneyAPI, CompletionRequest, CompletionResponse } from '@money-api/client';

const request: CompletionRequest = {
  prompt: 'Hello',
  max_tokens: 100
};

const response: CompletionResponse = await client.text.complete(request);
```

## Configuration

```typescript
const client = new MoneyAPI({
  apiKey: 'sk_...',
  baseURL: 'https://api.moneyapi.example.com',  // Optional
  timeout: 60000  // Optional, default 60s
});
```

## License

MIT
