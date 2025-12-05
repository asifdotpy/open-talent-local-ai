/**
 * Platform Flows Index
 * Exports all platform scanners and the registry.
 */

export { platformRegistry, PlatformRegistry } from './registry';

// Platform-specific exports
export {
  scanLinkedIn,
  LinkedInScanRequestSchema,
  LinkedInProfileSchema,
  LinkedInScanResponseSchema,
} from './linkedin';

export {
  scanGitHub,
  GitHubScanRequestSchema,
  GitHubProfileSchema,
  GitHubScanResponseSchema,
} from './github';

export {
  scanStackOverflow,
  StackOverflowScanRequestSchema,
  StackOverflowProfileSchema,
  StackOverflowScanResponseSchema,
} from './stackoverflow';
