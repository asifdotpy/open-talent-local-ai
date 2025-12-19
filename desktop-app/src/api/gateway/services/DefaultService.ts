/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnalyzeSentimentRequest } from '../models/AnalyzeSentimentRequest';
import type { AnalyzeSentimentResponse } from '../models/AnalyzeSentimentResponse';
import type { HealthResponse } from '../models/HealthResponse';
import type { InterviewResponseRequest } from '../models/InterviewResponseRequest';
import type { InterviewSession } from '../models/InterviewSession';
import type { ModelsResponse } from '../models/ModelsResponse';
import type { StartInterviewRequest } from '../models/StartInterviewRequest';
import type { SynthesizeSpeechRequest } from '../models/SynthesizeSpeechRequest';
import type { SynthesizeSpeechResponse } from '../models/SynthesizeSpeechResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Health Check
     * Get gateway and service health status.
     *
     * Returns overall status and per-service details for status bar.
     * @returns HealthResponse Successful Response
     * @throws ApiError
     */
    public static healthCheckHealthGet(): CancelablePromise<HealthResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }
    /**
     * System Status
     * Get comprehensive system status.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static systemStatusApiV1SystemStatusGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/system/status',
        });
    }
    /**
     * List Services
     * List all 14 registered OpenTalent microservices.
     *
     * Returns registry with URLs and current status for each service.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listServicesApiV1ServicesGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/services',
        });
    }
    /**
     * List Models
     * List all available models from all sources.
     *
     * Merges models from granite-interview-service and ollama.
     * Returns fallback if backends unavailable.
     * @returns ModelsResponse Successful Response
     * @throws ApiError
     */
    public static listModelsApiV1ModelsGet(): CancelablePromise<ModelsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/models',
        });
    }
    /**
     * Select Model
     * Select a specific model for interviews.
     *
     * Validates model exists in available models.
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static selectModelApiV1ModelsSelectPost(
        modelId: string,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/models/select',
            query: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Synthesize Speech
     * Proxy text-to-speech to voice-service when enabled.
     * @param requestBody
     * @returns SynthesizeSpeechResponse Successful Response
     * @throws ApiError
     */
    public static synthesizeSpeechApiV1VoiceSynthesizePost(
        requestBody: SynthesizeSpeechRequest,
    ): CancelablePromise<SynthesizeSpeechResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/voice/synthesize',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Analyze Sentiment
     * Proxy sentiment analysis to analytics-service when enabled.
     * @param requestBody
     * @returns AnalyzeSentimentResponse Successful Response
     * @throws ApiError
     */
    public static analyzeSentimentApiV1AnalyticsSentimentPost(
        requestBody: AnalyzeSentimentRequest,
    ): CancelablePromise<AnalyzeSentimentResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/analytics/sentiment',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Execute Agent
     * Proxy agent execution to agents-service when enabled.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static executeAgentApiV1AgentsExecutePost(
        requestBody: Record<string, any>,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/agents/execute',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Start Interview
     * Start a new interview session.
     *
     * Routes to granite-interview-service if available, otherwise uses fallback templates.
     * @param requestBody
     * @returns InterviewSession Successful Response
     * @throws ApiError
     */
    public static startInterviewApiV1InterviewsStartPost(
        requestBody: StartInterviewRequest,
    ): CancelablePromise<InterviewSession> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/interviews/start',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Respond To Interview
     * Submit candidate response and get next question.
     *
     * Continues interview flow with next question or marks complete if all questions done.
     * @param requestBody
     * @returns InterviewSession Successful Response
     * @throws ApiError
     */
    public static respondToInterviewApiV1InterviewsRespondPost(
        requestBody: InterviewResponseRequest,
    ): CancelablePromise<InterviewSession> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/interviews/respond',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Interview Summary
     * Get interview summary and assessment.
     *
     * Returns simple summary with question count and candidate info.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getInterviewSummaryApiV1InterviewsSummaryPost(
        requestBody: InterviewSession,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/interviews/summary',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Dashboard
     * Get complete dashboard data in one request.
     *
     * Combines health, models, and system info for UI.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getDashboardApiV1DashboardGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dashboard',
        });
    }
    /**
     * Root
     * Root endpoint with API info.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static rootGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }
}
