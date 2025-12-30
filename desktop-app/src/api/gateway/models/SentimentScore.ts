/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Sentiment analysis result.
 */
export type SentimentScore = {
    /**
     * Sentiment score (-1.0 to 1.0)
     */
    score: number;
    /**
     * Sentiment magnitude (0.0 to 1.0)
     */
    magnitude: number;
    /**
     * Sentiment label (positive, negative, neutral)
     */
    label: string;
};

