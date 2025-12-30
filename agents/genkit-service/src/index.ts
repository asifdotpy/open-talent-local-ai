import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';
import { startFlowServer } from '@genkit-ai/express';
import { z } from 'zod';
import { platformRegistry, PlatformScanRequestSchema } from './flows/platforms/registry';

// Configure Genkit with Google AI
const ai = genkit({
  plugins: [
    googleAI({
      apiKey: process.env.GOOGLE_GENAI_API_KEY,
    }),
  ],
});

// Define input/output schemas using Zod
const JobDescriptionSchema = z.object({
  description: z.string(),
  numQuestions: z.number().default(5),
});

const BooleanQuerySchema = z.object({
  searchTerms: z.string(),
  platform: z.string().default('linkedin'),
});

const EngagementContextSchema = z.object({
  candidateName: z.string(),
  candidateProfile: z.string(),
  jobDescription: z.string(),
});

const CandidateProfileSchema = z.object({
  name: z.string(),
  skills: z.array(z.string()),
  experience: z.string(),
  jobRequirements: z.object({}).optional(),
  interviewHistory: z.array(z.object({})).optional(),
});

const InterviewQuestionSchema = z.object({
  question: z.string(),
  type: z.string(), // technical, behavioral, situational
  context: z.string(),
});

const ResponseEvaluationSchema = z.object({
  score: z.number(),
  feedback: z.string(),
  strengths: z.array(z.string()),
  weaknesses: z.array(z.string()),
  recommendations: z.array(z.string()),
});

const InterviewAssessmentSchema = z.object({
  overallScore: z.number(),
  summary: z.string(),
  detailedFeedback: z.string(),
  hireRecommendation: z.string(),
});

// Flow 1: Generate Interview Questions
export const generateInterviewQuestions = ai.defineFlow(
  {
    name: 'generateInterviewQuestions',
    inputSchema: JobDescriptionSchema,
    outputSchema: z.object({
      questions: z.array(z.string()),
    }),
  },
  async (input) => {
    // Use Gemini to generate contextual interview questions
    const prompt = `Generate ${input.numQuestions} interview questions for a candidate applying for a role with this description: ${input.description}

Please provide questions that assess:
- Technical skills and experience
- Problem-solving abilities
- Communication and collaboration
- Cultural fit and motivation

Format as a JSON array of strings.`;

    const response = await ai.generate({
      model: 'gemini-1.5-flash',
      prompt: prompt,
      config: {
        temperature: 0.7,
        maxOutputTokens: 1000,
      },
    });

    // Parse the response to extract questions
    const text = response.text;
    try {
      const parsed = JSON.parse(text);
      return { questions: parsed };
    } catch (e) {
      // Fallback: extract questions from text
      const lines = text.split('\n').filter(line => line.trim().length > 10);
      return { questions: lines.slice(0, input.numQuestions || 5) };
    }
  }
);

// Flow 2: Generate Boolean Search Query
export const generateBooleanQuery = ai.defineFlow(
  {
    name: 'generateBooleanQuery',
    inputSchema: BooleanQuerySchema,
    outputSchema: z.object({
      query: z.string(),
      explanation: z.string(),
    }),
  },
  async (input) => {
    const prompt = `Generate an optimized boolean search query for ${input.platform} to find candidates with skills in: ${input.searchTerms}

Consider:
- Platform-specific syntax and operators
- Inclusion of relevant keywords and exclusion of irrelevant terms
- Focus on experienced professionals
- Use of quotes, parentheses, and boolean operators (AND, OR, NOT)

Provide the query and a brief explanation of the strategy.`;

    const response = await ai.generate({
      model: 'googleai/gemini-1.5-flash',
      prompt: prompt,
      config: {
        temperature: 0.3,
        maxOutputTokens: 500,
      },
    });

    const text = response.text;
    // Parse or extract query and explanation
    const lines = text.split('\n');
    const query = lines[0] || text;
    const explanation = lines.slice(1).join(' ') || 'Optimized boolean query';

    return { query, explanation };
  }
);

