/**
 * Voice Input Service Tests
 * Unit tests for microphone capture and recording
 */

import { VoiceInputService, VoiceInputConfig } from '../voice-input';

describe('VoiceInputService', () => {
  let voiceInputService: VoiceInputService;

  beforeEach(() => {
    voiceInputService = new VoiceInputService();
    jest.clearAllMocks();
  });

  describe('Microphone Access', () => {
    it('should check microphone permission status', async () => {
      const result = await voiceInputService.checkMicrophoneAccess();
      expect(result).toHaveProperty('available');
      expect(result).toHaveProperty('permitted');
      expect(typeof result.available).toBe('boolean');
      expect(typeof result.permitted).toBe('boolean');
    });

    it('should handle microphone requests', async () => {
      const result = await voiceInputService.requestMicrophoneAccess();
      expect(typeof result).toBe('boolean');
    });
  });

  describe('Recording', () => {
    it('should get audio level during recording', async () => {
      const level = voiceInputService.getAudioLevel();
      expect(typeof level).toBe('number');
      expect(level).toBeGreaterThanOrEqual(0);
      expect(level).toBeLessThanOrEqual(100);
    });

    it('should get waveform data', () => {
      const waveform = voiceInputService.getWaveformData();
      expect(Array.isArray(waveform)).toBe(true);
    });

    it('should check recording state', () => {
      const isRecording = voiceInputService.isRecording();
      expect(typeof isRecording).toBe('boolean');
    });
  });

  describe('Session Management', () => {
    it('should have dispose method', () => {
      expect(() => {
        voiceInputService.dispose();
      }).not.toThrow();
    });
  });
});
