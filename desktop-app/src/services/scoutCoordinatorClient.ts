/**
 * Scout Coordinator Agent API Client
 *
 * Connects the desktop app to the scout-coordinator-agent (port 8095)
 * for candidate sourcing pipeline management.
 */

const SCOUT_COORDINATOR_URL = process.env.REACT_APP_SCOUT_COORDINATOR_URL || 'http://localhost:8095';

export interface PipelineConfig {
    jobDescription: string;
    location?: string;
    skills?: string[];
    tools: string[]; // ['github', 'stackoverflow', 'googleXray', 'contactout', 'salesql']
    userId?: string;
}

export interface PipelineResponse {
    pipeline_id: string;
    status: string;
    message?: string;
}

export interface PipelineStatus {
    pipeline_id: string;
    state: 'pending' | 'scanning' | 'enriching' | 'scoring' | 'engaging' | 'completed' | 'failed';
    progress_percentage: number;
    recent_activities?: Activity[];
    candidates_found?: number;
    error_message?: string;
}

export interface Activity {
    timestamp: string;
    type: 'success' | 'info' | 'warning' | 'error';
    icon: string;
    message: string;
}

export interface Candidate {
    id: string;
    name: string;
    headline?: string;
    location?: string;
    score: number;
    skills?: string[];
    github_url?: string;
    github_stars?: number;
    linkedin_url?: string;
    stackoverflow_url?: string;
    stackoverflow_reputation?: number;
    avatar_url?: string;
    bio?: string;
    experience?: Array<{
        title: string;
        company: string;
        duration: string;
    }>;
    scoring?: {
        skills_match: number;
        experience: number;
        activity: number;
        location: number;
        reputation: number;
    };
}

export interface CandidatesResponse {
    pipeline_id: string;
    total_candidates: number;
    candidates: Candidate[];
}

export interface AgentHealthResponse {
    [agentName: string]: {
        status: 'healthy' | 'unhealthy' | 'unreachable' | 'unknown';
        last_check?: string;
        response_time_ms?: number;
    };
}

export class ScoutCoordinatorClient {
    private baseUrl: string;

    constructor(baseUrl?: string) {
        this.baseUrl = baseUrl || SCOUT_COORDINATOR_URL;
    }

    /**
     * Create a new sourcing pipeline
     */
    async createPipeline(config: PipelineConfig): Promise<PipelineResponse> {
        try {
            const response = await fetch(`${this.baseUrl}/pipelines/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_description: config.jobDescription,
                    location: config.location,
                    required_skills: config.skills || [],
                    sourcing_methods: config.tools,
                    user_id: config.userId || 'desktop_user',
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Pipeline creation failed: ${response.statusText} - ${errorText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to create pipeline:', error);
            throw error;
        }
    }

    /**
     * Get pipeline status
     */
    async getPipelineStatus(pipelineId: string): Promise<PipelineStatus> {
        try {
            const response = await fetch(`${this.baseUrl}/pipelines/${pipelineId}/status`);

            if (!response.ok) {
                throw new Error(`Failed to get status: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get pipeline status:', error);
            throw error;
        }
    }

    /**
     * Get candidates from completed pipeline
     */
    async getCandidates(pipelineId: string): Promise<CandidatesResponse> {
        try {
            const response = await fetch(`${this.baseUrl}/pipelines/${pipelineId}/candidates`);

            if (!response.ok) {
                throw new Error(`Failed to get candidates: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to get candidates:', error);
            throw error;
        }
    }

    /**
     * Get agent health status
     */
    async getAgentHealth(): Promise<AgentHealthResponse> {
        try {
            const response = await fetch(`${this.baseUrl}/agents/health`);

            if (!response.ok) {
                console.warn('Agent health check failed, using fallback');
                return this.getFallbackAgentHealth();
            }

            return await response.json();
        } catch (error) {
            console.warn('Agent health check error, using fallback:', error);
            return this.getFallbackAgentHealth();
        }
    }

    /**
     * Fallback agent health (when service unavailable)
     */
    private getFallbackAgentHealth(): AgentHealthResponse {
        return {
            'scout-coordinator': { status: 'unreachable' },
            'data-enrichment': { status: 'unknown' },
            'quality-focused': { status: 'unknown' },
            'proactive-scanning': { status: 'unknown' },
            'boolean-mastery': { status: 'unknown' },
        };
    }

    /**
     * Check if scout coordinator is reachable
     */
    async checkHealth(): Promise<boolean> {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(5000), // 5 second timeout
            });
            return response.ok;
        } catch (error) {
            console.error('Scout coordinator health check failed:', error);
            return false;
        }
    }
}

// Export singleton instance
export const scoutCoordinator = new ScoutCoordinatorClient();
