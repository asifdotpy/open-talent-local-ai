import { create } from 'zustand';

// Types
export interface InterviewQuestion {
  id: string;
  text: string;
  order: number;
  response?: string;
  response_timestamp?: string;
}

export interface InterviewAnswer {
  question_id: string;
  answer: string;
  timestamp: string;
}

export interface InterviewRoom {
  room_id: string;
  candidate_id: string;
  job_role: string;
  status: 'created' | 'in_progress' | 'completed';
  questions: InterviewQuestion[];
  current_question_index: number;
  answers: InterviewAnswer[];
  duration: number; // in seconds
  started_at?: string;
  completed_at?: string;
  participants: any[];
  webrtc_offer?: any;
  webrtc_answer?: any;
}

export interface InterviewResult {
  room_id: string;
  candidate_id: string;
  job_role: string;
  total_questions: number;
  completed_questions: number;
  average_response_length: number;
  completion_rate: number;
  assessment_score: number;
  feedback: string;
}

export interface AssessmentResult {
  category: string;
  score: number;
  maxScore: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
}

// Avatar Types
export interface Avatar {
  id: string;
  name: string;
  url: string;
  morphTargetType: 'ARKit' | 'Oculus' | 'RPM';
  hasFullLipSync: boolean;
  isLocal: boolean;
  thumbnail?: string;
}

export interface PhonemeData {
  phoneme: string;
  timestamp: number;
  intensity: number;
}

export interface AudioData {
  audioUrl?: string;
  audioBase64?: string;
  duration?: number;
}

interface InterviewState {
  // Current room
  currentRoom: InterviewRoom | null;
  currentQuestion: InterviewQuestion | null;
  isLoading: boolean;
  error: string | null;

  // WebRTC state
  webrtcConnection: RTCPeerConnection | null;
  isWebRTCConnected: boolean;

  // Avatar state
  currentAvatar: Avatar | null;
  availableAvatars: Avatar[];
  phonemes: PhonemeData[];
  audioData: AudioData | null;
  isAvatarLoading: boolean;
  avatarError: string | null;

  // Actions
  createRoom: (candidateId: string, jobRole: string) => Promise<void>;
  beginInterview: () => Promise<void>;
  getNextQuestion: () => Promise<void>;
  submitAnswer: (answer: string) => Promise<void>;
  completeInterview: () => Promise<InterviewResult>;
  getInterviewResults: () => Promise<AssessmentResult[]>;
  resetRoom: () => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;

  // WebRTC actions
  initializeWebRTC: () => Promise<void>;
  startWebRTC: () => Promise<void>;
  closeWebRTC: () => void;

  // Avatar actions
  initializeAvatars: () => Promise<void>;
  selectAvatar: (avatar: Avatar) => void;
  updatePhonemes: (phonemes: PhonemeData[]) => void;
  setAudioData: (audioData: AudioData | null) => void;
  setAvatarLoading: (loading: boolean) => void;
  setAvatarError: (error: string | null) => void;
}

