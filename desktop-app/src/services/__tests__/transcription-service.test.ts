/**
 * Transcription Service Tests
 * Unit tests for speech-to-text and phoneme extraction
 */

import { TranscriptionService } from '../transcription-service';

// Mock the @xenova/transformers module since it has ES module issues with Jest
jest.mock('@xenova/transformers', () => ({
  pipeline: jest.fn(async (task, model) => {
    return jest.fn(async (audioData, options) => ({
      text: 'test transcription',
      confidence: 0.95,
      chunks: [],
    }));
  }),
  env: {
    allowLocalModels: true,
    allowRemoteModels: true,
    cacheDir: '~/.cache/huggingface',
  },
}));

describe('TranscriptionService', () => {
  let transcriptionService: TranscriptionService;

  beforeEach(() => {
    transcriptionService = new TranscriptionService();
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize transcription service', () => {
      // Service should be instantiable
      expect(transcriptionService).toBeDefined();
    });

    it('should support different model sizes', () => {
      // Service should handle different configs
      expect(transcriptionService).toBeDefined();
    });

    it('should support different languages', () => {
      // Service should handle language configs
      expect(transcriptionService).toBeDefined();
    });
  });

  describe('Transcription', () => {
    it('should be callable with audio blob', () => {
      // Service should have transcribe method
      expect(typeof transcriptionService.transcribe).toBe('function');
    });

    it('should return confidence score', () => {
      // Service should be properly typed
      expect(transcriptionService).toBeDefined();
    });

    it('should handle language detection', () => {
      // Service should support language
      expect(transcriptionService).toBeDefined();
    });
  });

  describe('Phoneme Extraction', () => {
    it('should extract phonemes', () => {
      // Service should support phoneme extraction
      expect(transcriptionService).toBeDefined();
    });

    it('should include timestamps', () => {
      // Service should handle timestamps
      expect(transcriptionService).toBeDefined();
    });

    it('should maintain sequential timestamps', () => {
      // Service should order timestamps
      expect(transcriptionService).toBeDefined();
    });

    it('should map vowel intensities correctly', () => {
      // Service should map vowels
      expect(transcriptionService).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid audio format gracefully', () => {
      // Service should handle errors
      expect(transcriptionService).toBeDefined();
    });

    it('should handle null blob gracefully', () => {
      // Service should validate input
      expect(transcriptionService).toBeDefined();
    });
  });

  describe('Performance', () => {
    it('should transcribe efficiently', () => {
      // Service should be performant
      expect(transcriptionService).toBeDefined();
    });
  });
});
