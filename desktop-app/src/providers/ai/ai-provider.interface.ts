export interface AIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface AIResponse {
  message: AIMessage;
  model: string;
  metadata?: {
    tokens?: number;
    latency?: number; // nanoseconds or ms depending on provider
  };
}

export interface AIProvider {
  chat(messages: AIMessage[], model: string): Promise<AIResponse>;
  listModels(): Promise<string[]>;
  checkHealth(): Promise<boolean>;
  getName(): string;
}