// Flow 3: Generate Personalized Engagement Message
export const generateEngagementMessage = ai.defineFlow(
  {
    name: 'generateEngagementMessage',
    inputSchema: EngagementContextSchema,
    outputSchema: z.object({
      subject: z.string(),
      message: z.string(),
    }),
  },
  async (input) => {
    const prompt = `Generate a personalized outreach message for a candidate.

Candidate Name: ${input.candidateName}
Candidate Profile Summary: ${input.candidateProfile}
Job Description: ${input.jobDescription}

Create:
1. An engaging email subject line
2. A personalized message that:
   - References something specific from their profile
   - Explains why this role might interest them
   - Includes a clear call-to-action
   - Maintains a professional yet friendly tone
   - Is concise (under 200 words)

Format as JSON with "subject" and "message" fields.`;

    const response = await ai.generate({
      model: 'googleai/gemini-1.5-flash',
      prompt: prompt,
      config: {
        temperature: 0.8,
        maxOutputTokens: 800,
      },
    });

    const text = response.text;
    try {
      const parsed = JSON.parse(text);
      return parsed;
    } catch (e) {
      // Fallback parsing
      const lines = text.split('\n');
      const subject = lines[0] || 'Exciting opportunity for you';
      const message = lines.slice(1).join('\n') || 'We have an opportunity that matches your profile.';
      return { subject, message };
    }
  }
);

// Flow 4: Score Candidate Quality
export const scoreCandidateQuality = ai.defineFlow(
  {
    name: 'scoreCandidateQuality',
    inputSchema: CandidateProfileSchema,
    outputSchema: z.object({
      score: z.number(),
      reasoning: z.string(),
      qualityLevel: z.string(),
    }),
  },
  async (input) => {
    const prompt = `Evaluate the quality of this candidate profile for technical roles:

Name: ${input.name}
Skills: ${input.skills.join(', ')}
Experience: ${input.experience}

Provide a quality score from 0-100 based on:
- Relevance and number of technical skills
- Depth of experience described
- Overall profile completeness

Also provide reasoning and categorize as 'low', 'medium', or 'high' quality.

Format as JSON with score, reasoning, and qualityLevel fields.`;

    const response = await ai.generate({
      model: 'googleai/gemini-1.5-flash',
      prompt: prompt,
      config: {
        temperature: 0.2,
        maxOutputTokens: 300,
      },
    });

    const text = response.text;
    try {
      const parsed = JSON.parse(text);
      return parsed;
    } catch (e) {
      // Fallback
      const score = Math.min(100, input.skills.length * 10 + (input.experience.length > 200 ? 40 : 20));
      const qualityLevel = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low';
      const reasoning = `Based on ${input.skills.length} skills and experience description length.`;
      return { score, reasoning, qualityLevel };
    }
  }
);

// Flow 5: Generate Single Interview Question
export const generateInterviewQuestion = ai.defineFlow(
  {
    name: 'generateInterviewQuestion',
    inputSchema: z.object({
      candidateProfile: CandidateProfileSchema,
      questionIndex: z.number(),
      previousQuestions: z.array(z.string()).optional(),
    }),
    outputSchema: InterviewQuestionSchema,
  },
  async (input) => {
    const { candidateProfile, questionIndex, previousQuestions = [] } = input;

    const questionType = questionIndex < 3 ? 'technical' :
                        questionIndex < 6 ? 'behavioral' : 'situational';

    const prompt = `Generate a ${questionType} interview question for this candidate:

Candidate: ${candidateProfile.name}
Skills: ${candidateProfile.skills.join(', ')}
Experience: ${candidateProfile.experience}
Job Requirements: ${JSON.stringify(candidateProfile.jobRequirements || {})}

Previous questions asked: ${previousQuestions.join('; ')}

Create a question that:
- Is relevant to their background
- Tests ${questionType} abilities
- Hasn't been asked before
- Is open-ended and insightful

Provide the question, its type, and brief context.`;

    const response = await ai.generate({
      model: 'googleai/gemini-1.5-flash',
      prompt: prompt,
      config: {
        temperature: 0.7,
        maxOutputTokens: 200,
      },
    });

    const text = response.text;
    try {
      const parsed = JSON.parse(text);
      return parsed;
    } catch (e) {
      // Fallback
      const question = `Can you tell me about your experience with ${candidateProfile.skills[0] || 'relevant technologies'}?`;
      return {
        question,
        type: questionType,
        context: 'General experience assessment'
      };
    }
  }
);

