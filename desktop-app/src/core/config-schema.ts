import { z } from 'zod';

export const AppConfigSchema = z.object({
  ai: z.object({
    provider: z.enum(['ollama', 'mock']),
    ollama: z.object({
      baseURL: z.string().url(),
      defaultModel: z.string(),
      timeout: z.number().positive(),
    }),
  }),
  storage: z.object({
    provider: z.enum(['sqlite', 'indexeddb']).default('sqlite'),
    path: z.string().optional(),
  }),
  voice: z.object({
    enabled: z.boolean().default(true),
    sampleRate: z.number().positive().default(16000),
  }),
  avatar: z.object({
    enabled: z.boolean().default(true),
    quality: z.enum(['low', 'medium', 'high']).default('medium'),
  }),
  interview: z.object({
    defaultRole: z.string().default('Software Engineer'),
    defaultQuestions: z.number().int().positive().default(5),
  }),
});

export type AppConfig = z.infer<typeof AppConfigSchema>;
