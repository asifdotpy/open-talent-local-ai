import { create } from 'zustand';

// Types matching the backend API
export interface InterviewQuestion {
  question_text: string;
  question_type: string;
  difficulty: string;
  priority: 'must_ask' | 'nice_to_ask';
  expected_duration: number;
  evaluation_criteria: string[];
  follow_up_questions: string[];
  skill_assessed: string[];
  ai_generated: boolean;
  generated_at: string;
}

export interface QuestionTemplate {
  template_id: string;
  template_name: string;
  description: string;
  job_roles: string[];
  questions: InterviewQuestion[];
  is_public: boolean;
  created_by?: string;
  usage_count: number;
}

export interface GenerationResponse {
  questions: InterviewQuestion[];
  total_questions: number;
  total_duration: number;
  must_ask_count: number;
  nice_to_ask_count: number;
  metadata: {
    source: string;
    prompt_used?: string;
    template_id?: string;
  };
}

export interface NaturalLanguagePrompt {
  prompt: string;
  job_title?: string;
  required_skills?: string[];
  company_culture?: string[];
  num_questions?: number;
  difficulty?: string;
  interview_duration?: number;
}

interface QuestionBuilderState {
  // Data
  templates: QuestionTemplate[];
  generatedQuestions: InterviewQuestion[];
  currentTemplate: QuestionTemplate | null;
  isLoading: boolean;
  error: string | null;

  // UI State
  selectedTemplateId: string | null;
  naturalLanguagePrompt: NaturalLanguagePrompt;
  showAdvancedOptions: boolean;

  // Actions
  loadTemplates: () => Promise<void>;
  generateQuestions: (prompt: NaturalLanguagePrompt) => Promise<void>;
  useTemplate: (templateId: string) => Promise<void>;
  createCustomTemplate: (template: Omit<QuestionTemplate, 'template_id' | 'usage_count'>) => Promise<void>;
  pinQuestion: (questionIndex: number) => void;
  unpinQuestion: (questionIndex: number) => void;
  resetQuestions: () => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  updatePrompt: (updates: Partial<NaturalLanguagePrompt>) => void;
  toggleAdvancedOptions: () => void;
  selectTemplate: (templateId: string | null) => void;
}

export const useQuestionBuilderStore = create<QuestionBuilderState>((set, get) => ({
  // Initial state
  templates: [],
  generatedQuestions: [],
  currentTemplate: null,
  isLoading: false,
  error: null,
  selectedTemplateId: null,
  naturalLanguagePrompt: {
    prompt: '',
    job_title: '',
    required_skills: [],
    company_culture: [],
    num_questions: 5,
    difficulty: 'mid_level',
    interview_duration: 45
  },
  showAdvancedOptions: false,

  // Load available templates
  loadTemplates: async () => {
    set({ isLoading: true, error: null });
    try {
      const { questionBuilderAPI } = await import('../services/api');
      const templates = await questionBuilderAPI.getTemplates();
      set({ templates, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load templates',
        isLoading: false
      });
    }
  },

  // Generate questions from natural language
  generateQuestions: async (prompt: NaturalLanguagePrompt) => {
    set({ isLoading: true, error: null });
    try {
      const { questionBuilderAPI } = await import('../services/api');
      const response: GenerationResponse = await questionBuilderAPI.generateQuestions(prompt);
      set({
        generatedQuestions: response.questions,
        naturalLanguagePrompt: prompt,
        selectedTemplateId: null,
        currentTemplate: null,
        isLoading: false
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to generate questions',
        isLoading: false
      });
    }
  },

  // Use a template to generate questions
  useTemplate: async (templateId: string) => {
    set({ isLoading: true, error: null });
    try {
      const { questionBuilderAPI } = await import('../services/api');
      const response: GenerationResponse = await questionBuilderAPI.useTemplate(templateId);

      // Find the template details
      const { templates } = get();
      const template = templates.find(t => t.template_id === templateId);

      set({
        generatedQuestions: response.questions,
        currentTemplate: template || null,
        selectedTemplateId: templateId,
        naturalLanguagePrompt: {
          prompt: '',
          job_title: '',
          required_skills: [],
          company_culture: [],
          num_questions: 5,
          difficulty: 'mid_level',
          interview_duration: 45
        },
        isLoading: false
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to use template',
        isLoading: false
      });
    }
  },

  // Create custom template
  createCustomTemplate: async (templateData) => {
    set({ isLoading: true, error: null });
    try {
      const { questionBuilderAPI } = await import('../services/api');
      const newTemplate = await questionBuilderAPI.createTemplate(templateData);
      const { templates } = get();
      set({
        templates: [...templates, newTemplate],
        isLoading: false
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create template',
        isLoading: false
      });
    }
  },

  // Pin a question (make it must-ask)
  pinQuestion: (questionIndex: number) => {
    const { generatedQuestions } = get();
    if (questionIndex >= 0 && questionIndex < generatedQuestions.length) {
      const updatedQuestions = [...generatedQuestions];
      updatedQuestions[questionIndex] = {
        ...updatedQuestions[questionIndex],
        priority: 'must_ask'
      };
      set({ generatedQuestions: updatedQuestions });
    }
  },

  // Unpin a question (make it nice-to-ask)
  unpinQuestion: (questionIndex: number) => {
    const { generatedQuestions } = get();
    if (questionIndex >= 0 && questionIndex < generatedQuestions.length) {
      const updatedQuestions = [...generatedQuestions];
      updatedQuestions[questionIndex] = {
        ...updatedQuestions[questionIndex],
        priority: 'nice_to_ask'
      };
      set({ generatedQuestions: updatedQuestions });
    }
  },

  // Reset questions
  resetQuestions: () => {
    set({
      generatedQuestions: [],
      currentTemplate: null,
      selectedTemplateId: null,
      error: null
    });
  },

  // Utility actions
  setError: (error: string | null) => {
    set({ error });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  updatePrompt: (updates: Partial<NaturalLanguagePrompt>) => {
    const { naturalLanguagePrompt } = get();
    set({
      naturalLanguagePrompt: { ...naturalLanguagePrompt, ...updates }
    });
  },

  toggleAdvancedOptions: () => {
    const { showAdvancedOptions } = get();
    set({ showAdvancedOptions: !showAdvancedOptions });
  },

  selectTemplate: (templateId: string | null) => {
    set({ selectedTemplateId: templateId });
  }
}));