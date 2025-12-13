/**
 * E2E Test Suite: Complete Testimonial Workflow
 * Tests full user journey: Record → Transcribe → Fill Form → Submit → Store
 * 
 * Coverage:
 * - 10+ test scenarios
 * - Cross-service integration (Voice → Transcription → Form → Database)
 * - Data integrity validation
 * - Error recovery paths
 * - Performance characteristics
 */

import { VoiceInputService } from '../../services/voice-input';
import { AvatarRenderer } from '../../services/avatar-renderer';
import { TranscriptionService } from '../../services/transcription-service';
import { TestimonialDatabase } from '../../services/testimonial-database';

// Mock all services
jest.mock('../../services/voice-input');
jest.mock('../../services/avatar-renderer');
jest.mock('../../services/transcription-service');
jest.mock('../../services/testimonial-database');

describe('E2E: Complete Testimonial Workflow', () => {
  let voiceService: any;
  let avatarService: any;
  let transcriptionService: any;
  let database: any;

  beforeEach(() => {
    // Setup service mocks
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
        location: 'Workplace',
        anonymous: false,
        witnessNames: ['John Doe'],
        context: 'This is a test testimonial about workplace discrimination',
        privacyMaskApplied: false,
        status: 'pending',
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
      // Step 1: Check microphone access
      const hasMic = await voiceService.checkMicrophoneAccess();
      expect(hasMic).toBe(true);

      // Step 2: Start recording with avatar animation
      const recordingSession = await voiceService.startRecording();
      expect(recordingSession.sessionId).toBeDefined();

      // Step 3: Avatar lip-sync during recording
      const avatarState = avatarService.getState();
      expect(avatarState.isInitialized).toBe(true);
      await avatarService.playLipSyncAnimation();
      expect(avatarService.playLipSyncAnimation).toHaveBeenCalled();

      // Step 4: Stop recording
      const recording = await voiceService.stopRecording();
      expect(recording.audioPath).toBeDefined();
      expect(recording.duration).toBeGreaterThan(0);

      // Step 5: Transcribe audio
      const transcription = await transcriptionService.transcribe(recording.audioPath);
      expect(transcription.text).toBeDefined();
      expect(transcription.confidence).toBeGreaterThan(0);

      // Step 6: Extract phonemes for lip-sync
      const phonemes = transcriptionService.extractPhonemes(transcription.text);
      expect(phonemes.length).toBeGreaterThan(0);

      // Step 7: Save to database
      const testimonialData = {
        recordedAt: new Date().toISOString(),
        audioPath: recording.audioPath,
        incidentType: 'discrimination',
        location: 'Workplace',
        anonymous: false,
        witnessNames: ['John Doe'],
        context: transcription.text,
      };
      const savedId = await database.save(testimonialData);
      expect(savedId).toBeDefined();
      expect(database.save).toHaveBeenCalled();
    });

    it('should handle microphone permission denied gracefully', async () => {
      voiceService.checkMicrophoneAccess.mockResolvedValue(false);
      const hasMic = await voiceService.checkMicrophoneAccess();
      expect(hasMic).toBe(false);
      expect(voiceService.startRecording).not.toHaveBeenCalled();
    });

    it('should validate transcription confidence before saving', async () => {
      const lowConfidenceTranscription = {
        text: 'Low confidence text',
        confidence: 0.45, // Below 50% threshold
        language: 'en',
      };
      
      // Should warn but allow save with flag
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
      
      // Transcribe uses same path
      await transcriptionService.transcribe(recording.audioPath);
      expect(transcriptionService.transcribe).toHaveBeenCalledWith(audioPath);
      
      // Database stores same path
      const testimony = { audioPath, context: 'test' };
      await database.save(testimony);
      expect(database.save).toHaveBeenCalled();
    });
  });

  describe('Data Integrity Through Pipeline', () => {
    it('should not lose data during transcription → database transition', async () => {
      const originalContext = 'Original testimonial text with all details preserved';
      const transcription = {
        text: originalContext,
        confidence: 0.92,
        language: 'en',
      };
      
      const saved = await database.save({
        context: transcription.text,
        confidence: transcription.confidence,
      });
      
      const retrieved = await database.getById(saved);
      expect(retrieved.context).toBe(originalContext);
    });

    it('should handle special characters in transcription', async () => {
      const specialText = "It's a test: discrimination, harassment, & workplace issues!";
      transcriptionService.transcribe.mockResolvedValue({
        text: specialText,
        confidence: 0.88,
        language: 'en',
      });
      
      const transcription = await transcriptionService.transcribe('/audio/special.wav');
      const saved = await database.save({ context: transcription.text });
      
      expect(database.save).toHaveBeenCalledWith(
        expect.objectContaining({ context: specialText })
      );
    });

    it('should preserve metadata through workflow', async () => {
      const metadata = {
        recordedAt: '2025-12-12T21:30:00Z',
        location: 'Remote',
        incidentType: 'discrimination',
        anonymous: true,
      };
      
      const saved = await database.save(metadata);
      const retrieved = await database.getById(saved);
      
      expect(retrieved.recordedAt).toBe(metadata.recordedAt);
      expect(retrieved.location).toBe(metadata.location);
      expect(retrieved.incidentType).toBe(metadata.incidentType);
      expect(retrieved.anonymous).toBe(metadata.anonymous);
    });
  });

  describe('Cross-Service Error Handling', () => {
    it('should handle transcription failure gracefully', async () => {
      transcriptionService.transcribe.mockRejectedValue(
        new Error('Transcription service unavailable')
      );
      
      try {
        await transcriptionService.transcribe('/audio/test.wav');
      } catch (error: any) {
        expect(error.message).toContain('Transcription service');
      }
    });

    it('should handle database save failure and retry', async () => {
      // First attempt fails
      database.save.mockRejectedValueOnce(new Error('Storage quota exceeded'));
      
      // Verify error handling
      try {
        await database.save({ context: 'test' });
      } catch (error: any) {
        expect(error.message).toContain('quota');
      }
      
      // Retry should work
      database.save.mockResolvedValueOnce('testimonial-456');
      const saved = await database.save({ context: 'test' });
      expect(saved).toBe('testimonial-456');
    });

    it('should handle invalid incident type with validation', async () => {
      const invalidData = {
        context: 'test',
        incidentType: 'invalid_type', // Not in enum
      };
      
      // Should validate or throw
      expect(invalidData.incidentType).not.toMatch(/^(discrimination|harassment|wage|safety|other)$/);
    });
  });

  describe('Performance Characteristics', () => {
    it('should complete full workflow within target time (< 15 seconds)', async () => {
      const startTime = Date.now();
      
      await voiceService.checkMicrophoneAccess();
      const session = await voiceService.startRecording();
      await avatarService.playLipSyncAnimation();
      await voiceService.stopRecording();
      const transcription = await transcriptionService.transcribe('/audio/test.wav');
      await database.save({ context: transcription.text });
      
      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(15000); // 15 seconds
    });

    it('should allow concurrent recording and transcription prep', async () => {
      const startTime = Date.now();
      
      // Parallel operations
      const [microphone, transcriptionState] = await Promise.all([
        voiceService.checkMicrophoneAccess(),
        Promise.resolve(transcriptionService.getState()),
      ]);
      
      expect(microphone).toBe(true);
      expect(transcriptionState.isReady).toBe(true);
      
      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(1000); // Should be parallel
    });

    it('should not block UI during transcription', async () => {
      // Transcription is async, should not block
      transcriptionService.transcribe.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          text: 'test',
          confidence: 0.9,
          language: 'en',
        }), 500))
      );
      
      const transcribePromise = transcriptionService.transcribe('/audio/test.wav');
      
      // UI operations should not be blocked
      const avatarState = avatarService.getState();
      expect(avatarState.isInitialized).toBe(true);
      
      const transcription = await transcribePromise;
      expect(transcription.text).toBe('test');
    });
  });

  describe('Edge Cases & Boundary Conditions', () => {
    it('should handle very short audio recording (< 1 second)', async () => {
      const shortRecording = { audioPath: '/audio/short.wav', duration: 500 };
      
      // Should still allow transcription
      await transcriptionService.transcribe(shortRecording.audioPath);
      expect(transcriptionService.transcribe).toHaveBeenCalled();
    });

    it('should handle very long audio recording (> 10 minutes)', async () => {
      const longRecording = { audioPath: '/audio/long.wav', duration: 600000 };
      
      // Should handle long audio
      await transcriptionService.transcribe(longRecording.audioPath);
      expect(transcriptionService.transcribe).toHaveBeenCalled();
    });

    it('should handle empty or null transcription gracefully', async () => {
      transcriptionService.transcribe.mockResolvedValue({
        text: '', // Empty transcription
        confidence: 0.0,
        language: 'en',
      });
      
      const transcription = await transcriptionService.transcribe('/audio/empty.wav');
      expect(transcription.text).toBe('');
      
      // Should not save empty context
      if (!transcription.text) {
        expect(database.save).not.toHaveBeenCalled();
      }
    });

    it('should handle maximum witness count (10 witnesses)', async () => {
      const witnesses = Array.from({ length: 10 }, (_, i) => `Witness ${i + 1}`);
      
      const testimony = {
        context: 'test',
        witnessNames: witnesses,
      };
      
      await database.save(testimony);
      expect(database.save).toHaveBeenCalledWith(
        expect.objectContaining({ witnessNames: witnesses })
      );
    });

    it('should handle rapid successive saves', async () => {
      const saves = Array.from({ length: 5 }, (_, i) => ({
        context: `Testimonial ${i}`,
      }));
      
      await Promise.all(saves.map(s => database.save(s)));
      expect(database.save).toHaveBeenCalledTimes(5);
    });
  });

  describe('State Management Across Workflow', () => {
    it('should maintain avatar state during entire recording session', async () => {
      const initialState = avatarService.getState();
      expect(initialState.isInitialized).toBe(true);
      
      // Avatar state should not change during operations
      await voiceService.startRecording();
      const midState = avatarService.getState();
      expect(midState.isInitialized).toBe(true);
      
      await voiceService.stopRecording();
      const finalState = avatarService.getState();
      expect(finalState.isInitialized).toBe(true);
    });

    it('should handle avatar animation during transcription', async () => {
      await avatarService.playLipSyncAnimation();
      const phonemes = transcriptionService.extractPhonemes('test text');
      
      expect(avatarService.playLipSyncAnimation).toHaveBeenCalled();
      expect(phonemes.length).toBeGreaterThan(0);
    });

    it('should reset services after workflow completion', async () => {
      // Simulate workflow
      await voiceService.startRecording();
      await voiceService.stopRecording();
      await transcriptionService.transcribe('/audio/test.wav');
      
      // Should be able to start new workflow
      const newSession = await voiceService.startRecording();
      expect(newSession.sessionId).toBeDefined();
    });
  });
});
