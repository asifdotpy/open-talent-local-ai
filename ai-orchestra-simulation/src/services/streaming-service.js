import { SERVICE_CONFIG } from '../config/app-config.js';
import { debugLog } from '../utils/logger.js';

// Live streaming state
let websocket = null;
let audioContext = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let isConnected = false;
let sessionId = null;

// WebSocket connection to avatar animation service
export async function initWebSocket() {
  return new Promise((resolve, reject) => {
    const wsUrl = `${SERVICE_CONFIG.avatarAnimation}/${sessionId}`;

    websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      debugLog('WEBSOCKET', 'Connected to avatar animation service');
      isConnected = true;
      resolve();
    };

    websocket.onmessage = (event) => {
      handleWebSocketMessage(JSON.parse(event.data));
    };

    websocket.onclose = () => {
      debugLog('WEBSOCKET', 'Disconnected from avatar animation service');
      isConnected = false;
    };

    websocket.onerror = (error) => {
      debugLog('WEBSOCKET', 'WebSocket error:', error);
      reject(error);
    };
  });
}

// Handle incoming WebSocket messages from avatar service
function handleWebSocketMessage(message) {
  debugLog('WEBSOCKET', 'Received message:', message.type);

  switch (message.type) {
    case 'animation_data':
      updateAvatarAnimation(message.data);
      break;
    case 'audio_chunk':
      playStreamingAudio(message.data);
      break;
    case 'phoneme_data':
      updatePhonemeAnimation(message.data);
      break;
    case 'interview_status':
      updateInterviewStatus(message.data);
      break;
    default:
      debugLog('WEBSOCKET', 'Unknown message type:', message.type);
  }
}

// Initialize Web Audio API context
export async function initAudioContext() {
  try {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    debugLog('AUDIO', 'Audio context initialized');
  } catch (error) {
    debugLog('ERROR', 'Failed to initialize audio context:', error);
    throw error;
  }
}

// Initialize microphone access for real-time STT
export async function initMicrophone() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 44100,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true
      }
    });

    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      audioChunks = [];

      // Send audio to voice service for STT
      await sendAudioToSTT(audioBlob);
    };

    debugLog('MICROPHONE', 'Microphone access granted');
  } catch (error) {
    debugLog('ERROR', 'Failed to initialize microphone:', error);
    throw error;
  }
}

// Send audio chunk to voice service for speech-to-text
async function sendAudioToSTT(audioBlob) {
  try {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'audio.webm');

    const response = await fetch(`${SERVICE_CONFIG.voiceService}/voice/stt`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`STT service error: ${response.status}`);
    }

    const result = await response.json();
    debugLog('STT', 'Transcribed text:', result.text);

    // Send transcribed text to conversation service
    await sendTextToConversation(result.text);

  } catch (error) {
    debugLog('ERROR', 'STT processing failed:', error);
  }
}

// Send transcribed text to conversation service for LLM processing
async function sendTextToConversation(text) {
  try {
    const response = await fetch(`${SERVICE_CONFIG.conversationService}/conversation/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        text: text,
        context: 'interview'
      })
    });

    if (!response.ok) {
      throw new Error(`Conversation service error: ${response.status}`);
    }

    const result = await response.json();
    debugLog('CONVERSATION', 'LLM response:', result.response);

    // Send LLM response to TTS service
    await sendTextToTTS(result.response);

  } catch (error) {
    debugLog('ERROR', 'Conversation processing failed:', error);
  }
}

// Send text to voice service for text-to-speech
async function sendTextToTTS(text) {
  try {
    const response = await fetch(`${SERVICE_CONFIG.voiceService}/voice/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`TTS service error: ${response.status}`);
    }

    // Stream audio response
    const audioStream = response.body;
    const reader = audioStream.getReader();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Send audio chunk to WebSocket for real-time playback and animation
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          type: 'audio_chunk',
          data: Array.from(value) // Convert Uint8Array to regular array
        }));
      }
    }

  } catch (error) {
    debugLog('ERROR', 'TTS processing failed:', error);
  }
}

