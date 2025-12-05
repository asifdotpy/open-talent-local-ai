import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';
import { flows } from '../index';
import { platformRegistry } from '../flows/platforms/registry';
import * as linkedin from '../flows/platforms/linkedin';
import * as github from '../flows/platforms/github';
import * as stackoverflow from '../flows/platforms/stackoverflow';

// Mock Genkit configuration
genkit({
  plugins: [
    googleAI({
      apiKey: 'test-api-key', // Use a dummy API key for tests
    }),
  ],
});

describe('Genkit AI Flows', () => {
  // Test for generateBooleanQuery flow
  it('should define generateBooleanQuery flow', () => {
    expect(flows.generateBooleanQuery).toBeDefined();
    expect(typeof flows.generateBooleanQuery).toBe('function');
  });

  // Test for generateEngagementMessage flow
  it('should define generateEngagementMessage flow', () => {
    expect(flows.generateEngagementMessage).toBeDefined();
    expect(typeof flows.generateEngagementMessage).toBe('function');
  });

  // Test for scoreCandidateQuality flow
  it('should define scoreCandidateQuality flow', () => {
    expect(flows.scoreCandidateQuality).toBeDefined();
    expect(typeof flows.scoreCandidateQuality).toBe('function');
  });

  // Test for generateInterviewQuestions flow
  it('should define generateInterviewQuestions flow', () => {
    expect(flows.generateInterviewQuestions).toBeDefined();
    expect(typeof flows.generateInterviewQuestions).toBe('function');
  });

  // Test for generateInterviewQuestion flow
  it('should define generateInterviewQuestion flow', () => {
    expect(flows.generateInterviewQuestion).toBeDefined();
    expect(typeof flows.generateInterviewQuestion).toBe('function');
  });

  // Test for evaluateInterviewResponse flow
  it('should define evaluateInterviewResponse flow', () => {
    expect(flows.evaluateInterviewResponse).toBeDefined();
    expect(typeof flows.evaluateInterviewResponse).toBe('function');
  });

  // Test for generateFinalAssessment flow
  it('should define generateFinalAssessment flow', () => {
    expect(flows.generateFinalAssessment).toBeDefined();
    expect(typeof flows.generateFinalAssessment).toBe('function');
  });
});

describe('PlatformRegistry', () => {
  beforeEach(() => {
    // Clear and re-register platforms for each test to ensure isolation
    // @ts-ignore
    platformRegistry.platforms = new Map();
    platformRegistry.register('linkedin', {
      scan: linkedin.scanLinkedIn,
      metadata: linkedin.platformMetadata,
      requestSchema: linkedin.LinkedInScanRequestSchema,
      responseSchema: linkedin.LinkedInScanResponseSchema,
    });
    platformRegistry.register('github', {
      scan: github.scanGitHub,
      metadata: github.platformMetadata,
      requestSchema: github.GitHubScanRequestSchema,
      responseSchema: github.GitHubScanResponseSchema,
    });
    platformRegistry.register('stackoverflow', {
      scan: stackoverflow.scanStackOverflow,
      metadata: stackoverflow.platformMetadata,
      requestSchema: stackoverflow.StackOverflowScanRequestSchema,
      responseSchema: stackoverflow.StackOverflowScanResponseSchema,
    });
  });

  it('should register default platforms', () => {
    expect(platformRegistry.listPlatforms()).toEqual(['linkedin', 'github', 'stackoverflow']);
  });

  it('should successfully scan multiple platforms', async () => {
    const requests = [
      { platform: 'linkedin', request: { searchQuery: 'engineer', maxResults: 1 } },
      { platform: 'github', request: { searchQuery: 'python', maxResults: 1 } },
    ];

    const results = await platformRegistry.scanMultiple(requests);

    expect(results.length).toBe(2);
    expect(results[0].platform).toBe('linkedin');
    expect(results[0].result).toBeDefined();
    expect(results[0].error).toBeUndefined();
    expect(results[1].platform).toBe('github');
    expect(results[1].result).toBeDefined();
    expect(results[1].error).toBeUndefined();
  });

  it('should handle partial failures when scanning multiple platforms', async () => {
    // Mock one platform to throw an error
    const mockErrorScan = jest.fn().mockImplementation(() => {
      throw new Error('Mock scan error');
    });
    platformRegistry.register('failing_platform', {
      scan: mockErrorScan,
      metadata: { name: 'Failing', type: 'test', capabilities: [], rateLimit: {}, authentication: { required: false, type: 'none' } },
      requestSchema: linkedin.LinkedInScanRequestSchema, // Use any valid schema for mock
      responseSchema: linkedin.LinkedInScanResponseSchema, // Use any valid schema for mock
    });

    const requests = [
      { platform: 'linkedin', request: { searchQuery: 'engineer', maxResults: 1 } },
      { platform: 'failing_platform', request: { searchQuery: 'error' } },
    ];

    const results = await platformRegistry.scanMultiple(requests);

    expect(results.length).toBe(2);
    expect(results[0].platform).toBe('linkedin');
    expect(results[0].result).toBeDefined();
    expect(results[0].error).toBeUndefined();
    expect(results[1].platform).toBe('failing_platform');
    expect(results[1].result).toBeNull();
    expect(results[1].error).toBe('Mock scan error');
  });

  it('should return an error for an unregistered platform', async () => {
    const requests = [
      { platform: 'unregistered', request: { searchQuery: 'test' } },
    ];

    const results = await platformRegistry.scanMultiple(requests);

    expect(results.length).toBe(1);
    expect(results[0].platform).toBe('unregistered');
    expect(results[0].result).toBeNull();
    expect(results[0].error).toContain("Platform 'unregistered' is not registered.");
  });

  it('should validate request schema and fail for invalid request shape', async () => {
    // Missing required field 'searchQuery' for LinkedIn schema
    await expect(
      platformRegistry.scan('linkedin', { location: 'SF', maxResults: 1 })
    ).rejects.toThrow(/Invalid request for platform 'linkedin'/);
  });
});

// Placeholder for Redis integration tests
describe('Redis Integration (Placeholder)', () => {
  it('should have tests for Redis pub/sub integration', () => {
    // TODO: Implement actual tests for Redis subscription and publishing
    // This will involve mocking the Redis client and verifying method calls.
    expect(true).toBe(true); // Placeholder assertion
  });
});
