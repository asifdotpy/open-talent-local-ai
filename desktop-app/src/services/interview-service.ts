import { DEFAULT_MODEL, getModelConfig } from './model-config';
import { ErrorHandler, HealthChecker } from '../utils/error-handler';
import { InputValidator } from '../utils/validation';
import { AIProvider, AIMessage } from '../providers/ai/ai-provider.interface';

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
  private aiProvider: AIProvider;
  private isHealthy = false;

  constructor(provider: AIProvider) {
    this.aiProvider = provider;

    HealthChecker.startHealthChecks(
      () => this.checkStatus(),
      (healthy) => {
        this.isHealthy = healthy;
      }
    );
  }

  /**
   * Check if Ollama server is running with retry logic
   */
  async checkStatus(): Promise<boolean> {
    try {
      await ErrorHandler.retryWithBackoff(() => this.aiProvider.checkHealth(), 2, 500, 'Status check');
      this.isHealthy = true;
      return true;
    } catch (error) {
      this.isHealthy = false;
      console.warn('[InterviewService] Ollama status check failed:', error);
      return false;
    }
  }

  /**
   * List all available models with error handling
   */
  async listModels(): Promise<any[]> {
    try {
      const models = await ErrorHandler.retryWithBackoff(
        () => this.aiProvider.listModels(),
        3,
        1000,
        'List models'
      );
      return models.map((name) => ({ name }));
    } catch (error) {
      const appError = ErrorHandler.handleError(error, 'List models');
      console.error('[InterviewService] Failed to list models:', appError.getUserMessage());
      return [];
    }
  }

  /**
   * Get health status
   */
  isServiceHealthy(): boolean {
    return this.isHealthy;
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

Guidelines (MANDATORY):
- Introduce yourself as "OpenTalent Interviewer" (no placeholders or brackets)
- Ask ONE question at a time and wait for the candidate's response
- Keep questions clear, concise, and practical
- Be professional but friendly
- After the candidate answers, give a brief acknowledgment (1-2 sentences max)
- Then ask the next question
- Number your questions (e.g., "Question 1:", "Question 2:")
- After ${totalQuestions} questions, thank the candidate and provide a brief summary
- NEVER use placeholder tokens like [Your Name] or [Greeting]; do not invent candidate background

Start by saying: "Hello, I'm OpenTalent Interviewer. Question 1:" and then ask the first question.`,

      'Product Manager': `You are an experienced interviewer conducting a job interview for a Product Manager position.

Your interview will consist of exactly ${totalQuestions} questions covering:
1. Product strategy and vision
2. Stakeholder management experience
3. Data-driven decision making
4. Conflict resolution skills
5. Innovation and creativity examples

Guidelines (MANDATORY):
- Introduce yourself as "OpenTalent Interviewer" (no placeholders or brackets)
- Ask ONE question at a time and wait for the candidate's response
- Keep questions clear, concise, and scenario-based
- Be professional but friendly
- After the candidate answers, give a brief acknowledgment (1-2 sentences max)
- Then ask the next question
- Number your questions (e.g., "Question 1:", "Question 2:")
- After ${totalQuestions} questions, thank the candidate and provide a brief summary
- NEVER use placeholder tokens like [Your Name] or [Greeting]; do not invent candidate background

Start by saying: "Hello, I'm OpenTalent Interviewer. Question 1:" and then ask the first question.`,

      'Data Analyst': `You are an experienced interviewer conducting a job interview for a Data Analyst position.

Your interview will consist of exactly ${totalQuestions} questions covering:
1. SQL and database knowledge
2. Data visualization and reporting
3. Statistical analysis approach
4. Business problem-solving with data
5. Communication of insights to non-technical stakeholders

Guidelines (MANDATORY):
- Introduce yourself as "OpenTalent Interviewer" (no placeholders or brackets)
- Ask ONE question at a time and wait for the candidate's response
- Keep questions clear, concise, and practical
- Be professional but friendly
- After the candidate answers, give a brief acknowledgment (1-2 sentences max)
- Then ask the next question
- Number your questions (e.g., "Question 1:", "Question 2:")
- After ${totalQuestions} questions, thank the candidate and provide a brief summary
- NEVER use placeholder tokens like [Your Name] or [Greeting]; do not invent candidate background

Start by saying: "Hello, I'm OpenTalent Interviewer. Question 1:" and then ask the first question.`,
    };

    return prompts[role] || prompts['Software Engineer'];
  }

  /**
   * Start a new interview session with comprehensive error handling
   */
  async startInterview(
    role: string = 'Software Engineer',
    model: string = DEFAULT_MODEL,
    totalQuestions: number = 5
  ): Promise<InterviewSession> {
    // Validate inputs
    const roleValidation = InputValidator.validateRole(role);
    if (!roleValidation.valid) {
      throw ErrorHandler.handleError(
        new Error(roleValidation.error),
        'Start interview - role validation'
      );
    }

    const questionsValidation = InputValidator.validateTotalQuestions(totalQuestions);
    if (!questionsValidation.valid) {
      throw ErrorHandler.handleError(
        new Error(questionsValidation.error),
        'Start interview - questions validation'
      );
    }

    // Check Ollama health
    if (!this.isHealthy) {
      throw ErrorHandler.handleError(
        new Error('Ollama service is not running'),
        'Start interview - health check'
      );
    }

    const systemPrompt = this.getInterviewPrompt(role, totalQuestions);

    try {
      const response = await ErrorHandler.retryWithBackoff(
        () =>
          this.aiProvider.chat(
            [
              { role: 'system', content: systemPrompt },
              { role: 'user', content: 'Please start the interview.' },
            ] as AIMessage[],
            model
          ),
        3,
        2000,
        'Start interview'
      );

      if (!response?.message?.content) {
        throw new Error('Invalid response from server');
      }

      const assistantMessage = response.message.content;

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
      const appError = ErrorHandler.handleError(error, 'Start interview');
      ErrorHandler.logError(appError);
      throw appError;
    }
  }

  /**
   * Send a response and get the next question with error handling
   */
  async sendResponse(
    session: InterviewSession,
    userResponse: string
  ): Promise<InterviewSession> {
    // Validate response
    const validation = InputValidator.validateInterviewResponse(userResponse);
    if (!validation.valid) {
      throw ErrorHandler.handleError(
        new Error(validation.error),
        'Send response - validation'
      );
    }

    // Check Ollama health
    if (!this.isHealthy) {
      throw ErrorHandler.handleError(
        new Error('Ollama service is not running'),
        'Send response - health check'
      );
    }

    const newMessages: Message[] = [
      ...session.messages,
      { role: 'user', content: userResponse },
    ];

    try {
      const response = await ErrorHandler.retryWithBackoff(
        () => this.aiProvider.chat(newMessages as AIMessage[], session.config.model),
        3,
        2000,
        'Send response'
      );

      if (!response?.message?.content) {
        throw new Error('Invalid response from server');
      }

      const assistantMessage = response.message.content;

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
      const appError = ErrorHandler.handleError(error, 'Send response');
      ErrorHandler.logError(appError);
      throw appError;
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
