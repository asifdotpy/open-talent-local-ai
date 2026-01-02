/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request to synthesize speech from text.
 */
export type SynthesizeSpeechRequest = {
    /**
     * Text to synthesize
     */
    text: string;
    /**
     * Voice identifier (e.g., en-US-Neural2-C, en-GB-Neural2-A)
     */
    voice?: string;
    /**
     * Speech speed (0.5-2.0)
     */
    speed?: number;
    /**
     * Pitch adjustment (-20 to 20)
     */
    pitch?: number;
};
