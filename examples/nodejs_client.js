/**
 * Example Node.js client for Money API Service
 *
 * Install dependencies:
 *   npm install axios
 */

const axios = require('axios');

class MoneyAPIClient {
  constructor(apiKey, baseURL = 'http://localhost:8000') {
    this.apiKey = apiKey;
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async textCompletion({ prompt, model = 'claude-sonnet', maxTokens = 1000, temperature = 0.7, system = null }) {
    const response = await this.client.post('/api/v1/text/completions', {
      prompt,
      model,
      max_tokens: maxTokens,
      temperature,
      system
    });
    return response.data;
  }

  async summarize(text, length = 'medium') {
    const response = await this.client.post('/api/v1/text/summarize', {
      text,
      length
    });
    return response.data;
  }

  async translate(text, sourceLang, targetLang) {
    const response = await this.client.post('/api/v1/text/translate', {
      text,
      source_lang: sourceLang,
      target_lang: targetLang
    });
    return response.data;
  }

  async generateImage({ prompt, model = 'sdxl', size = '1024x1024', n = 1 }) {
    const response = await this.client.post('/api/v1/image/generate', {
      prompt,
      model,
      size,
      n
    });
    return response.data;
  }

  async getUsageStats(period = '30d') {
    const response = await this.client.get('/api/v1/manage/usage', {
      params: { period }
    });
    return response.data;
  }
}

// Example usage
async function main() {
  const client = new MoneyAPIClient('sk_your_api_key_here');

  try {
    // Text completion
    console.log('=== Text Completion ===');
    const completion = await client.textCompletion({
      prompt: 'Write a haiku about artificial intelligence',
      maxTokens: 100
    });
    console.log(`Generated: ${completion.content}`);
    console.log(`Cost: $${completion.cost.toFixed(4)}`);

    // Summarization
    console.log('\n=== Summarization ===');
    const longText = `
      Artificial intelligence (AI) is transforming industries across the globe.
      From healthcare to finance, AI systems are helping humans make better decisions,
      automate repetitive tasks, and unlock new insights from data.
    `;
    const summary = await client.summarize(longText, 'short');
    console.log(`Summary: ${summary.summary}`);

    // Translation
    console.log('\n=== Translation ===');
    const translation = await client.translate(
      'Hello, how are you?',
      'en',
      'es'
    );
    console.log(`Translated: ${translation.translated_text}`);

    // Usage stats
    console.log('\n=== Usage Statistics ===');
    const stats = await client.getUsageStats('30d');
    console.log(`Total requests: ${stats.total_requests}`);
    console.log(`Total cost: $${stats.total_cost.toFixed(2)}`);
    console.log(`Total tokens: ${stats.total_tokens}`);

  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

if (require.main === module) {
  main();
}

module.exports = MoneyAPIClient;
