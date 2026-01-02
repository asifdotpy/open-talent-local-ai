/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SentimentScore } from './SentimentScore';
/**
 * Response with sentiment analysis.
 */
export type AnalyzeSentimentResponse = {
    /**
     * Sentiment analysis
     */
    sentiment: SentimentScore;
    /**
     * Text that was analyzed
     */
    text: string;
    /**
     * Analysis context
     */
    context?: (string | null);
    /**
     * Per-sentence analysis
     */
    sentences?: null;
};
