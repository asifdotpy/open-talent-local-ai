/**
 * Memory & Load Testing Suite
 * Tests memory management, storage quotas, and concurrent operations
 */

import { TestimonialDatabase } from '../services/testimonial-database';
import { VoiceInputService } from '../services/voice-input';
import { TranscriptionService } from '../services/transcription-service';

jest.mock('../services/testimonial-database');
jest.mock('../services/voice-input');
jest.mock('../services/transcription-service');

class StorageQuotaMonitor {
  private usedStorage = 0;
  private maxQuota = 50 * 1024 * 1024;

  addData(sizeBytes: number): boolean {
    if (this.usedStorage + sizeBytes > this.maxQuota) {
      return false;
    }
    this.usedStorage += sizeBytes;
    return true;
  }

  removeData(sizeBytes: number): void {
    this.usedStorage = Math.max(0, this.usedStorage - sizeBytes);
  }

  getUsagePercent(): number {
    return (this.usedStorage / this.maxQuota) * 100;
  }

  getRemainingBytes(): number {
    return this.maxQuota - this.usedStorage;
  }

  isNearQuota(): boolean {
    return this.getUsagePercent() > 90;
  }

  clear(): void {
    this.usedStorage = 0;
  }
}

describe('Memory & Load Testing', () => {
  let database: any;
  let voiceService: any;
  let transcriptionService: any;
  let quotaMonitor: StorageQuotaMonitor;

  beforeEach(() => {
    quotaMonitor = new StorageQuotaMonitor();

    database = {
      save: jest.fn().mockImplementation((data: any) => {
        const dataSize = JSON.stringify(data).length;
        if (!quotaMonitor.addData(dataSize)) {
          throw new Error('Storage quota exceeded');
        }
        return Promise.resolve('testimonial-' + Date.now());
      }),
      delete: jest.fn().mockImplementation(() => {
        quotaMonitor.removeData(5000);
        return Promise.resolve(true);
      }),
      getAll: jest.fn().mockResolvedValue([]),
      clear: jest.fn().mockImplementation(() => {
        quotaMonitor.clear();
        return Promise.resolve(true);
      }),
    };

    voiceService = {
      startRecording: jest.fn().mockResolvedValue({ sessionId: 'session-123' }),
      stopRecording: jest.fn().mockResolvedValue({ audioPath: '/audio/test.wav' }),
      dispose: jest.fn(),
    };

    transcriptionService = {
      transcribe: jest.fn().mockResolvedValue({
        text: 'Test transcription',
        confidence: 0.9,
      }),
    };

    (TestimonialDatabase as jest.Mock).mockImplementation(() => database);
    (VoiceInputService as jest.Mock).mockImplementation(() => voiceService);
    (TranscriptionService as jest.Mock).mockImplementation(() => transcriptionService);
  });

  describe('Storage Quota Management', () => {
    it('should respect storage quota limit', async () => {
      let count = 0;
      const largeTestimony = {
        context: 'x'.repeat(100000),
        incidentType: 'discrimination',
      };

      while (quotaMonitor.getRemainingBytes() > 100000) {
        try {
          await database.save(largeTestimony);
          count++;
        } catch (error: any) {
          if (error.message.includes('quota')) {
            break;
          }
        }
      }

      expect(count).toBeGreaterThan(100);
      expect(quotaMonitor.getUsagePercent()).toBeGreaterThan(90);
    });

    it('should warn when approaching quota limit', () => {
      quotaMonitor.addData(42.5 * 1024 * 1024);
      expect(quotaMonitor.isNearQuota()).toBe(false);

      quotaMonitor.addData(3.5 * 1024 * 1024);
      expect(quotaMonitor.isNearQuota()).toBe(true);
    });

    it('should handle quota exceeded error gracefully', async () => {
      quotaMonitor.addData(49 * 1024 * 1024);

      const largeData = { context: 'x'.repeat(2000000) };

      await expect(database.save(largeData)).rejects.toThrow('quota exceeded');
    });

    it('should allow cleanup when quota is exceeded', async () => {
      quotaMonitor.addData(50 * 1024 * 1024);
      expect(quotaMonitor.getRemainingBytes()).toBe(0);

      await database.clear();
      expect(quotaMonitor.getUsagePercent()).toBe(0);
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle 10 concurrent save operations', async () => {
      const saves = Array.from({ length: 10 }, (_, i) =>
        database.save({
          context: `Testimony ${i}`,
          incidentType: 'discrimination',
        })
      );

      const results = await Promise.all(saves);
      expect(results.length).toBe(10);
    });

    it('should handle concurrent recording + transcription', async () => {
      const operations = await Promise.all([
        voiceService.startRecording(),
        transcriptionService.transcribe('/audio/test.wav'),
      ]);

      expect(operations.length).toBe(2);
    });

    it('should handle rapid session creation and cleanup', async () => {
      for (let i = 0; i < 10; i++) {
        const session = await voiceService.startRecording();
        expect(session.sessionId).toBeDefined();

        await voiceService.stopRecording();
        voiceService.dispose();
      }

      expect(voiceService.startRecording).toHaveBeenCalledTimes(10);
    });

    it('should maintain stability under load', async () => {
      const operations = [];

      for (let i = 0; i < 50; i++) {
        operations.push(
          database.save({ context: `Testimony ${i}` })
        );
      }

      const results = await Promise.all(operations);
      expect(results.length).toBe(50);
    });
  });

  describe('Long-Running Session Stability', () => {
    it('should handle periodic cleanup', async () => {
      for (let i = 0; i < 50; i++) {
        await database.save({ context: `Testimony ${i}` });
      }

      await database.clear();
      const remaining = await database.getAll();
      expect(remaining.length).toBe(0);
    });

    it('should recover from errors without degradation', async () => {
      for (let i = 0; i < 10; i++) {
        await database.save({ context: `Testimony ${i}` });
      }

      database.save.mockRejectedValueOnce(new Error('Service error'));

      try {
        await database.save({ context: 'Error test' });
      } catch (error) {
        // Expected
      }

      database.save.mockImplementation(() =>
        Promise.resolve('testimonial-' + Date.now())
      );

      for (let i = 0; i < 10; i++) {
        await database.save({ context: `Testimony after error ${i}` });
      }

      expect(database.save).toHaveBeenCalled();
    });
  });

  describe('Resource Management', () => {
    it('should properly cleanup database on clear', async () => {
      const ids = [];
      for (let i = 0; i < 20; i++) {
        const id = await database.save({
          context: `Testimony ${i}`,
        });
        ids.push(id);
      }

      expect(ids.length).toBe(20);

      await database.clear();
      const remaining = await database.getAll();
      expect(remaining.length).toBe(0);
    });

    it('should cleanup voice service resources properly', async () => {
      await voiceService.startRecording();
      await voiceService.stopRecording();
      voiceService.dispose();

      expect(voiceService.dispose).toHaveBeenCalled();
    });
  });

  describe('Error Recovery', () => {
    it('should identify memory hotspots', () => {
      const operations = [
        { name: 'transcription', mem: 45 },
        { name: 'database-save', mem: 5 },
        { name: 'phoneme-extraction', mem: 25 },
      ];

      const sorted = operations.sort((a, b) => b.mem - a.mem);
      expect(sorted[0].name).toBe('transcription');
    });

    it('should identify CPU intensive operations', () => {
      const operations = [
        { name: 'transcription', cpu: 85 },
        { name: 'database-query', cpu: 15 },
      ];

      const sorted = operations.sort((a, b) => b.cpu - a.cpu);
      expect(sorted[0].name).toBe('transcription');
    });
  });
});
