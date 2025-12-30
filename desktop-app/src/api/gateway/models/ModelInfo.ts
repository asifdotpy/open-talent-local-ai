/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Model information.
 */
export type ModelInfo = {
    /**
     * Model ID
     */
    id: string;
    /**
     * Human-readable name
     */
    name: string;
    /**
     * Parameter count (350M, 2B, 8B, etc.)
     */
    paramCount: string;
    /**
     * RAM required
     */
    ramRequired: string;
    /**
     * Download size
     */
    downloadSize: string;
    /**
     * Model description
     */
    description: string;
    /**
     * Training dataset
     */
    dataset?: (string | null);
    /**
     * Model source
     */
    source?: (string | null);
};

