/**
 * Voice Service Integration - Phase 1 Audio Stream Handler
 *
 * Manages audio stream connection to Voice Service and feeds audio/phoneme data
 * to VideoRecorder and PhonemeMapper for synchronized lip-sync animation
 */

import { Logger } from '../utils/Logger.js';

export class VoiceServiceIntegration {
  constructor(config = {}) {
    this.logger = new Logger('VoiceServiceIntegration');

    this.config = {
      voiceServiceUrl: config.voiceServiceUrl || 'http://localhost:8002',
      synthesizeEndpoint: config.synthesizeEndpoint || '/api/synthesize',
      sampleRate: config.sampleRate || 48000,
      audioContext: config.audioContext || null,
      enablePhonemes: config.enablePhonemes !== false,
      enableVisualizer: config.enableVisualizer !== false,
      ...config,
    };

    // Audio stream management
    this.audioContext = this.config.audioContext || new (window.AudioContext || window.webkitAudioContext)();
    this.audioBuffer = null;
    this.audioSource = null;
    this.analyser = null;
    this.frequencyData = new Uint8Array(256);

    // Speech data
    this.currentSpeechText = '';
    this.phonemeSequence = [];
    this.currentPhonemeIndex = 0;
    this.speechStartTime = 0;

    // Callbacks
    this.onAudioReady = null;
    this.onPhonemeUpdate = null;
    this.onSpeechComplete = null;

    // State
    this.isConnected = false;
    this.isSynthesizing = false;

    this.logger.log('Initialized', {
      voiceServiceUrl: this.config.voiceServiceUrl,
      sampleRate: this.config.sampleRate,
      phonemesEnabled: this.config.enablePhonemes,
    });
  }

