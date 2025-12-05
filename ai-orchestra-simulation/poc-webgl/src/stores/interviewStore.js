/**
 * Interview Store - Zustand State Management
 * Manages avatar interview state, voice service integration, and avatar selection
 */

import { create } from 'zustand';
import { rpmService } from '../services/rpmService';

// Avatar initialization will be handled by RPM service
let initializedAvatars = [];
let storeInstance = null;

// Initialize avatars on module load
const initializeAvatars = async () => {
  try {
    console.log('🎭 Initializing RPM avatars...');
    initializedAvatars = await rpmService.initializeAvatars();
    console.log('✅ RPM avatars initialized:', initializedAvatars.length);
    console.log('🎭 First avatar URL:', initializedAvatars[0]?.url);

    // Update the store instance if it exists
    if (storeInstance) {
      storeInstance.setState({
        availableAvatars: initializedAvatars,
        currentAvatar: initializedAvatars.length > 0 ? initializedAvatars[0] : null
      });
    }
  } catch (error) {
    console.error('❌ Failed to initialize RPM avatars:', error);
    // Fallback to empty array - will be handled gracefully
    initializedAvatars = [];
  }
};

// Start initialization
initializeAvatars();

const useInterviewStore = create((set, get) => {
  const store = {
    // State
    currentQuestion: null,
    isAvatarSpeaking: false,
    phonemes: [],
    audioData: null,
    audioTime: 0,
    duration: 0,

    // Avatar State - Start with null, will be updated when avatars load
    currentAvatar: null,
    availableAvatars: [],

    // WebSocket State
    wsConnection: null,
    wsConnected: false,
    wsSessionId: null,
    wsReconnectAttempts: 0,
    maxReconnectAttempts: 5,

    // Actions
    setPhonemes: (phonemes) => set({ phonemes }),
    setAudioData: (audioData) => set({ audioData }),
    setAudioTime: (time) => set({ audioTime: time }),
    setDuration: (duration) => set({ duration }),

    // Avatar Actions - Simplified for single avatar
    selectAvatar: (avatarId) => {
      console.log('🎭 Selecting avatar:', avatarId);
      const state = get();
      const avatar = state.availableAvatars.find(a => a.id === avatarId);
      if (avatar) {
        set({ currentAvatar: avatar });
        console.log('✅ Avatar selected:', avatar.name, 'Type:', avatar.morphTargetType);
      } else {
        console.error('❌ Avatar not found:', avatarId);
      }
    },

    refreshAvatars: async () => {
      try {
        console.log('🔄 Refreshing RPM avatars...');
        const avatars = await rpmService.initializeAvatars();
        initializedAvatars = avatars;
        set({
          availableAvatars: avatars,
          currentAvatar: avatars.length > 0 ? avatars[0] : null
        });
        console.log('✅ Avatars refreshed:', avatars.length);
        return avatars;
      } catch (error) {
        console.error('❌ Failed to refresh avatars:', error);
        throw error;
      }
    },

    // WebSocket Actions
    connectWebSocket: () => {
      // Skip WebSocket connection for demo - use local phoneme processing instead
      console.log('🔌 Skipping WebSocket connection - using local phoneme processing for demo');
      set({
        wsConnection: null,
        wsConnected: false,
        wsReconnectAttempts: 0
      });
    },

    disconnectWebSocket: () => {
      const state = get();
      if (state.wsConnection) {
        console.log('🔌 Disconnecting WebSocket...');
        state.wsConnection.close(1000, 'client_disconnect');
        set({
          wsConnection: null,
          wsConnected: false,
          wsSessionId: null
        });
      }
    },

    handleWebSocketMessage: (message) => {
      switch (message.type) {
        case 'connected':
          console.log('🎭 R3F session established:', message.sessionId);
          set({ wsSessionId: message.sessionId });
          // Send ready message
          get().sendWebSocketMessage({ type: 'ready' });
          break;

        case 'ready_ack':
          console.log('✅ R3F renderer ready');
          break;

        case 'phoneme_frame':
          // Update phoneme state for lip-sync animation
          set({
            phonemes: message.phonemeData ? [message.phonemeData] : [],
            audioTime: message.timestamp,
            isAvatarSpeaking: message.mouthOpen > 0.1
          });
          break;

        case 'heartbeat':
          // Respond to heartbeat
          get().sendWebSocketMessage({ type: 'heartbeat' });
          break;

        case 'broadcast':
          console.log('📢 Broadcast message:', message);
          break;

        case 'error':
          console.error('❌ WebSocket error message:', message.message);
          break;

        default:
          console.warn('⚠️ Unknown WebSocket message type:', message.type);
      }
    },

    sendWebSocketMessage: (message) => {
      const state = get();
      if (state.wsConnection && state.wsConnected) {
        state.wsConnection.send(JSON.stringify(message));
      } else {
        console.warn('⚠️ Cannot send WebSocket message - not connected');
      }
    },

    speakQuestion: async (text) => {
      set({ isAvatarSpeaking: true, currentQuestion: text });

      try {
        const response = await fetch('http://localhost:8002/voice/tts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: text,
            voice: 'en-US',
            extract_phonemes: true
          })
        });

        if (!response.ok) {
          throw new Error(`Voice service error: ${response.status}`);
        }

        const data = await response.json();

        set({
          phonemes: data.phonemes,
          audioData: data.audio_data,
          duration: data.duration
        });

        // For demo without WebSocket, directly update the state for lip sync
        console.log('🎭 Using local phoneme processing for lip sync demo');
        if (data.phonemes && data.phonemes.length > 0) {
          // Simulate real-time phoneme playback
          data.phonemes.forEach((phoneme, index) => {
            setTimeout(() => {
              set({
                phonemes: [phoneme], // Current phoneme for lip sync
                audioTime: phoneme.start,
                isAvatarSpeaking: true
              });
            }, index * 100); // Send phonemes with small delay
          });

          // Stop speaking after all phonemes
          setTimeout(() => {
            set({ isAvatarSpeaking: false });
          }, data.phonemes.length * 100 + 500);
        }

        return data;
      } catch (error) {
        console.error('Failed to generate speech:', error);
        set({ isAvatarSpeaking: false });
        throw error;
      }
    },

    stopSpeaking: () => set({
      isAvatarSpeaking: false,
      audioTime: 0,
      currentQuestion: null
    }),
  };

  // Set the store instance for async updates
  storeInstance = { setState: set };

  return store;
});

export { useInterviewStore };
