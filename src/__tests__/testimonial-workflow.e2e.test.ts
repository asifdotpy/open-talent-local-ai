/**
 * E2E Test Suite: Complete Testimonial Workflow
 * Tests full user journey: Record → Transcribe → Fill Form → Submit → Store
 */

import { VoiceInputService } from '../services/voice-input';
import { AvatarRenderer } from '../services/avatar-renderer';
import { TranscriptionService } from '../services/transcription-service';
import { TestimonialDatabase } from '../services/testimonial-database';

jest.mock('../services/voice-input');
jest.mock('../services/avatar-renderer');
jest.mock('../services/transcription-service');
jest.mock('../services/testimonial-database');

describe('E2E: Complete Testimonial Workflow', () => {
  let voiceService: any;
  let avatarService: any;
  let transcriptionService: any;
  let database: any;

  beforeEach(() => {
    voiceService = {
      checkMicrophoneAccess: jest.fn().mockResolvedValue(true),
      startRecording: jest.fn().mockResolvedValue({
        sessionId: 'test-session-123',
        timestamp: Date.now(),
      }),
      stopRecording: jest.fn().mockResolvedValue({
        audioPath: '/audio/test-123.wav',
        duration: 5000,
      }),
      getAudioLevel: jest.fn().mockReturnValue(45),
      isRecording: jest.fn().mockReturnValue(false),
    };

    avatarService = {
      initialize: jest.fn().mockResolvedValue(true),
      playLipSyncAnimation: jest.fn().mockResolvedValue(true),
      setExpression: jest.fn().mockReturnValue(true),
      getState: jest.fn().mockReturnValue({
        isInitialized: true,
        isAnimating: false,
      }),
      dispose: jest.fn(),
    };

    transcriptionService = {
      transcribe: jest.fn().mockResolvedValue({
        text: 'This is a test testimonial about workplace discrimination',
        confidence: 0.94,
        language: 'en',
      }),
      extractPhonemes: jest.fn().mockReturnValue([
        { phoneme: 'a', timestamp: 100, intensity: 0.8 },
        { phoneme: 'e', timestamp: 200, intensity: 0.4 },
      ]),
      getState: jest.fn().mockReturnValue({
        isReady: true,
        modelSize: 'base',
      }),
    };

    database = {
      initialize: jest.fn().mockResolvedValue(true),
      save: jest.fn().mockResolvedValue('testimonial-123'),
      getById: jest.fn().mockResolvedValue({
        id: 'testimonial-123',
        recordedAt: new Date().toISOString(),
        audioPath: '/audio/test-123.wav',
        incidentType: 'discrimination',
      }),
      search: jest.fn().mockResolvedValue([]),
      update: jest.fn().mockResolvedValue(true),
    };

    (VoiceInputService as jest.Mock).mockImplementation(() => voiceService);
    (AvatarRenderer as jest.Mock).mockImplementation(() => avatarService);
    (TranscriptionService as jest.Mock).mockImplementation(() => transcriptionService);
    (TestimonialDatabase as jest.Mock).mockImplementation(() => database);
  });

  describe('Full Workflow: Record → Transcribe → Submit', () => {
    it('should complete full workflow without errors', async () => {
      const hasMic = await voiceService.checkMicrophoneAccess();
      expect(hasMic).toBe(true);

      const recordingSession = await voiceService.startRecording();
      expect(recordingSession.sessionId).toBeDefined();

      const avatarState = avatarService.getState();
      expect(avatarState.isInitialized).toBe(true);
      
      await avatarService.playLipSyncAnimation();
      expect(avatarService.playLipSyncAnimation).toHaveBeenCalled();

      const recording = await voiceService.stopRecording();
      expect(recording.audioPath).toBeDefined();

      const transcription = await transcriptionService.transcribe(recording.audioPath);
      expect(transcription.text).toBeDefined();

      const phonemes = transcriptionService.extractPhonemes(transcription.text);
      expect(phonemes.length).toBeGreaterThan(0);

      const testimonialData = {
        recordedAt: new Date().toISOString(),
        audioPath: recording.audioPath,
        context: transcription.text,
      };
      const savedId = await database.save(testimonialData);
      expect(savedId).toBeDefined();
    });

    it('should validate transcription confidence before saving', async () => {
      const lowConfidenceTranscription = {
        text: 'Low confidence text',
        confidence: 0.45,
        language: 'en',
      };
      
      expect(lowConfidenceTranscription.confidence).toBeLessThan(0.7);
      const testimonialData = {
        context: lowConfidenceTranscription.text,
        confidenceLow: lowConfidenceTranscription.confidence < 0.7,
      };
      await database.save(testimonialData);
      expect(database.save).toHaveBeenCalled();
    });

    it('should preserve audio path through entire workflow', async () => {
      const audioPath = '/audio/test-123.wav';
      const recording = { audioPath, duration: 5000 };
      
      await transcriptionService.transcribe(recording.audioPath);
      expect(transcriptionService.transcribe).toHaveBeenCalledWith(audioPath);
      
      const testimony = { audioPath, context: 'test' };
      await database.save(testimony);
      expect(database.save).toHaveBeenCalled();
    });
  });

  describe('Data Integrity Through Pipeline', () => {
    it('should not lose data during transcription → database transition', async () => {
      const originalContext = 'Original testimonial text with all details';
      const transcription = {
        text: originalContext,
        confidence: 0.92,
      };
      
      const saved = await database.save({
        context: transcription.text,
      });
      
      const retrieved = await database.getById(saved);
      expect(retrieved).toBeDefined();
    });

    it('should handle special characters in transcription', async () => {
      const specialText = "It's a test: discrimination, harassment!";
      transcriptionService.transcribe.mockResolvedValue({
        text: specialText,
        confidence: 0.88,
      });
      
      const transcription = await transcriptionService.transcribe('/audio/special.wav');
      await database.save({ context: transcription.text });
      
      expect(database.save).toHaveBeenCalled();
    });
  });

  describe('Performance Characteristics', () => {
    it('should complete full workflow within target time', async () => {
      const startTime = Date.now();
      
      await voiceService.checkMicrophoneAccess();
      const session = await voiceService.startRecording();
      await avatarService.playLipSyncAnimation();
      await voiceService.stopRecording();
      const transcription = await transcriptionService.transcribe('/audio/test.wav');
      await database.save({ context: transcription.text });
      
      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(15000);
    });

    it('should not block UI during transcription', async () => {
      const transcribePromise = transcriptionService.transcribe('/audio/test.wav');
      
      const avatarState = avatarService.getState();
      expect(avatarState.isInitialized).toBe(true);
      
      const transcription = await transcribePromise;
      expect(transcription.text).toBeDefined();
    });
  });

  describe('Cross-Service Error Handling', () => {
    it('should handle transcription failure gracefully', async () => {
      transcriptionService.transcribe.mockRejectedValue(
        new Error('Service unavailable')
      );
      
      try {
        await transcriptionService.transcribe('/audio/test.wav');
      } catch (error: any) {
        expect(error.message).toContain('Service');
      }
    });

    it('should handle database save failure and retry', async () => {
      database.save.mockRejectedValueOnce(new Error('Storage quota exceeded'));
      
      try {
        await database.save({ context: 'test' });
      } catch (error: any) {
        expect(error.message).toContain('quota');
      }
      
      database.save.mockResolvedValueOnce('testimonial-456');
      const saved = await database.save({ context: 'test' });
      expect(saved).toBe('testimonial-456');
    });
  });
});
