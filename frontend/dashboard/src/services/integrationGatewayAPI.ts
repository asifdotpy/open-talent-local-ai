import axios from 'axios';

/**
 * Integration Gateway API Client
 * Unified API client for OpenTalent Desktop Integration Service (port 8009)
 * 
 * Provides access to:
 * - Interview orchestration (start, respond, summary)
 * - Model management (list, select)
 * - Voice synthesis (TTS)
 * - Analytics (sentiment analysis)
 * - Agents (interviewer agent proxy)
 * - System health monitoring
 */

const GATEWAY_BASE_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8009';

// Create axios instance for gateway
const gatewayClient = axios.create({
  baseURL: GATEWAY_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Response types
export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface InterviewConfig {
  role: string;
  model: string;
  totalQuestions: number;
}

export interface InterviewSession {
  config: InterviewConfig;
  messages: Message[];
  currentQuestion: number;
  isComplete: boolean;
}

export interface ModelInfo {
  id: string;
  name: string;
  paramCount: string;
  ramRequired: string;
  downloadSize: string;
  description: string;
  dataset: string | null;
  source: string | null;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  services: Record<string, any>;
  summary: {
    online: number;
    total: number;
    percentage: number;
  };
}

// Integration Gateway API
export const integrationGatewayAPI = {
  // Health & System Status
  health: {
    check: async (): Promise<HealthResponse> => {
      const response = await gatewayClient.get('/health');
      return response.data;
    },

    getSystemStatus: async () => {
      const response = await gatewayClient.get('/api/v1/system/status');
      return response.data;
    },

    getDashboard: async () => {
      const response = await gatewayClient.get('/api/v1/dashboard');
      return response.data;
    },
  },

  // Model Management
  models: {
    list: async (): Promise<{ models: ModelInfo[] }> => {
      const response = await gatewayClient.get('/api/v1/models');
      return response.data;
    },

    select: async (modelId: string) => {
      const response = await gatewayClient.post('/api/v1/models/select', null, {
        params: { model_id: modelId },
      });
      return response.data;
    },
  },

  // Interview Orchestration
  interview: {
    start: async (config: InterviewConfig): Promise<InterviewSession> => {
      const response = await gatewayClient.post('/api/v1/interviews/start', config);
      return response.data;
    },

    respond: async (message: string, session: InterviewSession): Promise<InterviewSession> => {
      const response = await gatewayClient.post('/api/v1/interviews/respond', {
        message,
        session,
      });
      return response.data;
    },

    summary: async (session: InterviewSession) => {
      const response = await gatewayClient.post('/api/v1/interviews/summary', session);
      return response.data;
    },
  },

  // Voice Service (TTS)
  voice: {
    synthesize: async (text: string, voice: string = 'en-US-Neural2-C') => {
      const response = await gatewayClient.post('/api/v1/voice/synthesize', {
        text,
        voice,
      });
      return response.data;
    },
  },

  // Analytics Service
  analytics: {
    sentiment: async (text: string, context?: any) => {
      const response = await gatewayClient.post('/api/v1/analytics/sentiment', {
        text,
        context,
      });
      return response.data;
    },
  },

  // Agents Service (Interviewer Agent)
  agents: {
    execute: async (action: string, payload: any) => {
      const response = await gatewayClient.post('/api/v1/agents/execute', {
        action,
        ...payload,
      });
      return response.data;
    },

    // Convenience methods for interviewer agent
    startInterview: async (candidateId: string) => {
      return integrationGatewayAPI.agents.execute('start', { candidate_id: candidateId });
    },

    getInterviewStatus: async (interviewId: string) => {
      return integrationGatewayAPI.agents.execute('status', { interview_id: interviewId });
    },

    submitAnswer: async (interviewId: string, answer: string) => {
      return integrationGatewayAPI.agents.execute('answer', { interview_id: interviewId, answer });
    },

    getNextQuestion: async (interviewId: string) => {
      return integrationGatewayAPI.agents.execute('next_question', { interview_id: interviewId });
    },
  },
};

// Export default instance
export default integrationGatewayAPI;
