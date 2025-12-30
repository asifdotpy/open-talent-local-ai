/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request to start an interview.
 */
export type StartInterviewRequest = {
    /**
     * Interview role (Software Engineer, Product Manager, Data Analyst)
     */
    role: string;
    /**
     * Model to use
     */
    model?: string;
    /**
     * Total questions
     */
    totalQuestions?: number;
};

