import { debugLog } from '../utils/logger.js';

// Audio processing state
let audioContext = null;
let analyser = null;
let microphone = null;
let audioDataArray = null;
let audioBufferLength = 0;

// Initialize audio processing system
export async function initAudioProcessing() {
  try {
    // Create audio context
    audioContext = new (window.AudioContext || window.webkitAudioContext)();

    // Create analyser node for frequency analysis
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.8;

    audioBufferLength = analyser.frequencyBinCount;
    audioDataArray = new Uint8Array(audioBufferLength);

    debugLog('AUDIO', 'Audio processing initialized');
  } catch (error) {
    debugLog('ERROR', 'Failed to initialize audio processing:', error);
    throw error;
  }
}

// Get microphone access for real-time audio analysis
export async function initMicrophoneAccess() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 44100,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true
      }
    });

    microphone = audioContext.createMediaStreamSource(stream);
    microphone.connect(analyser);

    debugLog('MICROPHONE', 'Microphone access granted for audio processing');
  } catch (error) {
    debugLog('ERROR', 'Failed to get microphone access:', error);
    throw error;
  }
}

// Get current audio frequency data
export function getAudioFrequencyData() {
  if (!analyser) return null;

  analyser.getByteFrequencyData(audioDataArray);
  return audioDataArray;
}

// Get current audio time domain data
export function getAudioTimeDomainData() {
  if (!analyser) return null;

  analyser.getByteTimeDomainData(audioDataArray);
  return audioDataArray;
}

// Calculate audio volume level (0-1)
export function getAudioVolume() {
  const frequencyData = getAudioFrequencyData();
  if (!frequencyData) return 0;

  let sum = 0;
  for (let i = 0; i < frequencyData.length; i++) {
    sum += frequencyData[i];
  }

  return sum / (frequencyData.length * 255); // Normalize to 0-1
}

// Detect if audio is currently playing (has significant volume)
export function isAudioActive(threshold = 0.01) {
  return getAudioVolume() > threshold;
}

// Get dominant frequency from audio spectrum
export function getDominantFrequency() {
  const frequencyData = getAudioFrequencyData();
  if (!frequencyData) return 0;

  let maxValue = 0;
  let maxIndex = 0;

  for (let i = 0; i < frequencyData.length; i++) {
    if (frequencyData[i] > maxValue) {
      maxValue = frequencyData[i];
      maxIndex = i;
    }
  }

  // Convert bin index to frequency
  const nyquist = audioContext.sampleRate / 2;
  return (maxIndex * nyquist) / frequencyData.length;
}

// Analyze audio for speech patterns
export function analyzeSpeechPatterns() {
  const frequencyData = getAudioFrequencyData();
  if (!frequencyData) return null;

  // Simple speech detection based on frequency ranges
  const lowFreq = frequencyData.slice(0, 10).reduce((a, b) => a + b, 0) / 10;
  const midFreq = frequencyData.slice(10, 50).reduce((a, b) => a + b, 0) / 40;
  const highFreq = frequencyData.slice(50).reduce((a, b) => a + b, 0) / (frequencyData.length - 50);

  return {
    lowFrequency: lowFreq / 255,
    midFrequency: midFreq / 255,
    highFrequency: highFreq / 255,
    isSpeech: midFreq > 100 && highFreq > 50, // Rough speech detection
    volume: getAudioVolume()
  };
}

// Create audio buffer from array
export function createAudioBuffer(audioData, sampleRate = 44100) {
  const buffer = audioContext.createBuffer(1, audioData.length, sampleRate);

  // Copy audio data to buffer
  const channelData = buffer.getChannelData(0);
  for (let i = 0; i < audioData.length; i++) {
    channelData[i] = audioData[i] / 255 - 0.5; // Convert to -0.5 to 0.5 range
  }

  return buffer;
}

// Play audio buffer
export function playAudioBuffer(buffer) {
  const source = audioContext.createBufferSource();
  source.buffer = buffer;
  source.connect(audioContext.destination);
  source.start();

  return source;
}

// Generate test tone for debugging
export function generateTestTone(frequency = 440, duration = 1) {
  const sampleRate = audioContext.sampleRate;
  const numSamples = sampleRate * duration;
  const audioData = new Float32Array(numSamples);

  for (let i = 0; i < numSamples; i++) {
    audioData[i] = Math.sin(2 * Math.PI * frequency * i / sampleRate) * 0.1;
  }

  const buffer = audioContext.createBuffer(1, numSamples, sampleRate);
  buffer.copyFromChannel(audioData, 0);

  return buffer;
}

// Clean up audio resources
export function cleanupAudio() {
  if (microphone) {
    microphone.disconnect();
    microphone = null;
  }

  if (audioContext && audioContext.state !== 'closed') {
    audioContext.close();
    audioContext = null;
  }

  analyser = null;
  audioDataArray = null;
  audioBufferLength = 0;

  debugLog('AUDIO', 'Audio resources cleaned up');
}

// Get audio context state
export function getAudioState() {
  return {
    contextState: audioContext ? audioContext.state : null,
    hasMicrophone: !!microphone,
    analyserActive: !!analyser,
    bufferLength: audioBufferLength
  };
}
