/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InterviewSession } from './InterviewSession';
/**
 * Request to respond to interview question.
 */
export type InterviewResponseRequest = {
    /**
     * Session ID (optional)
     */
    sessionId?: (string | null);
    /**
     * User's response message
     */
    message: string;
    /**
     * Full session (client can send entire session)
     */
    session?: (InterviewSession | null);
};

