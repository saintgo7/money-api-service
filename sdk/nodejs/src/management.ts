import { AxiosInstance } from 'axios';

export interface UserResponse {
  id: string;
  email: string;
  full_name?: string;
  company?: string;
  plan: string;
  credit_balance: number;
  is_active: boolean;
  created_at: string;
}

export interface APIKeyResponse {
  id: string;
  name: string;
  key?: string;
  key_prefix: string;
  permissions: string[];
  rate_limit: number;
  is_active: boolean;
  created_at: string;
  last_used?: string;
}

export interface UsageStats {
  total_requests: number;
  total_cost: number;
  total_tokens: number;
  by_endpoint: Record<string, any>;
  period: string;
}

export class ManagementAPI {
  constructor(private client: AxiosInstance) {}

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<UserResponse> {
    const response = await this.client.get('/api/v1/manage/users/me');
    return response.data;
  }

  /**
   * Create new API key
   */
  async createAPIKey(name: string, permissions?: string[]): Promise<APIKeyResponse> {
    const response = await this.client.post('/api/v1/manage/api-keys', {
      name,
      permissions: permissions || ['*']
    });
    return response.data;
  }

  /**
   * List all API keys
   */
  async listAPIKeys(): Promise<APIKeyResponse[]> {
    const response = await this.client.get('/api/v1/manage/api-keys');
    return response.data;
  }

  /**
   * Revoke API key
   */
  async revokeAPIKey(keyId: string): Promise<void> {
    await this.client.delete(`/api/v1/manage/api-keys/${keyId}`);
  }

  /**
   * Get usage statistics
   */
  async getUsage(period: string = '30d'): Promise<UsageStats> {
    const response = await this.client.get('/api/v1/manage/usage', {
      params: { period }
    });
    return response.data;
  }

  /**
   * Add credits to account
   */
  async addCredits(amount: number): Promise<any> {
    const response = await this.client.post('/api/v1/manage/credits', {
      amount
    });
    return response.data;
  }

  /**
   * Update subscription plan
   */
  async updateSubscription(plan: string): Promise<any> {
    const response = await this.client.post(`/api/v1/manage/subscription/${plan}`);
    return response.data;
  }
}
