/**
 * Redis Pub/Sub Integration for GenKit Service
 * Handles event-driven communication with other agents
 */

import Redis from 'ioredis';
import { platformRegistry } from './flows/platforms/registry';

// Redis client configuration
const REDIS_HOST = process.env.REDIS_HOST || 'localhost';
const REDIS_PORT = parseInt(process.env.REDIS_PORT || '6379', 10);

// Topic names
const TOPICS = {
  SCANNING: 'agents:scanning',
  CANDIDATES: 'agents:candidates',
  PIPELINE: 'agents:pipeline',
  ERRORS: 'agents:errors',
};

// Message types
interface ScanRequest {
  source_agent: string;
  message_type: 'SCAN_REQUEST';
  payload: {
    pipeline_id: string;
    job_id?: string;
    platforms: Array<{
      platform: string;
      query: string;
      filters?: Record<string, any>;
      maxResults?: number;
    }>;
  };
  correlation_id: string;
  timestamp: string;
}

interface CandidateFoundEvent {
  source_agent: string;
  message_type: 'CANDIDATE_FOUND';
  payload: {
    pipeline_id: string;
    platform: string;
    candidates: Array<{
      id: string;
      name: string;
      profile_url: string;
      skills: string[];
      experience?: string;
      location?: string;
      [key: string]: any;
    }>;
  };
  correlation_id: string;
  timestamp: string;
}

interface ScanCompletedEvent {
  source_agent: string;
  message_type: 'SCAN_COMPLETED';
  payload: {
    pipeline_id: string;
    total_candidates: number;
    platforms_scanned: string[];
    scan_duration_ms: number;
  };
  correlation_id: string;
  timestamp: string;
}

/**
 * Redis Pub/Sub Manager for GenKit Service
 */
export class RedisIntegration {
  private subscriber: Redis;
  private publisher: Redis;
  private isConnected: boolean = false;

  constructor() {
    // Create separate connections for pub and sub (Redis best practice)
    this.subscriber = new Redis({
      host: REDIS_HOST,
      port: REDIS_PORT,
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        console.log(`Redis subscriber retry attempt ${times}, delay: ${delay}ms`);
        return delay;
      },
    });

