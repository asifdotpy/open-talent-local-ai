import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:8004'; // Interview Service
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Interview API endpoints (now room-based)
export const interviewAPI = {
  // Create a new interview room
  createRoom: async (candidateId: string, jobRole: string) => {
    const response = await axios.post('/api/v1/rooms', {
      room_id: `room-${Date.now()}`,
      participants: [{
        user_id: candidateId,
        role: 'candidate',
        display_name: candidateId,
        joined_at: new Date().toISOString()
      }],
      duration_minutes: 30,
      job_id: null,
      project_id: null,
      job_description: `Interview for ${jobRole} position`
    });
    return response.data;
  },

  // Get room details
  getRoom: async (roomId: string) => {
    const response = await axios.get(`/api/v1/rooms/${roomId}`);
    return response.data;
  },

  // Start WebRTC connection for room
  startWebRTC: async (roomId: string, offer: any) => {
    const response = await axios.post(`/api/v1/rooms/${roomId}/webrtc`, {
      type: 'offer',
      sdp: offer.sdp
    });
    return response.data;
  },

  // Send WebRTC answer
  sendWebRTCAnswer: async (roomId: string, answer: any) => {
    const response = await axios.post(`/api/v1/rooms/${roomId}/webrtc`, {
      type: 'answer',
      sdp: answer.sdp
    });
    return response.data;
  },

  // Send ICE candidate
  sendICECandidate: async (roomId: string, candidate: any) => {
    const response = await axios.post(`/api/v1/rooms/${roomId}/webrtc`, {
      type: 'candidate',
      candidate: candidate.candidate,
      sdpMLineIndex: candidate.sdpMLineIndex,
      sdpMid: candidate.sdpMid
    });
    return response.data;
  },

  // Begin interview in room
  beginInterview: async (roomId: string) => {
    const response = await axios.post(`/api/v1/rooms/${roomId}/begin`);
    return response.data;
  },

  // Get next question
  getNextQuestion: async (roomId: string) => {
    const response = await axios.post(`/api/v1/rooms/${roomId}/next-question`);
    return response.data;
  },

  // Submit answer
  submitAnswer: async (roomId: string, questionId: string, answer: string) => {
    const response = await axios.post(`/api/v1/rooms/${roomId}/answer`, null, {
      params: { question_id: questionId, answer }
    });
    return response.data;
  },

  // Complete interview
  completeInterview: async (roomId: string) => {
    const response = await axios.post(`/api/v1/rooms/${roomId}/complete`);
    return response.data;
  },

  // Get interview results
  getInterviewResults: async (roomId: string) => {
    const response = await axios.get(`/api/v1/rooms/${roomId}/results`);
    return response.data;
  }
};

// Voice Service API (for future direct access)
export const voiceAPI = {
  baseURL: 'http://localhost:8002',

  // Text to speech
  textToSpeech: async (text: string, voice: string = 'alloy') => {
    const response = await axios.post(`${voiceAPI.baseURL}/tts`, {
      text,
      voice
    });
    return response.data;
  },

  // Speech to text
  speechToText: async (audioData: string) => {
    const response = await axios.post(`${voiceAPI.baseURL}/stt`, {
      audio_base64: audioData
    });
    return response.data;
  }
};

// Avatar Service API (for avatar management)
export const avatarAPI = {
  baseURL: 'http://localhost:8001',

  // Get available avatars
  getAvatars: async () => {
    const response = await axios.get(`${avatarAPI.baseURL}/avatars`);
    return response.data;
  },

  // Generate lip-sync video
  generateLipSync: async (audioBase64: string, avatarId: string = 'default', background: string = 'office') => {
    const response = await axios.post(`${avatarAPI.baseURL}/lipsync`, {
      audio_base64: audioBase64,
      avatar_id: avatarId,
      background
    });
    return response.data;
  },

  // Get avatar model URL
  getAvatarModel: async (avatarId: string) => {
    const response = await axios.get(`${avatarAPI.baseURL}/avatars/${avatarId}/model`);
    return response.data;
  }
};

// Health check all services
export const healthAPI = {
  checkInterviewService: async () => {
    const response = await axios.get('http://localhost:8004/health/');
    return response.data;
  },

  checkVoiceService: async () => {
    const response = await axios.get('http://localhost:8002/health');
    return response.data;
  },

  checkAvatarService: async () => {
    const response = await axios.get('http://localhost:8001/health');
    return response.data;
  },

  checkConversationService: async () => {
    const response = await axios.get('http://localhost:8003/health/');
    return response.data;
  }
};

// Question Builder API endpoints
export const questionBuilderAPI = {
  // Health check
  health: async () => {
    const response = await axios.get('/api/v1/health');
    return response.data;
  },

  // Generate questions from natural language
  generateQuestions: async (data: {
    prompt: string;
    job_title?: string;
    required_skills?: string[];
    company_culture?: string[];
    num_questions?: number;
    difficulty?: string;
    interview_duration?: number;
  }) => {
    const response = await axios.post('/api/v1/generate', data);
    return response.data;
  },

  // Get available templates
  getTemplates: async () => {
    const response = await axios.get('/api/v1/templates');
    return response.data;
  },

  // Get specific template
  getTemplate: async (templateId: string) => {
    const response = await axios.get(`/api/v1/templates/${templateId}`);
    return response.data;
  },

  // Use a template to generate questions
  useTemplate: async (templateId: string) => {
    const response = await axios.post(`/api/v1/templates/${templateId}/use`, {});
    return response.data;
  },

  // Create custom template
  createTemplate: async (data: {
    template_name: string;
    description: string;
    questions: any[];
    job_roles: string[];
    is_public?: boolean;
  }) => {
    const response = await axios.post('/api/v1/templates', data);
    return response.data;
  }
};