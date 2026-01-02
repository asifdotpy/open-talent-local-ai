/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request to analyze sentiment of text.
 */
export type AnalyzeSentimentRequest = {
    /**
     * Text to analyze
     */
    text: string;
    /**
     * Context for analysis (e.g., 'interview_response', 'general')
     */
    context?: (string | null);
};
