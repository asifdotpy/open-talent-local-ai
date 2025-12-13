/**
 * Voice Input Service
 * Handles microphone capture, recording, voice activity detection, and storage
 * Part of Day 5-6 implementation
 */

import WaveSurfer from 'wavesurfer.js';

export interface VoiceSession {
  sessionId: string;
  isRecording: boolean;
  recordedAudio: Blob;
  waveformData: number[];
  duration: number;
  timestamp: Date;
  encrypted: boolean;
}

export interface VoiceInputConfig {
  sampleRate: number;          // 16000 Hz for Whisper
  channelCount: number;        // 1 (mono)
  vadThreshold: number;        // 0-1, when to stop recording
  maxDuration: number;         // 5 minutes max
  autoStopSilence: number;     // ms of silence before auto-stop
}

const DEFAULT_CONFIG: VoiceInputConfig = {
  sampleRate: 16000,
  channelCount: 1,
  vadThreshold: 0.5,
  maxDuration: 5 * 60 * 1000, // 5 minutes
  autoStopSilence: 2000,       // 2 seconds of silence
};

export class VoiceInputService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private microphoneStream: MediaStream | null = null;
  private recordedChunks: Blob[] = [];
  private vad: any = null;
  private waveformData: number[] = [];
  private currentSession: VoiceSession | null = null;
  private audioLevel: number = 0;
  private silenceStartTime: number = 0;
  private config: VoiceInputConfig = DEFAULT_CONFIG;
  private recordingStartTime: number = 0;
  private analyserNode: AnalyserNode | null = null;
  private dataArray: Uint8Array | null = null;

  constructor() {
    this.recordedChunks = [];
    this.waveformData = [];
    this.silenceStartTime = Date.now();
  }

  /**
   * Request microphone access from the user
   */
  async requestMicrophoneAccess(): Promise<boolean> {
    try {
      this.microphoneStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: { ideal: 16000 },
        },
      });
      console.log('✅ Microphone access granted');
      return true;
    } catch (error) {
      console.error('❌ Microphone access denied:', error);
      return false;
    }
  }

  /**
   * Check if microphone access is available
   */
  async checkMicrophoneAccess(): Promise<{
    available: boolean;
    permitted: boolean;
  }> {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      return { available: false, permitted: false };
    }

    try {
      const permission = await navigator.permissions.query({
        name: 'microphone' as any,
      });
      return {
        available: true,
        permitted: permission.state === 'granted',
      };
    } catch (error) {
      return { available: true, permitted: this.microphoneStream !== null };
    }
  }

  /**
   * Initialize audio context and VAD
   */
  private initializeAudioContext(): Promise<void> {
    if (this.audioContext) return Promise.resolve();

    this.audioContext = new (window as any).AudioContext();
    (this.audioContext as any).resume?.();

    // Setup analyser for audio level visualization
    this.analyserNode = this.audioContext!.createAnalyser();
    this.analyserNode.fftSize = 2048;
    this.dataArray = new Uint8Array(this.analyserNode.frequencyBinCount);

    return Promise.resolve();
  }

  /**
   * Start recording with voice activity detection
   */
  async startRecording(userConfig?: Partial<VoiceInputConfig>): Promise<VoiceSession> {
    if (!this.microphoneStream) {
      const hasAccess = await this.requestMicrophoneAccess();
      if (!hasAccess) {
        throw new Error('Microphone access denied');
      }
    }

    // Merge user config with defaults
    this.config = { ...DEFAULT_CONFIG, ...userConfig };

    // Initialize audio context
    await this.initializeAudioContext();

    // Reset state
    this.recordedChunks = [];
    this.waveformData = [];
    this.silenceStartTime = Date.now();
    this.recordingStartTime = Date.now();

    // Create media recorder
    const mimeType = MediaRecorder.isTypeSupported('audio/webm')
      ? 'audio/webm'
      : 'audio/wav';

    this.mediaRecorder = new MediaRecorder(this.microphoneStream!, {
      mimeType,
    });

    // Collect audio data
    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this.recordedChunks.push(event.data);
      }
    };

    this.mediaRecorder.onerror = (event) => {
      console.error('MediaRecorder error:', event.error);
    };

    // Start recording
    this.mediaRecorder.start(100); // Collect data every 100ms

    // Connect analyser for real-time level
    if (this.audioContext && this.microphoneStream) {
      const source = this.audioContext.createMediaStreamSource(this.microphoneStream!);
      source.connect(this.analyserNode!);
    }

    // Create session
    this.currentSession = {
      sessionId: this.generateSessionId(),
      isRecording: true,
      recordedAudio: new Blob(),
      waveformData: [],
      duration: 0,
      timestamp: new Date(),
      encrypted: false,
    };

    console.log('🎤 Recording started');
    return this.currentSession;
  }

  /**
   * Stop recording and return audio blob
   */
  async stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('No active recording'));
        return;
      }

      this.mediaRecorder.onstop = async () => {
        if (this.recordedChunks.length === 0) {
          reject(new Error('No audio data recorded'));
          return;
        }

        const mimeType = this.recordedChunks[0].type || 'audio/webm';
        const audioBlob = new Blob(this.recordedChunks, { type: mimeType });

        if (this.currentSession) {
          this.currentSession.recordedAudio = audioBlob;
          this.currentSession.duration = Date.now() - this.recordingStartTime;
          this.currentSession.isRecording = false;
        }

        console.log('⏹️  Recording stopped:', {
          duration: this.currentSession?.duration,
          size: audioBlob.size,
        });

        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Get current audio level (0-100) for visualization
   */
  getAudioLevel(): number {
    if (!this.analyserNode || !this.dataArray) {
      return 0;
    }

    this.analyserNode.getByteFrequencyData(this.dataArray as any);
    const average =
      Array.from(this.dataArray).reduce((a, b) => a + b) / this.dataArray.length;

    // Normalize to 0-100
    this.audioLevel = Math.min(100, Math.round((average / 255) * 100));
    return this.audioLevel;
  }

  /**
   * Get waveform data for visualization
   */
  getWaveformData(): number[] {
    return this.waveformData;
  }

  /**
   * Check if recording is active
   */
  isRecording(): boolean {
    return this.currentSession?.isRecording ?? false;
  }

  /**
   * Get current session
   */
  getSession(): VoiceSession | null {
    return this.currentSession;
  }

  /**
   * Clean up audio resources
   */
  dispose(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }

    if (this.microphoneStream) {
      this.microphoneStream.getTracks().forEach((track) => {
        track.stop();
      });
      this.microphoneStream = null;
    }

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }

    this.recordedChunks = [];
    this.waveformData = [];
    this.currentSession = null;
  }

  /**
   * Convert audio blob to WAV format (for better compatibility)
   */
  async convertToWav(audioBlob: Blob): Promise<Blob> {
    if (!this.audioContext) {
      await this.initializeAudioContext();
    }

    const arrayBuffer = await audioBlob.arrayBuffer();
    const audioBuffer = await this.audioContext!.decodeAudioData(arrayBuffer);

    return this.encodeWav(audioBuffer);
  }

  /**
   * Encode audio buffer to WAV
   */
  private encodeWav(audioBuffer: AudioBuffer): Blob {
    const numberOfChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;

    const bytesPerSample = bitDepth / 8;
    const blockAlign = numberOfChannels * bytesPerSample;

    const channels = [];
    for (let i = 0; i < numberOfChannels; i++) {
      channels.push(audioBuffer.getChannelData(i));
    }

    const interleaved = this.interleave(channels);
    const dataLength = interleaved.length * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataLength);
    const view = new DataView(buffer);

    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    const writeFloat = (offset: number, input: Float32Array) => {
      let index = 0;
      const volume = 1;
      for (let i = 0; i < input.length; i++, index += 2) {
        const sample = input[i] < 0 ? input[i] * 0x8000 : input[i] * 0x7fff;
        view.setInt16(offset + index, Math.max(-32768, Math.min(32767, sample)), true);
      }
    };

    // WAV header
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + dataLength, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true); // chunk size
    view.setUint16(20, format, true);
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);
    writeString(36, 'data');
    view.setUint32(40, dataLength, true);

    writeFloat(44, interleaved);

    return new Blob([buffer], { type: 'audio/wav' });
  }

  /**
   * Interleave audio channels
   */
  private interleave(channels: Float32Array[]): Float32Array {
    const length = channels[0].length * channels.length;
    const result = new Float32Array(length);

    let index = 0;
    const channelCount = channels.length;

    for (let i = 0; i < channels[0].length; i++) {
      for (let j = 0; j < channelCount; j++) {
        result[index++] = channels[j][i];
      }
    }

    return result;
  }

  /**
   * Generate unique session ID
   */
  private generateSessionId(): string {
    return `voice-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton instance
export const voiceInputService = new VoiceInputService();
