import { z } from 'zod';
import axios from 'axios'; // Added axios import

// GitHub scan request schema
export const GitHubScanRequestSchema = z.object({
  searchQuery: z.string().describe('GitHub search query (repos, users, code)'),
  language: z.string().optional().describe('Programming language filter'),
  minStars: z.number().optional().describe('Minimum repository stars'),
  minFollowers: z.number().optional().describe('Minimum user followers'),
  location: z.string().optional().describe('Location filter'),
  maxResults: z.number().default(50).describe('Maximum number of developers to find'),
});

// GitHub developer profile schema
export const GitHubProfileSchema = z.object({
  username: z.string(),
  profileUrl: z.string(),
  name: z.string().optional(),
  bio: z.string().optional(),
  location: z.string().optional(),
  email: z.string().optional(),
  company: z.string().optional(),
  followers: z.number(),
  following: z.number(),
  publicRepos: z.number(),
  topRepositories: z.array(z.object({
    name: z.string(),
    description: z.string().optional(),
    language: z.string().optional(),
    stars: z.number(),
    forks: z.number(),
    url: z.string(),
  })),
  languages: z.array(z.string()),
  contributions: z.object({
    lastYear: z.number(),
    longestStreak: z.number(),
  }).optional(),
  scannedAt: z.string(),
});

// GitHub scan response schema
export const GitHubScanResponseSchema = z.object({
  platform: z.literal('github'),
  searchQuery: z.string(),
  totalResults: z.number(),
  developers: z.array(GitHubProfileSchema),
  scanDuration: z.number().describe('Scan duration in milliseconds'),
  error: z.string().optional(),
});

async function enrichViaGitHub(url: string): Promise<z.infer<typeof GitHubProfileSchema>> {
  if (!url.includes('github.com')) {
    throw new Error('Not a GitHub URL');
  }

  const username = url.split('/').pop();
  const response = await axios.get(`https://api.github.com/users/${username}`);

  if (response.status !== 200) {
    throw new Error(`GitHub API error: ${response.status}`);
  }

  const data = response.data;
  const profile: z.infer<typeof GitHubProfileSchema> = {
    username: data.login,
    profileUrl: data.html_url,
    name: data.name,
    bio: data.bio,
    location: data.location,
    email: data.email,
    company: data.company,
    followers: data.followers,
    following: data.following,
    publicRepos: data.public_repos,
    topRepositories: [], // This would require another API call
    languages: [], // This would require another API call
    contributions: {
      lastYear: 0, // This would require another API call
      longestStreak: 0, // This would require another API call
    },
    scannedAt: new Date().toISOString(),
  };

  return profile;
}

/**
 * GitHub scanning flow implementation.
 * Integrates with GitHub API to find developers.
 */
export async function scanGitHub(
  request: z.infer<typeof GitHubScanRequestSchema>
): Promise<z.infer<typeof GitHubScanResponseSchema>> {
  const startTime = Date.now();

  try {
    console.log(`Scanning GitHub with query: ${request.searchQuery}`);

    // For now, we'll just enrich a single profile from the search query if it's a URL
    // A real implementation would use the GitHub search API
    if (request.searchQuery.includes('github.com')) {
      const developer = await enrichViaGitHub(request.searchQuery);
      const scanDuration = Date.now() - startTime;
      return {
        platform: 'github',
        searchQuery: request.searchQuery,
        totalResults: 1,
        developers: [developer],
        scanDuration,
      };
    }

    // Fallback to empty array if no URL and no proper search implementation
    const scanDuration = Date.now() - startTime;
    return {
      platform: 'github',
      searchQuery: request.searchQuery,
      totalResults: 0,
      developers: [],
      scanDuration,
    };
  } catch (error) {
    const scanDuration = Date.now() - startTime;
    return {
      platform: 'github',
      searchQuery: request.searchQuery,
      totalResults: 0,
      developers: [],
      scanDuration,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

export const platformMetadata = {
  name: 'GitHub',
  type: 'developer_platform',
  capabilities: ['repo_search', 'code_analysis', 'contribution_tracking', 'language_proficiency'],
  rateLimit: {
    requestsPerMinute: 30,
    requestsPerHour: 5000,
  },
  authentication: {
    required: true,
    type: 'oauth_token',
  },
};