export const useInterviewStore = create<InterviewState>((set, get) => ({
  currentRoom: null,
  currentQuestion: null,
  isLoading: false,
  error: null,

  // WebRTC initial state
  webrtcConnection: null,
  isWebRTCConnected: false,

  // Avatar initial state
  currentAvatar: null,
  availableAvatars: [],
  phonemes: [],
  audioData: null,
  isAvatarLoading: false,
  avatarError: null,

  createRoom: async (candidateId: string, jobRole: string) => {
    set({ isLoading: true, error: null });
    try {
      const { interviewAPI } = await import('../services/api');
      const room = await interviewAPI.createRoom(candidateId, jobRole);
      set({
        currentRoom: room,
        currentQuestion: null,
        isLoading: false
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create interview room',
        isLoading: false
      });
    }
  },

  beginInterview: async () => {
    const { currentRoom } = get();
    if (!currentRoom) return;

    set({ isLoading: true, error: null });
    try {
      const { interviewAPI } = await import('../services/api');
      const updatedRoom = await interviewAPI.beginInterview(currentRoom.room_id);
      set({
        currentRoom: updatedRoom,
        isLoading: false
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to begin interview',
        isLoading: false
      });
    }
  },

  getNextQuestion: async () => {
    const { currentRoom } = get();
    if (!currentRoom) return;

    set({ isLoading: true, error: null });
    try {
      const { interviewAPI } = await import('../services/api');
      const response = await interviewAPI.getNextQuestion(currentRoom.room_id);
      set({
        currentQuestion: response.question,
        isLoading: false
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to get next question',
        isLoading: false
      });
    }
  },

  submitAnswer: async (answer: string) => {
    const { currentRoom, currentQuestion } = get();
    if (!currentRoom || !currentQuestion) return;

    set({ isLoading: true, error: null });
    try {
      const { interviewAPI } = await import('../services/api');
      await interviewAPI.submitAnswer(currentRoom.room_id, currentQuestion.id, answer);
      set({ isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to submit answer',
        isLoading: false
      });
    }
  },

  completeInterview: async () => {
    const { currentRoom } = get();
    if (!currentRoom) throw new Error('No active room');

    set({ isLoading: true, error: null });
    try {
      const { interviewAPI } = await import('../services/api');
      const result = await interviewAPI.completeInterview(currentRoom.room_id);
      set({
        currentRoom: { ...currentRoom, status: 'completed' },
        currentQuestion: null,
        isLoading: false
      });
      return result;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to complete interview',
        isLoading: false
      });
      throw error;
    }
  },

  getInterviewResults: async () => {
    const { currentRoom } = get();
    if (!currentRoom) throw new Error('No active room');

    set({ isLoading: true, error: null });
    try {
      const { interviewAPI } = await import('../services/api');
      const results = await interviewAPI.getInterviewResults(currentRoom.room_id);
      set({ isLoading: false });
      return results;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to get interview results',
        isLoading: false
      });
      throw error;
    }
  },

  resetRoom: () => {
    const { webrtcConnection } = get();
    if (webrtcConnection) {
      webrtcConnection.close();
    }
    set({
      currentRoom: null,
      currentQuestion: null,
      error: null,
      isLoading: false,
      webrtcConnection: null,
      isWebRTCConnected: false
    });
  },

  // WebRTC actions
  initializeWebRTC: async () => {
    try {
      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      });

      pc.onicecandidate = async (event) => {
        if (event.candidate) {
          // Send ICE candidate to backend
          const { currentRoom } = get();
          if (currentRoom) {
            try {
              const { interviewAPI } = await import('../services/api');
              await interviewAPI.sendICECandidate(currentRoom.room_id, event.candidate);
            } catch (error) {
              console.error('Failed to send ICE candidate:', error);
            }
          }
        }
      };

      pc.onconnectionstatechange = () => {
        set({ isWebRTCConnected: pc.connectionState === 'connected' });
      };

      set({ webrtcConnection: pc });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to initialize WebRTC'
      });
    }
  },

  startWebRTC: async () => {
    const { currentRoom, webrtcConnection } = get();
    if (!currentRoom || !webrtcConnection) return;

    try {
      // Create offer
      const offer = await webrtcConnection.createOffer();
      await webrtcConnection.setLocalDescription(offer);

      // Send offer to backend
      const { interviewAPI } = await import('../services/api');
      const response = await interviewAPI.startWebRTC(currentRoom.room_id, offer);

      // Set remote description from answer
      if (response.answer) {
        await webrtcConnection.setRemoteDescription(
          new RTCSessionDescription({
            type: 'answer',
            sdp: response.answer.sdp
          })
        );
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to start WebRTC connection'
      });
    }
  },

  closeWebRTC: () => {
    const { webrtcConnection } = get();
    if (webrtcConnection) {
      webrtcConnection.close();
      set({ webrtcConnection: null, isWebRTCConnected: false });
    }
  },

  // Avatar actions
  initializeAvatars: async () => {
    set({ isAvatarLoading: true, avatarError: null });
    try {
      // Import avatar service dynamically
      const { avatarService } = await import('../services/avatarService');
      const avatars = await avatarService.initializeAvatars();
      set({
        availableAvatars: avatars,
        currentAvatar: avatars[0] || null, // Default to first avatar
        isAvatarLoading: false
      });
    } catch (error) {
      set({
        avatarError: error instanceof Error ? error.message : 'Failed to initialize avatars',
        isAvatarLoading: false
      });
    }
  },

  selectAvatar: (avatar: Avatar) => {
    set({ currentAvatar: avatar });
  },

  updatePhonemes: (phonemes: PhonemeData[]) => {
    set({ phonemes });
  },

  setAudioData: (audioData: AudioData | null) => {
    set({ audioData });
  },

  setAvatarLoading: (loading: boolean) => {
    set({ isAvatarLoading: loading });
  },

  setAvatarError: (error: string | null) => {
    set({ avatarError: error });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  }
}));