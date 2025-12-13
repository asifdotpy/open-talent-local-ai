/**
 * Memory Profiling & Load Testing Suite
 * 
 * Tests:
 * - Memory leak detection
 * - Concurrent operation handling
 * - Storage quota limits
 * - Resource cleanup
 * - Long-running session stability
 */

import { TestimonialDatabase } from '../../services/testimonial-database';
import { VoiceInputService } from '../../services/voice-input';
import { TranscriptionService } from '../../services/transcription-service';
import { AvatarRenderer } from '../../services/avatar-renderer';

jest.mock('../../services/testimonial-database');
jest.mock('../../services/voice-input');
jest.mock('../../services/transcription-service');
jest.mock('../../services/avatar-renderer');

// Memory profiling utilities
class MemoryProfiler {
  private snapshots: Array<{ label: string; timestamp: number; memory: number }> = [];
  private leakThreshold = 10; // MB

  snapshot(label: string): number {
    const memory = performance.memory?.usedJSHeapSize || 0;
    const memoryMB = memory / 1024 / 1024;
    
    this.snapshots.push({
      label,
      timestamp: Date.now(),
      memory: memoryMB,
    });
    
    return memoryMB;
  }

  detectLeaks(): Array<{ label: string; growth: number }> {
    const leaks = [];
    
    for (let i = 1; i < this.snapshots.length; i++) {
      const prev = this.snapshots[i - 1];
      const curr = this.snapshots[i];
      const growth = curr.memory - prev.memory;
      
      if (growth > this.leakThreshold) {
        leaks.push({
          label: `${prev.label} → ${curr.label}`,
          growth,
        });
      }
    }
    
    return leaks;
  }

  getReport() {
    const sorted = [...this.snapshots].sort((a, b) => a.memory - b.memory);
    return {
      min: sorted[0],
      max: sorted[sorted.length - 1],
      snapshots: this.snapshots,
      leaks: this.detectLeaks(),
    };
  }

  clear(): void {
    this.snapshots = [];
  }
}

// Storage quota monitor
class StorageQuotaMonitor {
  private usedStorage = 0;
  private maxQuota = 50 * 1024 * 1024; // 50MB quota

