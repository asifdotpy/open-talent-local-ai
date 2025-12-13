/**
 * Transcription Service
 * Handles speech-to-text using Whisper model (local, no cloud)
 * Extracts phonemes for avatar lip-sync
 * Part of Day 5-6 implementation
 */

import { pipeline, env } from '@xenova/transformers';

export interface TranscriptionResult {
  text: string;
  confidence: number;
  language: string;
  duration: number;
  phonemeFrames: PhonemeFrame[];
  timestamps: TimestampFrame[];
}

export interface PhonemeFrame {
  time: number; // ms
  phoneme: string;
  intensity: number; // 0-1
}

export interface TimestampFrame {
  start: number; // seconds
  end: number;
  text: string;
}

export interface WhisperConfig {
  modelSize: 'tiny' | 'base' | 'small';
  language: string;
  taskType: 'transcribe' | 'translate';
}

// Configure transformers.js to use local cache
env.allowLocalModels = true;
env.allowRemoteModels = true;
env.cacheDir = '~/.cache/huggingface';

const DEFAULT_CONFIG: WhisperConfig = {
  modelSize: 'tiny', // Smallest model for speed
  language: 'en',
  taskType: 'transcribe',
};

// Phoneme mapping for English
const PHONEME_MAP: { [key: string]: string } = {
  'ae': 'a', 'ah': 'a', 'aa': 'a',
  'eh': 'e', 'ih': 'i',
  'oh': 'o', 'ao': 'o',
  'uh': 'u', 'uw': 'u',
  'er': 'r', 'ax': 'ə',
};

export class TranscriptionService {
  private transcriber: any = null;
  private isInitialized: boolean = false;
  private config: WhisperConfig = DEFAULT_CONFIG;
  private downloadProgress: number = 0;

  /**
   * Initialize Whisper model
   */
  async initialize(userConfig?: Partial<WhisperConfig>): Promise<void> {
    if (this.isInitialized) return;

    this.config = { ...DEFAULT_CONFIG, ...userConfig };

    try {
      const modelId = this.getModelId();
      
      console.log(`Loading ${modelId} model...`);

      // Load pipeline
      this.transcriber = await pipeline(
        'automatic-speech-recognition',
        modelId
      );

      this.isInitialized = true;
      this.downloadProgress = 100;
      console.log('✅ Whisper model initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Whisper:', error);
      throw error;
    }
  }

  /**
   * Get model ID based on size
   */
  private getModelId(): string {
    const modelMap = {
      tiny: 'Xenova/whisper-tiny',
      base: 'Xenova/whisper-base',
      small: 'Xenova/whisper-small',
    };
    return modelMap[this.config.modelSize];
  }

  /**
   * Transcribe audio blob to text with phonemes
   */
  async transcribe(audioBlob: Blob): Promise<TranscriptionResult> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      // Convert blob to array buffer
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioData = new Float32Array(arrayBuffer);

      const startTime = Date.now();

      // Run transcription
      const result = await this.transcriber(audioData, {
        language: this.config.language,
        task: this.config.taskType,
        return_timestamps: true,
      });

      const duration = (Date.now() - startTime) / 1000;

      // Extract text
      const text = result.text || '';

      // Extract timestamps
      const timestamps = this.extractTimestamps(result.chunks || []);

      // Extract phonemes
      const phonemeFrames = await this.extractPhonemes(text, result);

      return {
        text,
        confidence: result.confidence || 0.85,
        language: this.config.language,
        duration,
        phonemeFrames,
        timestamps,
      };
    } catch (error) {
      console.error('❌ Transcription failed:', error);
      throw error;
    }
  }

  /**
   * Extract phonemes from transcribed text
   */
  private async extractPhonemes(
    text: string,
    result: any
  ): Promise<PhonemeFrame[]> {
    const phonemeFrames: PhonemeFrame[] = [];

    // Simple phoneme extraction from text
    // In production, would use more sophisticated phonetic analysis
    const words = text.toLowerCase().split(/\s+/);
    let timeOffset = 0;

    for (const word of words) {
      const phonemes = this.textToPhonemes(word);
      const wordsPerSecond = 3; // Average speaking speed

      for (const phoneme of phonemes) {
        const intensity = this.getPhonemeIntensity(phoneme);
        phonemeFrames.push({
          time: timeOffset * 1000,
          phoneme,
          intensity,
        });
        timeOffset += 0.1; // 100ms per phoneme
      }

      timeOffset += 1 / wordsPerSecond;
    }

    return phonemeFrames;
  }

  /**
   * Convert word to phonemes (simplified)
   */
  private textToPhonemes(word: string): string[] {
    // Very simplified phoneme extraction
    // In production, use a proper phonetic library
    const vowels = ['a', 'e', 'i', 'o', 'u'];
    const phonemes: string[] = [];

    for (const char of word) {
      if (vowels.includes(char)) {
        phonemes.push(char);
      }
    }

    // If no vowels, return first letter
    if (phonemes.length === 0 && word.length > 0) {
      phonemes.push(word[0]);
    }

    return phonemes.length > 0 ? phonemes : ['ə']; // Schwa as default
  }

  /**
   * Get mouth openness for phoneme (0-1)
   */
  private getPhonemeIntensity(phoneme: string): number {
    // Map phonemes to mouth openness
    const intensityMap: { [key: string]: number } = {
      'a': 0.8, // Wide open
      'e': 0.4, // Smile
      'i': 0.3, // Narrow
      'o': 0.6, // Round open
      'u': 0.4, // Round closed
      'ə': 0.3, // Schwa (neutral)
      'r': 0.4,
      'm': 0.1, // Lips closed
      'p': 0.0, // Lips closed
      'b': 0.0, // Lips closed
    };

    return intensityMap[phoneme.toLowerCase()] || 0.3;
  }

  /**
   * Extract timestamps from result chunks
   */
  private extractTimestamps(chunks: any[]): TimestampFrame[] {
    if (!chunks || chunks.length === 0) {
      return [];
    }

    return chunks.map((chunk: any) => ({
      start: chunk.timestamp?.[0] || 0,
      end: chunk.timestamp?.[1] || 0,
      text: chunk.text || '',
    }));
  }

  /**
   * Check if service is initialized
   */
  isReady(): boolean {
    return this.isInitialized;
  }

  /**
   * Get model download progress (0-100)
   */
  getDownloadProgress(): number {
    return this.downloadProgress;
  }

  /**
   * Get model info
   */
  getModelInfo(): {
    modelId: string;
    modelSize: string;
    language: string;
  } {
    return {
      modelId: this.getModelId(),
      modelSize: this.config.modelSize,
      language: this.config.language,
    };
  }

  /**
   * Clear cached models
   */
  async clearCache(): Promise<void> {
    // In browser, cache is handled automatically
    // This is a placeholder for future cache management
    console.log('Cache management - implement in production');
  }

  /**
   * Dispose service
   */
  dispose(): void {
    this.transcriber = null;
    this.isInitialized = false;
    console.log('✅ Transcription service disposed');
  }
}

// Export singleton instance
export const transcriptionService = new TranscriptionService();
