import { AIProvider, AIMessage, AIResponse } from './ai-provider.interface';

export class MockAIProvider implements AIProvider {
  async chat(messages: AIMessage[], model: string): Promise<AIResponse> {
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    return {
      message: {
        role: 'assistant',
        content: `Mock reply to: ${lastUser?.content ?? 'Hello'} (model=${model})`,
      },
      model: model || 'mock-model',
      metadata: { tokens: 10, latency: 1 },
    };
  }

  async listModels(): Promise<string[]> {
    return ['mock-small', 'mock-medium'];
  }

  async checkHealth(): Promise<boolean> {
    return true;
  }

  getName(): string {
    return 'Mock';
  }
}