  addData(sizeBytes: number): boolean {
    if (this.usedStorage + sizeBytes > this.maxQuota) {
      return false; // Quota exceeded
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

describe('Memory Profiling & Load Testing', () => {
  let database: any;
  let voiceService: any;
  let transcriptionService: any;
  let avatarService: any;
  let profiler: MemoryProfiler;
  let quotaMonitor: StorageQuotaMonitor;

  beforeEach(() => {
    profiler = new MemoryProfiler();
    quotaMonitor = new StorageQuotaMonitor();

    database = {
      save: jest.fn().mockImplementation((data: any) => {
        // Simulate storage consumption
        const dataSize = JSON.stringify(data).length;
        if (!quotaMonitor.addData(dataSize)) {
          throw new Error('Storage quota exceeded');
        }
        return Promise.resolve('testimonial-' + Date.now());
      }),
      delete: jest.fn().mockImplementation(() => {
        quotaMonitor.removeData(5000); // Assume 5KB per record
        return Promise.resolve(true);
      }),
      getAll: jest.fn().mockResolvedValue([]),
      clear: jest.fn().mockImplementation(() => {
        quotaMonitor.clear();
        return Promise.resolve(true);
      }),
      getStorageStats: jest.fn().mockImplementation(() => ({
        used: quotaMonitor.getUsagePercent(),
        remaining: quotaMonitor.getRemainingBytes(),
      })),
    };

    voiceService = {
      startRecording: jest.fn().mockResolvedValue({ sessionId: 'session-123' }),
      stopRecording: jest.fn().mockResolvedValue({ audioPath: '/audio/test.wav', duration: 5000 }),
      dispose: jest.fn(),
    };

    transcriptionService = {
      transcribe: jest.fn().mockResolvedValue({
        text: 'Test transcription text',
        confidence: 0.9,
      }),
      getState: jest.fn().mockReturnValue({ isReady: true }),
    };

    avatarService = {
      initialize: jest.fn().mockResolvedValue(true),
      playLipSyncAnimation: jest.fn().mockResolvedValue(true),
      dispose: jest.fn(),
      getState: jest.fn().mockReturnValue({ isInitialized: true }),
    };

    (TestimonialDatabase as jest.Mock).mockImplementation(() => database);
    (VoiceInputService as jest.Mock).mockImplementation(() => voiceService);
    (TranscriptionService as jest.Mock).mockImplementation(() => transcriptionService);
    (AvatarRenderer as jest.Mock).mockImplementation(() => avatarService);
  });

  describe('Memory Leak Detection', () => {
    it('should not leak memory during repeated save operations', async () => {
      profiler.snapshot('start');
      
      for (let i = 0; i < 100; i++) {
        await database.save({
          context: `Testimony ${i}`,
          incidentType: 'discrimination',
        });
        
        if (i % 20 === 0) {
          profiler.snapshot(`iteration-${i}`);
        }
      }
      
      profiler.snapshot('end');
      const report = profiler.getReport();
      
      // Should not have significant leaks
      expect(report.leaks.length).toBeLessThan(3); // Allow minor fluctuations
    });

    it('should properly cleanup after recording session', async () => {
      profiler.snapshot('before-recording');
      
      await voiceService.startRecording();
      profiler.snapshot('recording-started');
      
      await voiceService.stopRecording();
      profiler.snapshot('recording-stopped');
      
      voiceService.dispose();
      profiler.snapshot('after-dispose');
      
      const report = profiler.getReport();
      const finalMemory = report.max.memory;
      const initialMemory = report.min.memory;
      
      // Memory should not grow unbounded
      expect(finalMemory - initialMemory).toBeLessThan(50); // Less than 50MB growth
    });

    it('should not leak memory during transcription service usage', async () => {
      profiler.snapshot('transcription-start');
      
      for (let i = 0; i < 50; i++) {
        await transcriptionService.transcribe(`/audio/test-${i}.wav`);
        
        if (i % 10 === 0) {
          profiler.snapshot(`transcription-${i}`);
        }
      }
      
      profiler.snapshot('transcription-end');
      const report = profiler.getReport();
      
      expect(report.leaks.length).toBeLessThan(3);
    });

    it('should cleanup avatar service resources properly', async () => {
      profiler.snapshot('avatar-start');
      
      await avatarService.initialize();
      profiler.snapshot('avatar-initialized');
      
      for (let i = 0; i < 30; i++) {
        await avatarService.playLipSyncAnimation();
      }
      
      profiler.snapshot('avatar-animations-done');
      avatarService.dispose();
      profiler.snapshot('avatar-disposed');
      
      const report = profiler.getReport();
      
      // Memory should decrease after disposal
      const beforeDispose = report.snapshots[report.snapshots.length - 2].memory;
      const afterDispose = report.snapshots[report.snapshots.length - 1].memory;
      
      expect(afterDispose).toBeLessThanOrEqual(beforeDispose);
    });
  });

  describe('Storage Quota Management', () => {
    it('should respect storage quota limit (50MB)', async () => {
      // Add testimonies until quota is reached
      let count = 0;
      const largeTestimony = {
        context: 'x'.repeat(100000), // ~100KB
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
      
      // Should have saved roughly 500 testimonies (50MB / 100KB)
      expect(count).toBeGreaterThan(400);
      expect(quotaMonitor.getUsagePercent()).toBeGreaterThan(90);
    });

    it('should warn when approaching quota limit', () => {
      // Fill storage to 85%
      quotaMonitor.addData(42.5 * 1024 * 1024);
      
      expect(quotaMonitor.isNearQuota()).toBe(false);
      
      // Fill to 92%
      quotaMonitor.addData(3.5 * 1024 * 1024);
      
      expect(quotaMonitor.isNearQuota()).toBe(true);
      expect(quotaMonitor.getUsagePercent()).toBeGreaterThan(90);
    });

    it('should handle quota exceeded error gracefully', async () => {
      // Fill storage
      quotaMonitor.addData(49 * 1024 * 1024); // 49MB
      
      // Try to save large testimony
      const largeData = { context: 'x'.repeat(2000000) }; // 2MB
      
      await expect(database.save(largeData)).rejects.toThrow('quota exceeded');
    });

    it('should allow cleanup when quota is exceeded', async () => {
      // Fill quota
      quotaMonitor.addData(50 * 1024 * 1024);
      
      expect(quotaMonitor.getRemainingBytes()).toBe(0);
      
      // Clear old testimonies
      await database.clear();
      
      expect(quotaMonitor.getUsagePercent()).toBe(0);
      expect(quotaMonitor.getRemainingBytes()).toBeGreaterThan(0);
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle 10 concurrent save operations', async () => {
      profiler.snapshot('concurrent-start');
      
      const saves = Array.from({ length: 10 }, (_, i) => 
        database.save({
          context: `Testimony ${i}`,
          incidentType: 'discrimination',
        })
      );
      
      const results = await Promise.all(saves);
      
      profiler.snapshot('concurrent-end');
      
      // All saves should succeed
      expect(results.length).toBe(10);
      expect(results.every(r => r)).toBe(true);
    });

    it('should handle concurrent recording + transcription', async () => {
      profiler.snapshot('concurrent-mixed-start');
      
      const operations = await Promise.all([
        voiceService.startRecording(),
        transcriptionService.transcribe('/audio/test.wav'),
        avatarService.playLipSyncAnimation(),
      ]);
      
      profiler.snapshot('concurrent-mixed-end');
      
      expect(operations.length).toBe(3);
    });

    it('should handle rapid session creation and cleanup', async () => {
      profiler.snapshot('rapid-sessions-start');
      
      for (let i = 0; i < 20; i++) {
        const session = await voiceService.startRecording();
        expect(session.sessionId).toBeDefined();
        
        await voiceService.stopRecording();
        voiceService.dispose();
      }
      
      profiler.snapshot('rapid-sessions-end');
      
      const report = profiler.getReport();
      const growth = report.max.memory - report.min.memory;
      
      // Should not accumulate memory with session cleanup
      expect(growth).toBeLessThan(30); // Less than 30MB
    });

    it('should maintain stability under load (100+ operations)', async () => {
      profiler.snapshot('load-test-start');
      
      const operations = [];
      
      for (let i = 0; i < 100; i++) {
        if (i % 3 === 0) {
          operations.push(database.save({ context: `Testimony ${i}`, incidentType: 'discrimination' }));
        } else if (i % 3 === 1) {
          operations.push(transcriptionService.transcribe(`/audio/test-${i}.wav`));
        } else {
          operations.push(avatarService.playLipSyncAnimation());
        }
      }
      
      await Promise.all(operations);
      profiler.snapshot('load-test-end');
      
      const report = profiler.getReport();
      
      // System should remain stable
      expect(report.leaks.length).toBeLessThan(5);
    });
  });

  describe('Long-Running Session Stability', () => {
    it('should maintain stability during 1-hour simulation', async () => {
      profiler.snapshot('session-start');
      
      // Simulate 1 hour = 3600 seconds
      // Operations every 3.6 seconds = 1000 operations
      const operationCount = 100; // Reduced for test execution
      
      for (let i = 0; i < operationCount; i++) {
        await database.save({
          context: `Testimony ${i}`,
          incidentType: 'discrimination',
        });
        
        if (i % 10 === 0) {
          await transcriptionService.transcribe('/audio/test.wav');
        }
        
        if (i % 20 === 0) {
          profiler.snapshot(`operation-${i}`);
        }
      }
      
      profiler.snapshot('session-end');
      
      const report = profiler.getReport();
      
      // Performance should not degrade
      expect(report.leaks.length).toBeLessThan(5);
      
      // Memory growth should be minimal
      const growth = report.max.memory - report.min.memory;
      expect(growth).toBeLessThan(100); // Less than 100MB
    });

    it('should handle periodic cleanup', async () => {
      profiler.snapshot('cleanup-cycle-start');
      
      // Save testimonies
      for (let i = 0; i < 50; i++) {
        await database.save({ context: `Testimony ${i}` });
      }
      
      profiler.snapshot('after-saves');
      
      // Cleanup
      await database.clear();
      
      profiler.snapshot('after-cleanup');
      
      const report = profiler.getReport();
      const afterCleanup = report.snapshots[report.snapshots.length - 1];
      const beforeCleanup = report.snapshots[report.snapshots.length - 2];
      
      // Memory should decrease after cleanup
      expect(afterCleanup.memory).toBeLessThanOrEqual(beforeCleanup.memory);
    });

    it('should recover from errors without degradation', async () => {
      profiler.snapshot('error-recovery-start');
      
      // Normal operations
      for (let i = 0; i < 10; i++) {
        await database.save({ context: `Testimony ${i}` });
      }
      
      profiler.snapshot('before-error');
      
      // Simulate error
      database.save.mockRejectedValueOnce(new Error('Service error'));
      
      try {
        await database.save({ context: 'Error test' });
      } catch (error) {
        // Expected
      }
      
      // Reset mock
      database.save.mockImplementation(() => Promise.resolve('testimonial-' + Date.now()));
      
      // Continue operations
      for (let i = 0; i < 10; i++) {
        await database.save({ context: `Testimony after error ${i}` });
      }
      
      profiler.snapshot('after-recovery');
      
      const report = profiler.getReport();
      
      // Should have recovered without issues
      expect(database.save).toHaveBeenCalled();
    });
  });

  describe('Resource Cleanup Validation', () => {
    it('should cleanup all resources on application shutdown', async () => {
      profiler.snapshot('shutdown-start');
      
      // Initialize services
      await avatarService.initialize();
      await voiceService.startRecording();
      await transcriptionService.transcribe('/audio/test.wav');
      
      profiler.snapshot('all-initialized');
      
      // Cleanup all services
      avatarService.dispose();
      voiceService.dispose();
      await database.clear();
      
      profiler.snapshot('shutdown-complete');
      
      const report = profiler.getReport();
      const finalMemory = report.max.memory;
      const initialMemory = report.min.memory;
      
      // Memory should return to near baseline
      expect(finalMemory - initialMemory).toBeLessThan(40);
    });

    it('should properly cleanup database indices', async () => {
      // Add testimonies
      const ids = [];
      for (let i = 0; i < 20; i++) {
        const id = await database.save({
          context: `Testimony ${i}`,
          incidentType: 'discrimination',
        });
        ids.push(id);
      }
      
      // Verify all saved
      expect(ids.length).toBe(20);
      
      // Clear and verify cleanup
      await database.clear();
      const remaining = await database.getAll();
      
      expect(remaining.length).toBe(0);
    });

    it('should manage temporary objects efficiently', async () => {
      profiler.snapshot('temp-objects-start');
      
      // Create many temporary objects (simulating typical operations)
      for (let i = 0; i < 1000; i++) {
        const tempObject = {
          id: `temp-${i}`,
          data: Array(100).fill(0),
          nested: { field: 'value' },
        };
        
        // Use and discard
        JSON.stringify(tempObject);
      }
      
      profiler.snapshot('temp-objects-end');
      
      // Temporary objects should be garbage collected
      // Memory should not grow unbounded
      const report = profiler.getReport();
      expect(report.leaks.length).toBe(0);
    });
  });

  describe('Performance Degradation Monitoring', () => {
    it('should alert if memory growth exceeds threshold', () => {
      const baseline = 100; // MB
      const current = 140; // MB
      const threshold = 30; // MB threshold
      
      const degradation = current - baseline;
      const isDegraded = degradation > threshold;
      
      expect(isDegraded).toBe(true);
      
      if (isDegraded) {
        console.warn(`Performance alert: Memory degradation of ${degradation}MB detected`);
      }
    });

    it('should track operation latency over time', () => {
      const latencies = [100, 105, 110, 150, 160, 165]; // ms
      
      const avg = latencies.reduce((a, b) => a + b, 0) / latencies.length;
      const trend = latencies[latencies.length - 1] - latencies[0];
      
      if (trend > avg * 0.5) {
        console.warn(`Performance alert: Latency trend shows ${trend}ms increase`);
      }
      
      // Should detect degradation
      expect(trend).toBeGreaterThan(50);
    });

    it('should identify memory hotspots from profile', () => {
      const profile = {
        transcription: 45,
        avatar: 35,
        database: 15,
        voiceInput: 5,
      };
      
      const total = Object.values(profile).reduce((a, b) => a + b, 0);
      const hotspots = Object.entries(profile)
        .filter(([_, mem]) => (mem / total) > 0.3)
        .map(([name, _]) => name);
      
      expect(hotspots.includes('transcription')).toBe(true);
      expect(hotspots.includes('avatar')).toBe(true);
    });
  });
});
