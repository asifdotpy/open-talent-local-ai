/**
 * Integration Service Client
 * Connects desktop app to microservices gateway (port 8009)
 */

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

/**
 * Fetch gateway and service health status
 */
export async function fetchIntegrationHealth(): Promise<IntegrationHealth | null> {
  try {
    const res = await fetch(`${INTEGRATION_BASE_URL}/health`);
    if (!res.ok) return null;
    const data = await res.json();

    // Normalize a few common shapes into IntegrationHealth
    const services: ServiceHealth[] = [];
    const svc = data.services || data?.serviceStatuses || {};
    for (const [name, info] of Object.entries(svc)) {
      const statusRaw = (info as any)?.status || (info as any) || 'offline';
      const status = typeof statusRaw === 'string' ? statusRaw.toLowerCase() : 'offline';
      services.push({
        name,
        status: status === 'healthy' || status === 'online' ? 'online' : (status as any),
        latencyMs: (info as any)?.latencyMs,
        details: (info as any) || undefined,
      });
    }

    const overall = (data.status || 'online').toLowerCase();
    return { status: overall as any, services };
  } catch {
    return null;
  }
}

/**
 * List all available AI models from gateway
 */
export async function listModels(): Promise<ModelInfo[]> {
  try {
    const res = await fetch(`${INTEGRATION_BASE_URL}/api/v1/models`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.models || [];
  } catch (error) {
    console.error('[IntegrationClient] Failed to list models:', error);
    return [];
  }
}

/**
 * Start a new interview via gateway
 */
export async function startInterview(
  request: StartInterviewRequest
): Promise<InterviewSession | null> {
  try {
    const res = await fetch(`${INTEGRATION_BASE_URL}/api/v1/interviews/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    console.error('[IntegrationClient] Failed to start interview:', error);
    return null;
  }
}

/**
 * Submit candidate response and get next question
 */
export async function respondToInterview(
  request: InterviewResponseRequest
): Promise<InterviewSession | null> {
  try {
    const res = await fetch(`${INTEGRATION_BASE_URL}/api/v1/interviews/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    console.error('[IntegrationClient] Failed to respond to interview:', error);
    return null;
  }
}

/**
 * Get interview summary
 */
export async function getInterviewSummary(
  session: InterviewSession
): Promise<{ summary: string; role: string; questionsAsked: number; responsesGiven: number } | null> {
  try {
    const res = await fetch(`${INTEGRATION_BASE_URL}/api/v1/interviews/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(session),
    });
    if (!res.ok) return null;
    return await res.json();
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
    const res = await fetch(`${INTEGRATION_BASE_URL}/api/v1/dashboard`);
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    console.error('[IntegrationClient] Failed to get dashboard:', error);
    return null;
  }
}
