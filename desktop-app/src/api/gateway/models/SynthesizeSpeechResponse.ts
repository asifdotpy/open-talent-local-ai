/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response with synthesized audio.
 */
export type SynthesizeSpeechResponse = {
    /**
     * URL to audio file
     */
    audioUrl?: (string | null);
    /**
     * Base64-encoded audio
     */
    audioBase64?: (string | null);
    /**
     * Audio duration in seconds
     */
    duration?: (number | null);
    /**
     * Audio format (mp3, wav, ogg)
     */
    format?: string;
    /**
     * Text that was synthesized
     */
    text: string;
    /**
     * Voice used
     */
    voice: string;
};
