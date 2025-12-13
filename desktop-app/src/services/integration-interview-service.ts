/**
 * Integration Interview Service
 * Routes all operations through the Desktop Integration Service (port 8009)
 * Falls back to direct Ollama if integration service unavailable
 */

import * as IntegrationClient from './integration-service-client';
import { InterviewService as OllamaInterviewService, InterviewSession, Message } from './interview-service';
import { AIProvider } from '../providers/ai/ai-provider.interface';

export { InterviewSession, Message };

export interface ModelInfo {
  id: string;
  name: string;
  paramCount?: string;
  ramRequired?: string;
  downloadSize?: string;
  description?: string;
  source?: string;
}

export class IntegrationInterviewService {
  private mode: 'integration' | 'ollama' = 'integration';
  private ollamaService: OllamaInterviewService;
  private isIntegrationHealthy = false;

  constructor(ollamaProvider: AIProvider) {
    this.ollamaService = new OllamaInterviewService(ollamaProvider);
    this.checkIntegrationHealth();
  }

  /**
   * Check if integration service is available
   */
  private async checkIntegrationHealth(): Promise<void> {
    try {
      const health = await IntegrationClient.fetchIntegrationHealth();
      this.isIntegrationHealthy = health !== null;
      
      // Auto-switch to integration mode if available
      if (this.isIntegrationHealthy) {
        this.mode = 'integration';
        console.log('[IntegrationInterviewService] Integration service detected, using gateway mode');
      } else {
        this.mode = 'ollama';
        console.log('[IntegrationInterviewService] Integration service unavailable, using direct Ollama mode');
      }
    } catch (error) {
      this.isIntegrationHealthy = false;
      this.mode = 'ollama';
      console.warn('[IntegrationInterviewService] Failed to check integration health:', error);
    }
  }

  /**
   * Get current mode
   */
  getMode(): 'integration' | 'ollama' {
    return this.mode;
  }

  /**
   * Force switch to specific mode
   */
  setMode(mode: 'integration' | 'ollama'): void {
    this.mode = mode;
    console.log(`[IntegrationInterviewService] Switched to ${mode} mode`);
  }

  /**
   * Check overall service status (integration or ollama)
   */
  async checkStatus(): Promise<boolean> {
    if (this.mode === 'integration') {
      const health = await IntegrationClient.fetchIntegrationHealth();
      return health !== null && health.status !== 'offline';
    } else {
      return await this.ollamaService.checkStatus();
    }
  }

  /**
   * List available models
   */
  async listModels(): Promise<ModelInfo[]> {
    if (this.mode === 'integration') {
      try {
        const models = await IntegrationClient.listModels();
        if (models && models.length > 0) {
          return models.map(m => ({
            id: m.id,
            name: m.name,
            paramCount: m.paramCount,
            ramRequired: m.ramRequired,
            downloadSize: m.downloadSize,
            description: m.description,
            source: m.source,
          }));
        }
        
        // Fallback to Ollama if integration returns no models
        console.warn('[IntegrationInterviewService] No models from integration service, falling back to Ollama');
        this.mode = 'ollama';
        return this.listModelsFromOllama();
      } catch (error) {
        console.error('[IntegrationInterviewService] Failed to list models from integration service:', error);
        this.mode = 'ollama';
        return this.listModelsFromOllama();
      }
    } else {
      return this.listModelsFromOllama();
    }
  }

  /**
   * List models from Ollama (fallback)
   */
  private async listModelsFromOllama(): Promise<ModelInfo[]> {
    const ollamaModels = await this.ollamaService.listModels();
    return ollamaModels.map(m => ({
      id: m.name,
      name: m.name,
      source: 'ollama',
    }));
  }

  /**
   * Start a new interview
   */
  async startInterview(
    role: string,
    model: string,
    totalQuestions: number = 5
  ): Promise<InterviewSession> {
    if (this.mode === 'integration') {
      try {
        const session = await IntegrationClient.startInterview({
          role,
          model,
          totalQuestions,
        });

        if (session) {
          console.log('[IntegrationInterviewService] Interview started via integration service');
          return session;
        }

        // Fallback to Ollama if integration fails
        console.warn('[IntegrationInterviewService] Integration service failed, falling back to Ollama');
        this.mode = 'ollama';
        return await this.ollamaService.startInterview(role, model, totalQuestions);
      } catch (error) {
        console.error('[IntegrationInterviewService] Failed to start interview via integration service:', error);
        this.mode = 'ollama';
        return await this.ollamaService.startInterview(role, model, totalQuestions);
      }
    } else {
      return await this.ollamaService.startInterview(role, model, totalQuestions);
    }
  }

  /**
   * Send response to interview
   */
  async sendResponse(session: InterviewSession, userResponse: string): Promise<InterviewSession> {
    if (this.mode === 'integration') {
      try {
        const updatedSession = await IntegrationClient.respondToInterview({
          message: userResponse,
          session,
        });

        if (updatedSession) {
          console.log('[IntegrationInterviewService] Response sent via integration service');
          return updatedSession;
        }

        // Fallback to Ollama if integration fails
        console.warn('[IntegrationInterviewService] Integration service failed, falling back to Ollama');
        this.mode = 'ollama';
        return await this.ollamaService.sendResponse(session, userResponse);
      } catch (error) {
        console.error('[IntegrationInterviewService] Failed to send response via integration service:', error);
        this.mode = 'ollama';
        return await this.ollamaService.sendResponse(session, userResponse);
      }
    } else {
      return await this.ollamaService.sendResponse(session, userResponse);
    }
  }

  /**
   * Get interview summary
   */
  getInterviewSummary(session: InterviewSession): string {
    // Use local summary generation (same for both modes)
    return this.ollamaService.getInterviewSummary(session);
  }

  /**
   * Check if service is healthy
   */
  isServiceHealthy(): boolean {
    if (this.mode === 'integration') {
      return this.isIntegrationHealthy;
    } else {
      return this.ollamaService.isServiceHealthy();
    }
  }

  /**
   * Get integration health details
   */
  async getIntegrationHealth(): Promise<IntegrationClient.IntegrationHealth | null> {
    return await IntegrationClient.fetchIntegrationHealth();
  }

  /**
   * Get dashboard data (integration mode only)
   */
  async getDashboard(): Promise<any> {
    if (this.mode === 'integration') {
      return await IntegrationClient.getDashboard();
    }
    return null;
  }
}
