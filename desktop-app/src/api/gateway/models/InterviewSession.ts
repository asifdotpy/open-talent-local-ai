/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InterviewConfig } from './InterviewConfig';
import type { Message } from './Message';
/**
 * Interview session data matching desktop app contract.
 */
export type InterviewSession = {
    config: InterviewConfig;
    messages: Array<Message>;
    currentQuestion: number;
    isComplete: boolean;
};