  /**
   * Synthesize speech from text via Voice Service
   * @param {string} text - Text to synthesize
   * @param {object} options - Synthesis options {voice, speed, pitch}
   * @returns {Promise} Resolves when synthesis complete
   */
  async synthesizeSpeech(text, options = {}) {
    if (this.isSynthesizing) {
      this.logger.warn('Synthesis already in progress');
      return null;
    }

    this.isSynthesizing = true;
    this.currentSpeechText = text;

    try {
      const payload = {
        text,
        voice: options.voice || 'default',
        speed: options.speed || 1.0,
        pitch: options.pitch || 1.0,
        format: 'wav',
        include_phonemes: this.config.enablePhonemes,
      };

      this.logger.log('Synthesizing speech', { textLength: text.length, ...payload });

      const response = await fetch(
        `${this.config.voiceServiceUrl}${this.config.synthesizeEndpoint}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error(`Voice Service error: ${response.statusText}`);
      }

      const data = await response.json();

      // Process audio
      if (data.audio_base64) {
        await this.processAudioData(data.audio_base64);
      }

      // Process phonemes
      if (data.phonemes && this.config.enablePhonemes) {
        this.phonemeSequence = data.phonemes;
        this.currentPhonemeIndex = 0;
        this.logger.log('Phoneme sequence loaded', { count: data.phonemes.length });
      }

      this.isConnected = true;

      if (this.onAudioReady) {
        this.onAudioReady({
          duration: data.duration || this.audioBuffer?.duration || 0,
          phonemeCount: this.phonemeSequence.length,
        });
      }

      return {
        success: true,
        duration: data.duration,
        phonemeCount: this.phonemeSequence.length,
        audioBuffer: this.audioBuffer,
      };
    } catch (error) {
      this.logger.error('Synthesis failed', { error: error.message });
      return { success: false, error: error.message };
    } finally {
      this.isSynthesizing = false;
    }
  }

  /**
   * Process base64-encoded audio data and create audio buffer
   */
  async processAudioData(base64Data) {
    try {
      // Decode base64 to binary
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Decode WAV to PCM
      const audioData = this.decodeWAV(bytes);

      // Create audio buffer
      this.audioBuffer = this.audioContext.createBuffer(
        audioData.channels,
        audioData.samples.length,
        this.config.sampleRate
      );

      const channelData = this.audioBuffer.getChannelData(0);
      channelData.set(audioData.samples);

      this.logger.log('Audio buffer created', {
        duration: this.audioBuffer.duration.toFixed(2),
        sampleRate: this.audioBuffer.sampleRate,
        channels: this.audioBuffer.numberOfChannels,
      });

      // Setup analyser for visualization
      if (this.config.enableVisualizer && !this.analyser) {
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 512;
      }
    } catch (error) {
      this.logger.error('Audio processing failed', { error: error.message });
    }
  }

  /**
   * Decode WAV file to PCM samples
   * @param {Uint8Array} wavData - WAV file data
   * @returns {object} Decoded audio {channels, samples}
   */
  decodeWAV(wavData) {
    const view = new DataView(wavData.buffer);

    // Skip WAV header (44 bytes for standard PCM)
    const headerOffset = 44;
    const dataLength = wavData.length - headerOffset;
    const samples = new Float32Array(dataLength / 2);

    // Convert 16-bit PCM to 32-bit float
    let offset = headerOffset;
    for (let i = 0; i < samples.length; i++) {
      const sample = view.getInt16(offset, true);
      samples[i] = sample < 0 ? sample / 0x8000 : sample / 0x7fff;
      offset += 2;
    }

    return {
      channels: 1,
      samples,
    };
  }

  /**
   * Play synthesized audio
   */
  playAudio() {
    if (!this.audioBuffer) {
      this.logger.warn('No audio buffer available');
      return;
    }

    if (this.audioSource) {
      this.audioSource.stop();
    }

    this.audioSource = this.audioContext.createBufferSource();
    this.audioSource.buffer = this.audioBuffer;

    // Connect to analyser if available
    if (this.analyser) {
      this.audioSource.connect(this.analyser);
      this.analyser.connect(this.audioContext.destination);
    } else {
      this.audioSource.connect(this.audioContext.destination);
    }

    this.speechStartTime = this.audioContext.currentTime;
    this.audioSource.start(0);

    this.logger.log('Audio playback started', {
      duration: this.audioBuffer.duration.toFixed(2),
    });
  }

  /**
   * Stop audio playback
   */
  stopAudio() {
    if (this.audioSource) {
      try {
        this.audioSource.stop();
      } catch (error) {
        // Already stopped
      }
      this.audioSource = null;
    }

    if (this.onSpeechComplete) {
      this.onSpeechComplete();
    }

    this.logger.log('Audio playback stopped');
  }

  /**
   * Get current phoneme for animation
   * @returns {object} Current phoneme {label, intensity} or null
   */
  getCurrentPhoneme() {
    if (!this.audioSource || !this.phonemeSequence.length) {
      return null;
    }

    const elapsedTime = this.audioContext.currentTime - this.speechStartTime;

    // Find current phoneme based on timestamp
    for (const phoneme of this.phonemeSequence) {
      if (elapsedTime >= phoneme.start && elapsedTime <= phoneme.end) {
        return {
          label: phoneme.label || phoneme.phoneme,
          start: phoneme.start,
          end: phoneme.end,
          intensity: phoneme.intensity || 1.0,
        };
      }
    }

    return null;
  }

  /**
   * Update phoneme callback (call from animation loop)
   */
  updatePhoneme() {
    if (!this.audioSource || !this.onPhonemeUpdate) {
      return;
    }

    const currentPhoneme = this.getCurrentPhoneme();
    if (currentPhoneme) {
      this.onPhonemeUpdate(currentPhoneme);
    }
  }

  /**
   * Get audio frequency data for visualization
   * @returns {Uint8Array} Frequency data
   */
  getFrequencyData() {
    if (this.analyser && this.audioSource) {
      this.analyser.getByteFrequencyData(this.frequencyData);
    }
    return this.frequencyData;
  }

  /**
   * Check audio playback status
   */
  isPlaying() {
    return this.audioSource !== null;
  }

  /**
   * Get current playback time
   */
  getCurrentTime() {
    if (!this.audioSource) return 0;
    return this.audioContext.currentTime - this.speechStartTime;
  }

  /**
   * Get audio duration
   */
  getDuration() {
    return this.audioBuffer?.duration || 0;
  }

  /**
   * Set phoneme update callback
   */
  setOnPhonemeUpdate(callback) {
    this.onPhonemeUpdate = callback;
  }

  /**
   * Set audio ready callback
   */
  setOnAudioReady(callback) {
    this.onAudioReady = callback;
  }

  /**
   * Set speech complete callback
   */
  setOnSpeechComplete(callback) {
    this.onSpeechComplete = callback;
  }

  /**
   * Dispose resources
   */
  dispose() {
    this.stopAudio();
    this.audioBuffer = null;
    this.audioSource = null;
    this.analyser = null;
    this.logger.log('Resources disposed');
  }
}

export default VoiceServiceIntegration;