// Flow 6: Evaluate Interview Response
export const evaluateInterviewResponse = ai.defineFlow(
  {
    name: 'evaluateInterviewResponse',
    inputSchema: z.object({
      question: z.string(),
      response: z.string(),
      candidateProfile: CandidateProfileSchema,
      interviewHistory: z.array(z.object({
        question: z.string(),
        response: z.string(),
        evaluation: z.object({}).optional(),
      })).optional(),
    }),
    outputSchema: ResponseEvaluationSchema,
  },
  async (input) => {
    const { question, response, candidateProfile, interviewHistory = [] } = input;

    const prompt = `Evaluate this interview response:

Question: ${question}
Response: ${response}

Candidate Profile:
- Name: ${candidateProfile.name}
- Skills: ${candidateProfile.skills.join(', ')}
- Experience: ${candidateProfile.experience}

Previous responses: ${interviewHistory.slice(-2).map(h => `Q: ${h.question} A: ${h.response}`).join('; ')}

Provide a score (1-10), feedback, strengths, weaknesses, and recommendations.
Be constructive and specific.`;

    const response_eval = await ai.generate({
      model: 'googleai/gemini-1.5-flash',
      prompt: prompt,
      config: {
        temperature: 0.4,
        maxOutputTokens: 600,
      },
    });

    const text = response_eval.text;
    try {
      const parsed = JSON.parse(text);
      return parsed;
    } catch (e) {
      // Fallback evaluation
      const score = response.length > 50 ? 7.0 : 5.0;
      return {
        score,
        feedback: 'Response recorded and evaluated',
        strengths: ['Clear communication'],
        weaknesses: [],
        recommendations: ['Provide more specific examples']
      };
    }
  }
);

// Flow 7: Generate Final Interview Assessment
export const generateFinalAssessment = ai.defineFlow(
  {
    name: 'generateFinalAssessment',
    inputSchema: z.object({
      candidateProfile: CandidateProfileSchema,
      interviewSummary: z.object({
        totalQuestions: z.number(),
        responses: z.array(z.object({
          question: z.string(),
          response: z.string(),
          evaluation: ResponseEvaluationSchema,
        })),
        averageScore: z.number(),
      }),
    }),
    outputSchema: InterviewAssessmentSchema,
  },
  async (input) => {
    const { candidateProfile, interviewSummary } = input;

    const prompt = `Generate a comprehensive final assessment for this candidate's interview:

Candidate: ${candidateProfile.name}
Skills: ${candidateProfile.skills.join(', ')}
Experience: ${candidateProfile.experience}

Interview Summary:
- Questions Asked: ${interviewSummary.totalQuestions}
- Average Score: ${interviewSummary.averageScore}/10
- Response Details: ${interviewSummary.responses.map(r =>
    `Q: ${r.question}\nA: ${r.response}\nScore: ${r.evaluation.score}`
  ).join('\n\n')}

Provide:
- Overall score (1-10)
- Executive summary
- Detailed feedback
- Hire recommendation (Strong Hire, Hire, Consider, No Hire)

Be thorough and balanced.`;

    const response = await ai.generate({
      model: 'googleai/gemini-1.5-flash',
      prompt: prompt,
      config: {
        temperature: 0.3,
        maxOutputTokens: 1000,
      },
    });

    const text = response.text;
    try {
      const parsed = JSON.parse(text);
      return parsed;
    } catch (e) {
      // Fallback
      const score = interviewSummary.averageScore;
      const recommendation = score >= 8 ? 'Strong Hire' :
                           score >= 6 ? 'Hire' :
                           score >= 4 ? 'Consider' : 'No Hire';
      return {
        overallScore: score,
        summary: `Candidate scored ${score}/10 overall`,
        detailedFeedback: 'Interview completed successfully',
        hireRecommendation: recommendation
      };
    }
  }
);

export const flows = {
  generateInterviewQuestions,
  generateBooleanQuery,
  generateEngagementMessage,
  scoreCandidateQuality,
  generateInterviewQuestion,
  evaluateInterviewResponse,
  generateFinalAssessment,
};

// Start the flow server and Redis integration only if not in a test environment
if (process.env.NODE_ENV !== 'test') {
  // Import and initialize Redis integration
  import('./redis-integration').then(({ redisIntegration }) => {
    // Initialize Redis subscriber
    redisIntegration.initialize().catch((err) => {
      console.error('Failed to initialize Redis integration:', err);
      console.warn('⚠️  GenKit service running without Redis integration');
    });

    // Graceful shutdown handler
    const shutdown = async () => {
      console.log('\n🛑 Shutting down GenKit service...');
      await redisIntegration.shutdown();
      process.exit(0);
    };

    process.on('SIGTERM', shutdown);
    process.on('SIGINT', shutdown);

    console.log('🚀 Redis integration initialized');
  });

  // Start the flow server
  startFlowServer({
    flows: [
      generateInterviewQuestions,
      generateBooleanQuery,
      generateEngagementMessage,
      scoreCandidateQuality,
      generateInterviewQuestion,
      evaluateInterviewResponse,
      generateFinalAssessment,
    ],
    port: 3400,
  });

  console.log('🎯 GenKit flow server started on port 3400');
}
