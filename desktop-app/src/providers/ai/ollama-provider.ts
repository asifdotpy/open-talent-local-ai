import axios, { AxiosInstance } from 'axios';
import { AIProvider, AIMessage, AIResponse } from './ai-provider.interface';

export interface OllamaConfig {
  baseURL: string;
  timeout: number;
}

export class OllamaProvider implements AIProvider {
  private client: AxiosInstance;

  constructor(private config: OllamaConfig) {
    this.client = axios.create({ baseURL: config.baseURL, timeout: config.timeout });
  }

  async chat(messages: AIMessage[], model: string): Promise<AIResponse> {
    const response = await this.client.post('/api/chat', {
      model,
      messages,
      stream: false,
    });

    return {
      message: response.data.message,
      model,
      metadata: {
        tokens: response.data?.eval_count,
        latency: response.data?.total_duration,
      },
    };
  }

  async listModels(): Promise<string[]> {
    const response = await this.client.get('/api/tags');
    return response.data?.models?.map((m: any) => m.name) ?? [];
  }

  async checkHealth(): Promise<boolean> {
    try {
      await this.client.get('/api/tags');
      return true;
    } catch {
      return false;
    }
  }

  getName(): string {
    return 'Ollama';
  }
}
