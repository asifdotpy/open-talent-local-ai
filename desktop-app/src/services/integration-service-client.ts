/**
 * Integration Service Client (typed)
 * Connects desktop app to microservices gateway (port 8009)
 * Now uses generated OpenAPI client where available.
 */

import { DefaultService, OpenAPI } from '../api/gateway';
import type { HealthResponse } from '../api/gateway/models/HealthResponse';
import type { ModelsResponse } from '../api/gateway/models/ModelsResponse';
import type { StartInterviewRequest as StartReq } from '../api/gateway/models/StartInterviewRequest';
import type { InterviewResponseRequest as RespondReq } from '../api/gateway/models/InterviewResponseRequest';
import type { InterviewSession as SessionModel } from '../api/gateway/models/InterviewSession';

export interface ServiceHealth {
  name: string;
  status: 'online' | 'offline' | 'degraded';
  latencyMs?: number;
  details?: Record<string, any>;
}

export interface IntegrationHealth {
  status: 'online' | 'offline' | 'degraded';
  services: ServiceHealth[];
}

export interface ModelInfo {
  id: string;
  name: string;
  paramCount: string;
  ramRequired: string;
  downloadSize: string;
  description: string;
  dataset?: string;
  source: string;
}

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

export interface StartInterviewRequest {
  role: string;
  model: string;
  totalQuestions: number;
}

export interface InterviewResponseRequest {
  sessionId?: string;
  message: string;
  session?: InterviewSession;
}

const INTEGRATION_BASE_URL = process.env.INTEGRATION_BASE_URL || 'http://localhost:8009';
OpenAPI.BASE = INTEGRATION_BASE_URL;

/**
 * Convert generated HealthResponse to local IntegrationHealth shape
 */
function toIntegrationHealth(hr: HealthResponse): IntegrationHealth {
  const services: ServiceHealth[] = Object.entries(hr.services || {}).map(([name, info]) => {
    const statusRaw: any = (info as any)?.status ?? info ?? 'offline';
    const status = typeof statusRaw === 'string' ? statusRaw.toLowerCase() : 'offline';
    return {
      name,
      status: (status === 'healthy' || status === 'online' ? 'online' : (status as any)) as any,
      latencyMs: (info as any)?.latencyMs,
      details: info as any,
    };
  });
  return { status: (hr.status as any) ?? 'offline', services };
}

/**
 * Fetch gateway and service health status (typed)
 */
export async function fetchIntegrationHealth(): Promise<IntegrationHealth | null> {
  try {
    const data = await DefaultService.healthCheckHealthGet();
    return toIntegrationHealth(data);
  } catch {
    return null;
  }
}

/**
 * List all available AI models from gateway (typed)
 */
export async function listModels(): Promise<ModelInfo[]> {
  try {
    const data: ModelsResponse = await DefaultService.listModelsApiV1ModelsGet();
    return (data.models || []) as unknown as ModelInfo[];
  } catch (error) {
    console.error('[IntegrationClient] Failed to list models:', error);
    return [];
  }
}

/**
 * Start a new interview via gateway (typed)
 */
export async function startInterview(
  request: StartInterviewRequest
): Promise<InterviewSession | null> {
  try {
    const body: StartReq = {
      role: request.role,
      model: request.model,
      totalQuestions: request.totalQuestions,
    };
    const session: SessionModel = await DefaultService.startInterviewApiV1InterviewsStartPost(body);
    return session as unknown as InterviewSession;
  } catch (error) {
    console.error('[IntegrationClient] Failed to start interview:', error);
    return null;
  }
}

/**
 * Submit candidate response and get next question (typed)
 */
export async function respondToInterview(
  request: InterviewResponseRequest
): Promise<InterviewSession | null> {
  try {
    const body: RespondReq = {
      message: request.message,
      session: request.session as any,
      sessionId: request.sessionId,
    };
    const updated: SessionModel = await DefaultService.respondToInterviewApiV1InterviewsRespondPost(body);
    return updated as unknown as InterviewSession;
  } catch (error) {
    console.error('[IntegrationClient] Failed to respond to interview:', error);
    return null;
  }
}

/**
 * Get interview summary (typed)
 */
export async function getInterviewSummary(
  session: InterviewSession
): Promise<{ summary: string; role: string; questionsAsked: number; responsesGiven: number } | null> {
  try {
    const res = await DefaultService.getInterviewSummaryApiV1InterviewsSummaryPost(session as any);
    return res as any;
  } catch (error) {
    console.error('[IntegrationClient] Failed to get interview summary:', error);
    return null;
  }
}

/**
 * Get complete dashboard data
 */
export async function getDashboard(): Promise<any> {
  try {
    return await DefaultService.getDashboardApiV1DashboardGet();
  } catch (error) {
    console.error('[IntegrationClient] Failed to get dashboard:', error);
    return null;
  }
}
