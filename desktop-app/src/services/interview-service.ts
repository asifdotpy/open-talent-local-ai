import axios from 'axios';
import { DEFAULT_MODEL, getModelConfig } from './model-config';

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface InterviewConfig {
  role: string;
  model: string;
  totalQuestions: number;
}

export interface InterviewSession {
  config: InterviewConfig;
  messages: Message[];
  currentQuestion: number;
  isComplete: boolean;
}

export class InterviewService {
  private baseURL: string;
  private client: any;

  constructor(baseURL = 'http://localhost:11434') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 60000, // Increased timeout for slower models
    });
  }

  /**
   * Check if Ollama server is running
   */
  async checkStatus(): Promise<boolean> {
    try {
      const response = await this.client.get('/api/tags');
      return response.status === 200;
    } catch (error) {
      console.error('Ollama status check failed:', error);
      return false;
    }
  }

  /**
   * List all available models
   */
  async listModels(): Promise<any[]> {
    try {
      const response = await this.client.get('/api/tags');
      return response.data.models || [];
    } catch (error) {
      console.error('Failed to list models:', error);
      return [];
    }
  }

  /**
   * Get interview system prompt based on role
   */
  private getInterviewPrompt(role: string, totalQuestions: number = 5): string {
    const prompts: Record<string, string> = {
      'Software Engineer': `You are an experienced technical interviewer conducting a job interview for a Junior Software Engineer position. 

Your interview will consist of exactly ${totalQuestions} questions covering:
1. Data structures and algorithms knowledge
2. A coding problem-solving scenario
3. Debugging approach and methodology
4. Team collaboration and communication
5. Learning mindset and continuous improvement

Guidelines:
- Ask ONE question at a time and wait for the candidate's response
- Keep questions clear, concise, and practical
- Be professional but friendly
- After the candidate answers, give a brief acknowledgment (1-2 sentences max)
- Then ask the next question
- Number your questions (e.g., "Question 1:", "Question 2:")
- After ${totalQuestions} questions, thank the candidate and provide a brief summary

Start by introducing yourself briefly and asking Question 1.`,

      'Product Manager': `You are an experienced interviewer conducting a job interview for a Product Manager position.

Your interview will consist of exactly ${totalQuestions} questions covering:
1. Product strategy and vision
2. Stakeholder management experience
3. Data-driven decision making
4. Conflict resolution skills
5. Innovation and creativity examples

Guidelines:
- Ask ONE question at a time and wait for the candidate's response
- Keep questions clear, concise, and scenario-based
- Be professional but friendly
- After the candidate answers, give a brief acknowledgment (1-2 sentences max)
- Then ask the next question
- Number your questions (e.g., "Question 1:", "Question 2:")
- After ${totalQuestions} questions, thank the candidate and provide a brief summary

Start by introducing yourself briefly and asking Question 1.`,

      'Data Analyst': `You are an experienced interviewer conducting a job interview for a Data Analyst position.

Your interview will consist of exactly ${totalQuestions} questions covering:
1. SQL and database knowledge
2. Data visualization and reporting
3. Statistical analysis approach
4. Business problem-solving with data
5. Communication of insights to non-technical stakeholders

Guidelines:
- Ask ONE question at a time and wait for the candidate's response
- Keep questions clear, concise, and practical
- Be professional but friendly
- After the candidate answers, give a brief acknowledgment (1-2 sentences max)
- Then ask the next question
- Number your questions (e.g., "Question 1:", "Question 2:")
- After ${totalQuestions} questions, thank the candidate and provide a brief summary

Start by introducing yourself briefly and asking Question 1.`,
    };

    return prompts[role] || prompts['Software Engineer'];
  }

  /**
   * Start a new interview session
   */
  async startInterview(
    role: string = 'Software Engineer',
    model: string = DEFAULT_MODEL,
    totalQuestions: number = 5
  ): Promise<InterviewSession> {
    const systemPrompt = this.getInterviewPrompt(role, totalQuestions);

    try {
      const response = await this.client.post('/api/chat', {
        model: model,
        messages: [
          {
            role: 'system',
            content: systemPrompt,
          },
          {
            role: 'user',
            content: 'Please start the interview.',
          },
        ],
        stream: false,
      });

      const assistantMessage = response.data.message.content;

      return {
        config: { role, model, totalQuestions },
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: 'Please start the interview.' },
          { role: 'assistant', content: assistantMessage },
        ],
        currentQuestion: 1,
        isComplete: false,
      };
    } catch (error: any) {
      throw new Error(`Failed to start interview: ${error.message}`);
    }
  }

  /**
   * Send a response and get the next question
   */
  async sendResponse(
    session: InterviewSession,
    userResponse: string
  ): Promise<InterviewSession> {
    const newMessages: Message[] = [
      ...session.messages,
      { role: 'user', content: userResponse },
    ];

    try {
      const response = await this.client.post('/api/chat', {
        model: session.config.model,
        messages: newMessages,
        stream: false,
      });

      const assistantMessage = response.data.message.content;

      // Detect if interview is complete
      const isComplete =
        session.currentQuestion >= session.config.totalQuestions ||
        assistantMessage.toLowerCase().includes('thank you') ||
        assistantMessage.toLowerCase().includes('end of interview') ||
        assistantMessage.toLowerCase().includes('conclud');

      return {
        ...session,
        messages: [
          ...newMessages,
          { role: 'assistant', content: assistantMessage },
        ],
        currentQuestion: isComplete
          ? session.currentQuestion
          : session.currentQuestion + 1,
        isComplete,
      };
    } catch (error: any) {
      throw new Error(`Failed to send response: ${error.message}`);
    }
  }

  /**
   * Get interview summary/assessment (basic version)
   */
  getInterviewSummary(session: InterviewSession): string {
    const totalResponses = session.messages.filter(
      (m) => m.role === 'user' && m.content !== 'Please start the interview.'
    ).length;

    return `Interview Complete!

Role: ${session.config.role}
Questions Asked: ${session.currentQuestion}
Responses Given: ${totalResponses}
Model Used: ${session.config.model}

Thank you for participating in this interview. Your responses have been recorded.`;
  }
}

export default InterviewService;