// Play streaming audio from TTS service
function playStreamingAudio(audioData) {
  try {
    const audioBuffer = new Uint8Array(audioData);
    audioContext.decodeAudioData(audioBuffer.buffer, (buffer) => {
      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContext.destination);
      source.start();

      // Extract phonemes from audio for lip-sync
      extractPhonemesFromAudio(buffer);
    });
  } catch (error) {
    debugLog('ERROR', 'Failed to play streaming audio:', error);
  }
}

// Extract phonemes from streaming audio for real-time lip-sync
function extractPhonemesFromAudio(audioBuffer) {
  // This would integrate with a real-time phoneme extraction service
  // For now, we'll use a simplified approach
  const sampleRate = audioBuffer.sampleRate;
  const channelData = audioBuffer.getChannelData(0);

  // Simple energy-based phoneme detection (placeholder)
  const phonemes = analyzeAudioEnergy(channelData, sampleRate);

  // Send phoneme data to WebSocket for avatar animation
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(JSON.stringify({
      type: 'phoneme_data',
      data: phonemes
    }));
  }
}

// Simple audio energy analysis for phoneme detection
function analyzeAudioEnergy(channelData, sampleRate) {
  const frameSize = Math.floor(sampleRate * 0.01); // 10ms frames
  const phonemes = [];

  for (let i = 0; i < channelData.length; i += frameSize) {
    const frame = channelData.slice(i, i + frameSize);
    const energy = frame.reduce((sum, sample) => sum + sample * sample, 0) / frame.length;

    // Classify based on energy levels (simplified)
    let phoneme = 'SIL'; // Silence
    if (energy > 0.01) phoneme = 'AH'; // Vowel
    if (energy > 0.05) phoneme = 'AA'; // Strong vowel

    phonemes.push({
      phoneme: phoneme,
      intensity: Math.min(energy * 100, 1.0),
      timestamp: i / sampleRate
    });
  }

  return phonemes;
}

// Initialize live streaming instead of static assets
export async function initLiveStreaming() {
  debugLog('STREAMING', 'Initializing live 2-way interview streaming...');

  try {
    // Generate session ID
    sessionId = `interview_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Initialize WebSocket connection to avatar animation service
    await initWebSocket();

    // Initialize audio context for real-time processing
    await initAudioContext();

    // Initialize microphone access
    await initMicrophone();

    debugLog('SUCCESS', 'Live streaming initialized successfully');
    return true;
  } catch (error) {
    debugLog('ERROR', 'Failed to initialize live streaming:', error);
    return false;
  }
}

// Recording controls
export function toggleRecording() {
  if (!isRecording) {
    startRecording();
  } else {
    stopRecording();
  }
}

function startRecording() {
  if (mediaRecorder && mediaRecorder.state === 'inactive') {
    audioChunks = [];
    mediaRecorder.start(100); // Record in 100ms chunks
    isRecording = true;
    debugLog('RECORDING', 'Started audio recording');
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    isRecording = false;
    debugLog('RECORDING', 'Stopped audio recording');
  }
}

// Get current state
export function getStreamingState() {
  return {
    isConnected,
    isRecording,
    sessionId,
    websocket: websocket ? websocket.readyState : null
  };
}

// Placeholder functions for WebSocket message handlers
// These will be implemented by the animation system
function updateAvatarAnimation(data) {
  // To be implemented by animation system
  debugLog('WEBSOCKET', 'Avatar animation update received');
}

function updatePhonemeAnimation(data) {
  // To be implemented by animation system
  debugLog('WEBSOCKET', 'Phoneme animation update received');
}

function updateInterviewStatus(data) {
  // To be implemented by UI system
  debugLog('WEBSOCKET', 'Interview status update received');
}
