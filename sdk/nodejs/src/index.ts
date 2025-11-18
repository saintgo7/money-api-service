/**
 * Money API Node.js SDK
 * Official TypeScript/JavaScript client for Money API Service
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import FormData from 'form-data';
import { TextAPI } from './text';
import { ImageAPI } from './image';
import { AudioAPI } from './audio';
import { DocumentAPI } from './document';
import { ManagementAPI } from './management';

export interface MoneyAPIConfig {
  apiKey: string;
  baseURL?: string;
  timeout?: number;
}

export class MoneyAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'MoneyAPIError';
  }
}

export class RateLimitError extends MoneyAPIError {
  constructor(
    message: string,
    public retryAfter: number
  ) {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}

export class InsufficientCreditsError extends MoneyAPIError {
  constructor(message: string = 'Insufficient credits') {
    super(message, 402);
    this.name = 'InsufficientCreditsError';
  }
}

export class MoneyAPI {
  private client: AxiosInstance;

  public readonly text: TextAPI;
  public readonly image: ImageAPI;
  public readonly audio: AudioAPI;
  public readonly document: DocumentAPI;
  public readonly management: ManagementAPI;

  constructor(config: MoneyAPIConfig) {
    const { apiKey, baseURL = 'https://api.moneyapi.example.com', timeout = 60000 } = config;

    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': 'money-api-nodejs/1.0.0'
      }
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      (error: AxiosError) => {
        if (error.response) {
          const { status, data } = error.response;

          if (status === 429) {
            const retryAfter = parseInt(error.response.headers['x-ratelimit-reset'] || '0');
            throw new RateLimitError('Rate limit exceeded', retryAfter);
          }

          if (status === 402) {
            throw new InsufficientCreditsError();
          }

          const message = (data as any)?.detail || error.message;
          throw new MoneyAPIError(message, status, data);
        }

        throw new MoneyAPIError(error.message);
      }
    );

    // Initialize API modules
    this.text = new TextAPI(this.client);
    this.image = new ImageAPI(this.client);
    this.audio = new AudioAPI(this.client);
    this.document = new DocumentAPI(this.client);
    this.management = new ManagementAPI(this.client);
  }

  /**
   * Get axios instance for custom requests
   */
  getClient(): AxiosInstance {
    return this.client;
  }
}

// Export all types and classes
export * from './text';
export * from './image';
export * from './audio';
export * from './document';
export * from './management';

export default MoneyAPI;
