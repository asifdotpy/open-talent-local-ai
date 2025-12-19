/**
 * Gateway Enhanced Client
 * Wraps generated DefaultService with typed helpers for interview, voice, and analytics flows.
 * Provides a clean API surface for the React components.
 */

import {
  DefaultService,
  OpenAPI,
  type StartInterviewRequest,
  type InterviewResponseRequest,
  type InterviewSession,
  type HealthResponse,
  type ModelsResponse,
} from '../api/gateway';

/**
 * Text-to-Speech Request/Response
 */
export interface SynthesizeSpeechRequest {
  text: string;
  voice?: string;  // e.g., 'en-US-Neural2-C'
  speed?: number;  // 0.5 to 2.0
  pitch?: number;  // -20 to 20
}

export interface SynthesizeSpeechResponse {
  audioUrl: string;
  audioBase64?: string;
  duration?: number;  // seconds
  format: 'mp3' | 'wav' | 'ogg';
}

/**
 * Sentiment Analysis Request/Response
 */
export interface AnalyzeSentimentRequest {
  text: string;
  context?: string;  // e.g., 'interview_response'
}

export interface AnalyzeSentimentResponse {
  score: number;  // -1.0 (negative) to 1.0 (positive)
  magnitude: number;  // 0.0 (weak) to 1.0 (strong)
  sentences?: Array<{ text: string; score: number; magnitude: number }>;
  entities?: Array<{ name: string; sentiment: number; salience: number }>;
}

/**
 * Configure base URL from environment
 */
export function configureGateway(baseUrl?: string): void {
  OpenAPI.BASE = baseUrl || process.env.INTEGRATION_BASE_URL || 'http://localhost:8009';
  console.log(`[GatewayClient] Configured to ${OpenAPI.BASE}`);
}

/**
 * Interview API
 */
export const InterviewAPI = {
  /**
   * Start a new interview
   */
  async start(request: StartInterviewRequest): Promise<InterviewSession | null> {
    try {
      const session = await DefaultService.startInterviewApiV1InterviewsStartPost(request);
      return session as unknown as InterviewSession;
    } catch (error) {
      console.error('[InterviewAPI] Failed to start interview:', error);
      return null;
    }
  },

  /**
   * Submit a response and get the next question
   */
  async respond(request: InterviewResponseRequest): Promise<InterviewSession | null> {
    try {
      const session = await DefaultService.respondToInterviewApiV1InterviewsRespondPost(request);
      return session as unknown as InterviewSession;
    } catch (error) {
      console.error('[InterviewAPI] Failed to respond to interview:', error);
      return null;
    }
  },

  /**
   * Get interview summary and assessment
   */
  async getSummary(session: InterviewSession): Promise<Record<string, any> | null> {
    try {
      const summary = await DefaultService.getInterviewSummaryApiV1InterviewsSummaryPost(
        session as any
      );
      return summary;
    } catch (error) {
      console.error('[InterviewAPI] Failed to get interview summary:', error);
      return null;
    }
  },
};

/**
 * Models API
 */
export const ModelsAPI = {
  /**
   * List all available models
   */
  async list(): Promise<any[]> {
    try {
      const response: ModelsResponse = await DefaultService.listModelsApiV1ModelsGet();
      return response.models || [];
    } catch (error) {
      console.error('[ModelsAPI] Failed to list models:', error);
      return [];
    }
  },

  /**
   * Select a specific model for subsequent interviews
   */
  async select(modelId: string): Promise<boolean> {
    try {
      await DefaultService.selectModelApiV1ModelsSelectPost(modelId);
      console.log(`[ModelsAPI] Selected model: ${modelId}`);
      return true;
    } catch (error) {
      console.error('[ModelsAPI] Failed to select model:', error);
      return false;
    }
  },
};

/**
 * Voice API (TTS)
 */
export const VoiceAPI = {
  /**
   * Synthesize speech from text
   * Proxies to voice-service when enabled.
   */
  async synthesize(
    request: SynthesizeSpeechRequest
  ): Promise<SynthesizeSpeechResponse | null> {
    try {
      const body = {
        text: request.text,
        voice: request.voice || 'en-US-Neural2-C',
        speed: request.speed || 1.0,
        pitch: request.pitch || 0,
      };
      const response = await DefaultService.synthesizeSpeechApiV1VoiceSynthesizePost(body);
      return response as unknown as SynthesizeSpeechResponse;
    } catch (error) {
      console.error('[VoiceAPI] Failed to synthesize speech:', error);
      return null;
    }
  },
};

/**
 * Analytics API (Sentiment Analysis)
 */
export const AnalyticsAPI = {
  /**
   * Analyze sentiment of candidate response
   * Proxies to analytics-service when enabled.
   * Useful for scoring and feedback during interview.
   */
  async analyzeSentiment(
    request: AnalyzeSentimentRequest
  ): Promise<AnalyzeSentimentResponse | null> {
    try {
      const body = {
        text: request.text,
        context: request.context || 'interview_response',
      };
      const response = await DefaultService.analyzeSentimentApiV1AnalyticsSentimentPost(body);
      
      // Map gateway response to our interface
      return {
        score: (response as any)?.score ?? 0,
        magnitude: (response as any)?.magnitude ?? 0,
        sentences: (response as any)?.sentences,
        entities: (response as any)?.entities,
      };
    } catch (error) {
      console.error('[AnalyticsAPI] Failed to analyze sentiment:', error);
      return null;
    }
  },
};

/**
 * Health & System API
 */
export const SystemAPI = {
  /**
   * Get gateway and service health
   */
  async getHealth(): Promise<HealthResponse | null> {
    try {
      return (await DefaultService.healthCheckHealthGet()) as unknown as HealthResponse;
    } catch (error) {
      console.error('[SystemAPI] Failed to get health:', error);
      return null;
    }
  },

  /**
   * Get comprehensive system status
   */
  async getStatus(): Promise<Record<string, any> | null> {
    try {
      return await DefaultService.systemStatusApiV1SystemStatusGet();
    } catch (error) {
      console.error('[SystemAPI] Failed to get system status:', error);
      return null;
    }
  },

  /**
   * Get all registered services
   */
  async listServices(): Promise<Record<string, any> | null> {
    try {
      return await DefaultService.listServicesApiV1ServicesGet();
    } catch (error) {
      console.error('[SystemAPI] Failed to list services:', error);
      return null;
    }
  },

  /**
   * Get complete dashboard data
   */
  async getDashboard(): Promise<Record<string, any> | null> {
    try {
      return await DefaultService.getDashboardApiV1DashboardGet();
    } catch (error) {
      console.error('[SystemAPI] Failed to get dashboard:', error);
      return null;
    }
  },
};

/**
 * Convenience export for all APIs
 */
export const GatewayClient = {
  configure: configureGateway,
  interview: InterviewAPI,
  models: ModelsAPI,
  voice: VoiceAPI,
  analytics: AnalyticsAPI,
  system: SystemAPI,
};

export default GatewayClient;