    this.publisher = new Redis({
      host: REDIS_HOST,
      port: REDIS_PORT,
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        console.log(`Redis publisher retry attempt ${times}, delay: ${delay}ms`);
        return delay;
      },
    });

    this.setupConnectionHandlers();
  }

  /**
   * Setup connection event handlers
   */
  private setupConnectionHandlers(): void {
    this.subscriber.on('connect', () => {
      console.log('✅ Redis subscriber connected');
      this.isConnected = true;
    });

    this.subscriber.on('error', (err) => {
      console.error('❌ Redis subscriber error:', err);
      this.isConnected = false;
    });

    this.publisher.on('connect', () => {
      console.log('✅ Redis publisher connected');
    });

    this.publisher.on('error', (err) => {
      console.error('❌ Redis publisher error:', err);
    });

    this.subscriber.on('reconnecting', () => {
      console.log('🔄 Redis subscriber reconnecting...');
    });

    this.publisher.on('reconnecting', () => {
      console.log('🔄 Redis publisher reconnecting...');
    });
  }

  /**
   * Initialize subscriptions and message handlers
   */
  async initialize(): Promise<void> {
    try {
      // Subscribe to scanning topic
      await this.subscriber.subscribe(TOPICS.SCANNING);
      console.log(`📡 Subscribed to ${TOPICS.SCANNING}`);

      // Handle incoming messages
      this.subscriber.on('message', async (channel, message) => {
        await this.handleMessage(channel, message);
      });

      console.log('✅ Redis integration initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Redis integration:', error);
      throw error;
    }
  }

  /**
   * Handle incoming Redis messages
   */
  private async handleMessage(channel: string, message: string): Promise<void> {
    try {
      console.log(`📨 Received message on ${channel}`);
      
      if (channel === TOPICS.SCANNING) {
        const scanRequest: ScanRequest = JSON.parse(message);
        await this.handleScanRequest(scanRequest);
      }
    } catch (error) {
      console.error('❌ Error handling message:', error);
      await this.publishError(error as Error, message);
    }
  }

  /**
   * Handle scan request from Scout AI
   */
  private async handleScanRequest(request: ScanRequest): Promise<void> {
    const startTime = Date.now();
    console.log(`🔍 Processing scan request for pipeline: ${request.payload.pipeline_id}`);

    try {
      // Prepare platform scan requests
      const scanRequests = request.payload.platforms.map(p => ({
        platform: p.platform,
        request: {
          searchQuery: p.query,
          maxResults: p.maxResults || 50,
          ...p.filters,
        },
      }));

      // Execute multi-platform scanning
      const results = await platformRegistry.scanMultiple(scanRequests);

      // Process results and publish events
      let totalCandidates = 0;
      const platformsScanned: string[] = [];

      for (const result of results) {
        if (result.error) {
          console.error(`❌ Scan failed for ${result.platform}:`, result.error);
          continue;
        }

        // Extract candidates from platform-specific response
        const candidates = this.extractCandidates(result.platform, result.result);
        
        if (candidates.length > 0) {
          // Publish CANDIDATE_FOUND event
          await this.publishCandidateFound({
            pipeline_id: request.payload.pipeline_id,
            platform: result.platform,
            candidates,
          }, request.correlation_id);

          totalCandidates += candidates.length;
          platformsScanned.push(result.platform);
        }
      }

      // Publish SCAN_COMPLETED event
      await this.publishScanCompleted({
        pipeline_id: request.payload.pipeline_id,
        total_candidates: totalCandidates,
        platforms_scanned: platformsScanned,
        scan_duration_ms: Date.now() - startTime,
      }, request.correlation_id);

      console.log(`✅ Scan completed: ${totalCandidates} candidates from ${platformsScanned.length} platforms`);
    } catch (error) {
      console.error('❌ Scan request failed:', error);
      await this.publishError(error as Error, JSON.stringify(request));
    }
  }

  /**
   * Extract candidates from platform-specific response
   */
  private extractCandidates(platform: string, response: any): Array<any> {
    try {
      switch (platform) {
        case 'linkedin':
          return response.profiles?.map((p: any) => ({
            id: p.profileUrl,
            name: p.fullName,
            profile_url: p.profileUrl,
            headline: p.headline,
            location: p.location,
            skills: p.skills || [],
            experience: p.experience?.[0]?.company || '',
            current_position: p.currentPosition,
          })) || [];

        case 'github':
          return response.developers?.map((d: any) => ({
            id: d.username,
            name: d.name || d.username,
            profile_url: d.profileUrl,
            bio: d.bio,
            location: d.location,
            skills: d.languages || [],
            repositories: d.topRepositories?.length || 0,
            contributions: d.contributions,
          })) || [];

        case 'stackoverflow':
          return response.users?.map((u: any) => ({
            id: u.userId.toString(),
            name: u.displayName,
            profile_url: u.profileUrl,
            location: u.location,
            skills: u.topTags?.map((t: any) => t.tagName) || [],
            reputation: u.reputation,
            badges: u.badgeCounts,
          })) || [];

        default:
          console.warn(`Unknown platform: ${platform}`);
          return [];
      }
    } catch (error) {
      console.error(`Error extracting candidates from ${platform}:`, error);
      return [];
    }
  }

  /**
   * Publish CANDIDATE_FOUND event
   */
  private async publishCandidateFound(
    payload: CandidateFoundEvent['payload'],
    correlationId: string
  ): Promise<void> {
    const event: CandidateFoundEvent = {
      source_agent: 'GenKit AI',
      message_type: 'CANDIDATE_FOUND',
      payload,
      correlation_id: correlationId,
      timestamp: new Date().toISOString(),
    };

    await this.publisher.publish(TOPICS.CANDIDATES, JSON.stringify(event));
    console.log(`📤 Published CANDIDATE_FOUND: ${payload.candidates.length} candidates from ${payload.platform}`);
  }

  /**
   * Publish SCAN_COMPLETED event
   */
  private async publishScanCompleted(
    payload: ScanCompletedEvent['payload'],
    correlationId: string
  ): Promise<void> {
    const event: ScanCompletedEvent = {
      source_agent: 'GenKit AI',
      message_type: 'SCAN_COMPLETED',
      payload,
      correlation_id: correlationId,
      timestamp: new Date().toISOString(),
    };

    await this.publisher.publish(TOPICS.PIPELINE, JSON.stringify(event));
    console.log(`📤 Published SCAN_COMPLETED: ${payload.total_candidates} total candidates in ${payload.scan_duration_ms}ms`);
  }

  /**
   * Publish error event
   */
  private async publishError(error: Error, context: string): Promise<void> {
    const errorEvent = {
      source_agent: 'GenKit AI',
      message_type: 'ERROR',
      payload: {
        error: error.message,
        stack: error.stack,
        context,
      },
      correlation_id: '',
      timestamp: new Date().toISOString(),
    };

    await this.publisher.publish(TOPICS.ERRORS, JSON.stringify(errorEvent));
    console.log('📤 Published ERROR event');
  }

  /**
   * Graceful shutdown
   */
  async shutdown(): Promise<void> {
    console.log('🛑 Shutting down Redis integration...');
    await this.subscriber.quit();
    await this.publisher.quit();
    console.log('✅ Redis integration shutdown complete');
  }

  /**
   * Health check
   */
  isHealthy(): boolean {
    return this.isConnected;
  }
}

// Export singleton instance
export const redisIntegration = new RedisIntegration();
