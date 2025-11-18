import axios, { AxiosInstance } from 'axios';

export interface TextCompletion {
    id: string;
    text: string;
    model: string;
    usage: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
    };
    cost: number;
    latency: number;
}

export interface ImageGeneration {
    id: string;
    url: string;
    model: string;
    cost: number;
    width: number;
    height: number;
}

export interface Balance {
    balance: number;
    currency: string;
}

export interface UsageSummary {
    total_requests: number;
    total_cost: number;
    period: string;
}

export interface CostPrediction {
    current_month: number;
    predicted_next_month: number;
    predicted_daily_average: number;
    trend: string;
    confidence: number;
    forecasts: any[];
}

export interface AnomalyDetection {
    is_anomaly: boolean;
    anomaly_score: number;
    threshold: number;
    date: string;
    actual_value: number;
    expected_value: number;
    deviation_percentage: number;
}

export interface UsageInsights {
    summary: {
        total_endpoints: number;
        analysis_period: string;
    };
    recommendations: Array<{
        type: string;
        priority: string;
        message: string;
    }>;
    cost_breakdown: Array<{
        endpoint: string;
        requests: number;
        cost: number;
        percentage: number;
        avg_latency: number;
    }>;
}

export class MoneyAPIClient {
    private client: AxiosInstance;

    constructor(apiKey: string, baseUrl: string = 'https://api.money-api.com') {
        this.client = axios.create({
            baseURL: baseUrl,
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            timeout: 60000
        });
    }

    async generateText(
        prompt: string,
        model: string = 'claude-3-sonnet',
        maxTokens: number = 1000
    ): Promise<TextCompletion> {
        const response = await this.client.post('/v1/text/completions', {
            prompt,
            model,
            max_tokens: maxTokens,
            stream: false
        });
        return response.data;
    }

    async generateImage(
        prompt: string,
        model: string = 'sdxl',
        width: number = 1024,
        height: number = 1024
    ): Promise<ImageGeneration> {
        const response = await this.client.post('/v1/image/generate', {
            prompt,
            model,
            width,
            height
        });
        return response.data;
    }

    async getBalance(): Promise<Balance> {
        const response = await this.client.get('/v1/account/balance');
        return response.data;
    }

    async getUsage(): Promise<UsageSummary> {
        const response = await this.client.get('/v1/account/usage');
        return response.data;
    }

    async predictCost(): Promise<CostPrediction> {
        const response = await this.client.get('/v1/ml/predict/cost');
        return response.data;
    }

    async detectAnomalies(days: number = 30): Promise<AnomalyDetection[]> {
        const response = await this.client.get('/v1/ml/anomalies/detect', {
            params: { days }
        });
        return response.data;
    }

    async getInsights(): Promise<UsageInsights> {
        const response = await this.client.get('/v1/ml/insights/usage');
        return response.data;
    }
}
