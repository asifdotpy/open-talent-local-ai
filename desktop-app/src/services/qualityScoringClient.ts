/**
 * Client for interacting with the quality-focused-agent
 * for candidate scoring and ranking.
 */

const QUALITY_FOCUSED_URL = process.env.REACT_APP_QUALITY_FOCUSED_URL || 'http://localhost:8096';

export interface ScoreRequest {
    candidate_id: string;
    job_description: string;
    candidate_profile: any;
}

export interface ScoreResult {
    candidate_id: string;
    overall_score: number;
    skill_match_score: number;
    experience_score: number;
    culture_fit_score: number;
    bias_flags: string[];
    recommendation: string;
    timestamp: string;
}

export class QualityScoringClient {
    private baseUrl: string;

    constructor(baseUrl?: string) {
        this.baseUrl = baseUrl || QUALITY_FOCUSED_URL;
    }

    /**
     * Get quality score for a candidate
     */
    async scoreCandidate(request: ScoreRequest): Promise<ScoreResult> {
        try {
            const response = await fetch(`${this.baseUrl}/score`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                throw new Error(`Failed to score candidate: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error scoring candidate:', error);
            throw error;
        }
    }

    /**
     * Check if the service is healthy
     */
    async checkHealth(): Promise<boolean> {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return response.ok;
        } catch (error) {
            return false;
        }
    }
}

export const qualityScoringClient = new QualityScoringClient();
