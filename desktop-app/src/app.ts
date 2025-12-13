import { container } from './core/di-container';
import { ConfigManager } from './core/config-manager';
import { EventBus } from './core/event-bus';
import { OllamaProvider } from './providers/ai/ollama-provider';
import { MockAIProvider } from './providers/ai/mock-provider';
import InterviewService from './services/interview-service';
import { IntegrationInterviewService } from './services/integration-interview-service';

// Initialize core singletons
const config = new ConfigManager();
const eventBus = new EventBus();

container.registerSingleton('ConfigManager', config);
container.registerSingleton('EventBus', eventBus);

// Choose AI provider based on config/env
const useMock = process.env.USE_MOCK_AI === '1' || config.get('ai').provider === 'mock';
const useIntegration = process.env.USE_INTEGRATION_SERVICE !== '0';  // Default to true

if (useMock) {
  container.register('AIProvider', () => new MockAIProvider());
} else {
  const aiCfg = config.get('ai').ollama;
  container.register('AIProvider', () => new OllamaProvider({ baseURL: aiCfg.baseURL, timeout: aiCfg.timeout }));
}

// Register InterviewService - use integration service by default
if (useIntegration) {
  container.register('InterviewService', () => {
    const provider = container.resolve<any>('AIProvider');
    return new IntegrationInterviewService(provider);
  });
  console.log('[App] Using Integration Interview Service (gateway mode)');
} else {
  container.register('InterviewService', () => {
    const provider = container.resolve<any>('AIProvider');
    return new InterviewService(provider);
  });
  console.log('[App] Using Direct Ollama Interview Service');
}

export { container };
