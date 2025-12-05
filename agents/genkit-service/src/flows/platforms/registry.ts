/**
 * Platform Registry
 * Central registry for all platform scanning plugins.
 * Allows dynamic discovery and execution of platform scanners.
 */

import { z } from 'zod';
import * as linkedin from './linkedin';
import * as github from './github';
import * as stackoverflow from './stackoverflow';

// Platform type enum
export const PlatformType = z.enum(['linkedin', 'github', 'stackoverflow', 'indeed', 'angellist']);

// Generic platform scan request
export const PlatformScanRequestSchema = z.object({
  platform: PlatformType,
  query: z.string(),
  maxResults: z.number().default(50),
  filters: z.record(z.any()).optional(),
});

// Platform metadata interface
export interface PlatformMetadata {
  name: string;
  type: string;
  capabilities: string[];
  rateLimit: {
    requestsPerMinute?: number;
    requestsPerHour?: number;
    requestsPerDay?: number;
  };
  authentication: {
    required: boolean;
    type: string;
  };
}

// Platform scanner interface
export interface PlatformScanner {
  scan: (request: any) => Promise<any>;
  metadata: PlatformMetadata;
  requestSchema: z.ZodSchema;
  responseSchema: z.ZodSchema;
}

/**
 * Platform Registry Class
 * Manages all available platform scanners and provides unified access.
 */
export class PlatformRegistry {
  private platforms: Map<string, PlatformScanner> = new Map();

  constructor() {
    this.registerDefaultPlatforms();
  }

  /**
   * Register all default platform scanners.
   */
  private registerDefaultPlatforms(): void {
    // Register LinkedIn
    this.register('linkedin', {
      scan: linkedin.scanLinkedIn,
      metadata: linkedin.platformMetadata,
      requestSchema: linkedin.LinkedInScanRequestSchema,
      responseSchema: linkedin.LinkedInScanResponseSchema,
    });

    // Register GitHub
    this.register('github', {
      scan: github.scanGitHub,
      metadata: github.platformMetadata,
      requestSchema: github.GitHubScanRequestSchema,
      responseSchema: github.GitHubScanResponseSchema,
    });

    // Register Stack Overflow
    this.register('stackoverflow', {
      scan: stackoverflow.scanStackOverflow,
      metadata: stackoverflow.platformMetadata,
      requestSchema: stackoverflow.StackOverflowScanRequestSchema,
      responseSchema: stackoverflow.StackOverflowScanResponseSchema,
    });

    console.log(`✅ Registered ${this.platforms.size} platform scanners`);
  }

  /**
   * Register a new platform scanner.
   */
  public register(name: string, scanner: PlatformScanner): void {
    this.platforms.set(name.toLowerCase(), scanner);
  }

  /**
   * Get a platform scanner by name.
   */
  public get(name: string): PlatformScanner | undefined {
    return this.platforms.get(name.toLowerCase());
  }

  /**
   * Check if a platform is registered.
   */
  public has(name: string): boolean {
    return this.platforms.has(name.toLowerCase());
  }

  /**
   * Get all registered platform names.
   */
  public listPlatforms(): string[] {
    return Array.from(this.platforms.keys());
  }

  /**
   * Get metadata for all platforms.
   */
  public getAllMetadata(): Record<string, PlatformMetadata> {
    const metadata: Record<string, PlatformMetadata> = {};
    this.platforms.forEach((scanner, name) => {
      metadata[name] = scanner.metadata;
    });
    return metadata;
  }

  /**
   * Execute a scan on a specific platform.
   */
  public async scan(platformName: string, request: any): Promise<any> {
    const scanner = this.get(platformName);
    
    if (!scanner) {
      throw new Error(`Platform '${platformName}' is not registered. Available platforms: ${this.listPlatforms().join(', ')}`);
    }

    // Validate request against platform schema
    try {
      scanner.requestSchema.parse(request);
    } catch (error) {
      throw new Error(`Invalid request for platform '${platformName}': ${error}`);
    }

    console.log(`🔍 Scanning ${platformName}...`);
    const result = await scanner.scan(request);

    // Validate response
    try {
      scanner.responseSchema.parse(result);
    } catch (error) {
      console.error(`Response validation failed for ${platformName}:`, error);
    }

    return result;
  }

  /**
   * Scan multiple platforms concurrently.
   */
  public async scanMultiple(
    requests: Array<{ platform: string; request: any }>
  ): Promise<Array<{ platform: string; result: any; error?: string }>> {
    const scanPromises = requests.map(async ({ platform, request }) => {
      try {
        const result = await this.scan(platform, request);
        return { platform, result };
      } catch (error) {
        return {
          platform,
          result: null,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    });

    return Promise.all(scanPromises);
  }

  /**
   * Get platforms by capability.
   */
  public getPlatformsByCapability(capability: string): string[] {
    const platforms: string[] = [];
    
    this.platforms.forEach((scanner, name) => {
      if (scanner.metadata.capabilities.includes(capability)) {
        platforms.push(name);
      }
    });

    return platforms;
  }

  /**
   * Get rate limit info for a platform.
   */
  public getRateLimit(platformName: string): PlatformMetadata['rateLimit'] | null {
    const scanner = this.get(platformName);
    return scanner ? scanner.metadata.rateLimit : null;
  }
}

// Export singleton instance
export const platformRegistry = new PlatformRegistry();

// Export schema types
export type PlatformScanRequest = z.infer<typeof PlatformScanRequestSchema>;
