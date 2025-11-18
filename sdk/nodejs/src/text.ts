import { AxiosInstance } from 'axios';

export interface CompletionRequest {
  prompt: string;
  model?: string;
  max_tokens?: number;
  temperature?: number;
  system?: string;
  stream?: boolean;
}

export interface CompletionResponse {
  id: string;
  content: string;
  usage: {
    total_tokens: number;
  };
  model: string;
  cost: number;
}

export interface SummarizeRequest {
  text: string;
  length?: 'short' | 'medium' | 'long';
}

export interface TranslateRequest {
  text: string;
  source_lang: string;
  target_lang: string;
}

export interface SentimentResponse {
  sentiment: string;
  score: number;
  confidence: number;
}

export interface Entity {
  text: string;
  type: string;
  confidence: number;
}

export class TextAPI {
  constructor(private client: AxiosInstance) {}

  /**
   * Generate text completion
   */
  async complete(request: CompletionRequest): Promise<CompletionResponse> {
    const response = await this.client.post('/api/v1/text/completions', {
      prompt: request.prompt,
      model: request.model || 'claude-sonnet',
      max_tokens: request.max_tokens || 1000,
      temperature: request.temperature || 0.7,
      system: request.system,
      stream: request.stream || false
    });
    return response.data;
  }

  /**
   * Summarize text
   */
  async summarize(request: SummarizeRequest): Promise<any> {
    const response = await this.client.post('/api/v1/text/summarize', {
      text: request.text,
      length: request.length || 'medium'
    });
    return response.data;
  }

  /**
   * Translate text
   */
  async translate(request: TranslateRequest): Promise<any> {
    const response = await this.client.post('/api/v1/text/translate', request);
    return response.data;
  }

  /**
   * Analyze sentiment
   */
  async analyzeSentiment(text: string): Promise<SentimentResponse> {
    const response = await this.client.post('/api/v1/text/sentiment', null, {
      params: { text }
    });
    return response.data;
  }

  /**
   * Extract named entities
   */
  async extractEntities(text: string): Promise<{ entities: Entity[] }> {
    const response = await this.client.post('/api/v1/text/entities', null, {
      params: { text }
    });
    return response.data;
  }
}
