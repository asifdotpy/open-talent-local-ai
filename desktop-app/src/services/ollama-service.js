const axios = require('axios');

class OllamaService {
  constructor(baseURL = 'http://localhost:11434') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000
    });
  }

  /**
   * Check if Ollama server is running
   */
  async checkStatus() {
    try {
      const response = await this.client.get('/api/tags');
      return response.status === 200;
    } catch (error) {
      console.error('Ollama status check failed:', error.message);
      return false;
    }
  }

  /**
   * List all available models
   */
  async listModels() {
    try {
      const response = await this.client.get('/api/tags');
      return response.data.models || [];
    } catch (error) {
      throw new Error(`Failed to list models: ${error.message}`);
    }
  }

  /**
   * Send a message to Ollama and get response
   */
  async sendMessage(message, model = 'granite-code:3b', conversationHistory = []) {
    try {
      const messages = [
        ...conversationHistory,
        { role: 'user', content: message }
      ];

      const response = await this.client.post('/api/chat', {
        model: model,
        messages: messages,
        stream: false
      });

      return response.data.message.content;
    } catch (error) {
      throw new Error(`Failed to send message: ${error.message}`);
    }
  }

  /**
   * Start an interview session for a specific role
   */
  async startInterview(role = 'Software Engineer', model = 'granite-code:3b') {
    const systemPrompt = this.getInterviewPrompt(role);

    try {
      const response = await this.client.post('/api/chat', {
        model: model,
        messages: [
          {
            role: 'system',
            content: systemPrompt
          },
          {
            role: 'user',
            content: 'Please start the interview and ask me the first question.'
          }
        ],
        stream: false
      });

      return response.data.message.content;
    } catch (error) {
      throw new Error(`Failed to start interview: ${error.message}`);
    }
  }

  /**
   * Get interview prompt based on role
   */
  getInterviewPrompt(role) {
    const prompts = {
      'Software Engineer': `You are an experienced technical interviewer conducting a job interview for a Junior Software Engineer position.

Your interview will consist of exactly 5 questions covering:
1. Data structures and algorithms knowledge
2. A coding problem-solving scenario
3. Debugging approach and methodology
4. Team collaboration and communication
5. Learning mindset and continuous improvement

Guidelines:
- Ask one question at a time
- Keep questions clear and concise
- Be professional but friendly
- After the candidate answers, acknowledge briefly and move to the next question
- After 5 questions, thank the candidate and end the interview

Start by introducing yourself and asking the first question.`,

      'Product Manager': `You are an experienced interviewer conducting a job interview for a Product Manager position.

Your interview will consist of exactly 5 questions covering:
1. Product strategy and vision
2. Stakeholder management experience
3. Data-driven decision making
4. Conflict resolution skills
5. Innovation and creativity examples

Guidelines:
- Ask one question at a time
- Keep questions clear and concise
- Be professional but friendly
- After the candidate answers, acknowledge briefly and move to the next question
- After 5 questions, thank the candidate and end the interview

Start by introducing yourself and asking the first question.`,

      'Data Analyst': `You are an experienced interviewer conducting a job interview for a Data Analyst position.

Your interview will consist of exactly 5 questions covering:
1. SQL and database knowledge
2. Data visualization and reporting
3. Statistical analysis approach
4. Business problem-solving with data
5. Communication of insights to non-technical stakeholders

Guidelines:
- Ask one question at a time
- Keep questions clear and concise
- Be professional but friendly
- After the candidate answers, acknowledge briefly and move to the next question
- After 5 questions, thank the candidate and end the interview

Start by introducing yourself and asking the first question.`
    };

    return prompts[role] || prompts['Software Engineer'];
  }
}

module.exports = OllamaService;
