import { z } from 'zod';
import axios from 'axios';

// Stack Overflow scan request schema
export const StackOverflowScanRequestSchema = z.object({
  tags: z.array(z.string()).describe('Technology tags to search for'),
  minReputation: z.number().default(1000).describe('Minimum reputation score'),
  location: z.string().optional().describe('Location filter'),
  maxResults: z.number().default(50).describe('Maximum number of users to find'),
});

// Stack Overflow user profile schema
export const StackOverflowProfileSchema = z.object({
  userId: z.number(),
  displayName: z.string(),
  profileUrl: z.string(),
  location: z.string().optional(),
  reputation: z.number(),
  badgeCounts: z.object({
    gold: z.number(),
    silver: z.number(),
    bronze: z.number(),
  }),
  topTags: z.array(z.object({
    tagName: z.string(),
    score: z.number(),
    postCount: z.number(),
  })),
  questionCount: z.number(),
  answerCount: z.number(),
  acceptRate: z.number().optional(),
  topPosts: z.array(z.object({
    title: z.string(),
    score: z.number(),
    url: z.string(),
    tags: z.array(z.string()),
  })).optional(),
  websiteUrl: z.string().optional(),
  githubProfile: z.string().optional(),
  scannedAt: z.string(),
});

// Stack Overflow scan response schema
export const StackOverflowScanResponseSchema = z.object({
  platform: z.literal('stackoverflow'),
  tags: z.array(z.string()),
  totalResults: z.number(),
  users: z.array(StackOverflowProfileSchema),
  scanDuration: z.number().describe('Scan duration in milliseconds'),
  error: z.string().optional(),
});

async function enrichViaStackOverflow(query: string): Promise<z.infer<typeof StackOverflowProfileSchema>> {
  const baseUrl = 'https://api.stackexchange.com/2.3';

  let userUrl: string;
  if (/^\d+$/.test(query)) {
    userUrl = `${baseUrl}/users/${query}?site=stackoverflow`;
  } else {
    const searchUrl = `${baseUrl}/users?order=desc&sort=reputation&inname=${query}&site=stackoverflow`;
    const searchResponse = await axios.get(searchUrl);
    if (searchResponse.status !== 200 || !searchResponse.data.items || searchResponse.data.items.length === 0) {
      throw new Error(`No Stack Overflow users found for: ${query}`);
    }
    const userId = searchResponse.data.items[0].user_id;
    userUrl = `${baseUrl}/users/${userId}?site=stackoverflow`;
  }

  const response = await axios.get(userUrl);

  if (response.status !== 200 || !response.data.items || response.data.items.length === 0) {
    throw new Error(`Stack Overflow API error: ${response.status}`);
  }

  const data = response.data.items[0];
  const profile: z.infer<typeof StackOverflowProfileSchema> = {
    userId: data.user_id,
    displayName: data.display_name,
    profileUrl: data.link,
    location: data.location,
    reputation: data.reputation,
    badgeCounts: data.badge_counts,
    topTags: [], // This would require another API call
    questionCount: data.question_count,
    answerCount: data.answer_count,
    acceptRate: data.accept_rate,
    topPosts: [], // This would require another API call
    websiteUrl: data.website_url,
    githubProfile: undefined, // Not available in this API response
    scannedAt: new Date().toISOString(),
  };

  return profile;
}

/**
 * Stack Overflow scanning flow implementation.
 * Integrates with Stack Overflow API to find experts.
 */
export async function scanStackOverflow(
  request: z.infer<typeof StackOverflowScanRequestSchema>
): Promise<z.infer<typeof StackOverflowScanResponseSchema>> {
  const startTime = Date.now();

  try {
    console.log(`Scanning Stack Overflow for tags: ${request.tags.join(', ')}`);

    // A real implementation would use the /users endpoint with the `tagged` parameter
    // For now, we'll just enrich a single user if a tag is provided as a search term
    const users = await Promise.all(request.tags.map(tag => enrichViaStackOverflow(tag)));

    const scanDuration = Date.now() - startTime;

    return {
      platform: 'stackoverflow',
      tags: request.tags,
      totalResults: users.length,
      users: users,
      scanDuration,
    };
  } catch (error) {
    const scanDuration = Date.now() - startTime;
    return {
      platform: 'stackoverflow',
      tags: request.tags,
      totalResults: 0,
      users: [],
      scanDuration,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

export const platformMetadata = {
  name: 'Stack Overflow',
  type: 'qa_platform',
  capabilities: ['expertise_verification', 'tag_analysis', 'reputation_scoring'],
  rateLimit: {
    requestsPerMinute: 30,
    requestsPerDay: 10000,
  },
  authentication: {
    required: false,
    type: 'api_key_optional',
  },
};
