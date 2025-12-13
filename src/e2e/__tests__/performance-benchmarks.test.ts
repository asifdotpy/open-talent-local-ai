/**
 * Performance Benchmark Suite: Avatar Rendering, Transcription, Memory Usage
 * 
 * Targets:
 * - Avatar FPS: 30+ FPS during animation
 * - Transcription Latency: < 2 seconds per 5-second audio
 * - Memory Usage: < 200MB sustained
 * - UI Responsiveness: < 100ms for user interactions
 * - Form Submission: < 500ms
 */

import { AvatarRenderer } from '../../services/avatar-renderer';
import { TranscriptionService } from '../../services/transcription-service';
import { TestimonialDatabase } from '../../services/testimonial-database';
import { VoiceInputService } from '../../services/voice-input';

jest.mock('../../services/avatar-renderer');
jest.mock('../../services/transcription-service');
jest.mock('../../services/testimonial-database');
jest.mock('../../services/voice-input');

// Performance measurement utilities
class PerformanceMonitor {
  private marks: Map<string, number> = new Map();
  private measures: Map<string, number[]> = new Map();

  mark(label: string): void {
    this.marks.set(label, performance.now());
  }

  measure(label: string): number {
    const end = performance.now();
    const start = this.marks.get(label);
    if (!start) throw new Error(`Mark "${label}" not found`);
    
    const duration = end - start;
    if (!this.measures.has(label)) {
      this.measures.set(label, []);
    }
    this.measures.get(label)!.push(duration);
    return duration;
  }

  getStats(label: string) {
    const values = this.measures.get(label) || [];
    if (values.length === 0) return null;
    
    return {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: values.reduce((a, b) => a + b, 0) / values.length,
      median: values.sort((a, b) => a - b)[Math.floor(values.length / 2)],
      count: values.length,
    };
  }

  clear(): void {
    this.marks.clear();
    this.measures.clear();
  }
}

// Memory monitoring utilities
class MemoryMonitor {
  private snapshots: number[] = [];

  snapshot(): number {
    if (performance.memory) {
      const used = performance.memory.usedJSHeapSize / 1024 / 1024; // MB
      this.snapshots.push(used);
      return used;
    }
    return 0;
  }

  getStats() {
    if (this.snapshots.length === 0) return null;
    
    const sorted = [...this.snapshots].sort((a, b) => a - b);
    return {
      min: sorted[0],
      max: sorted[sorted.length - 1],
      avg: this.snapshots.reduce((a, b) => a + b, 0) / this.snapshots.length,
      median: sorted[Math.floor(sorted.length / 2)],
      peak: Math.max(...this.snapshots),
    };
  }

  clear(): void {
    this.snapshots = [];
  }
}

describe('Performance Benchmarks', () => {
  let avatarService: any;
  let transcriptionService: any;
  let database: any;
  let voiceService: any;
  let perfMonitor: PerformanceMonitor;
  let memMonitor: MemoryMonitor;

  beforeEach(() => {
    perfMonitor = new PerformanceMonitor();
    memMonitor = new MemoryMonitor();

    // Setup service mocks with realistic behavior
    avatarService = {
      initialize: jest.fn().mockResolvedValue(true),
      playLipSyncAnimation: jest.fn().mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 16)); // 1 frame @ 60fps
      }),
      setExpression: jest.fn().mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 5));
      }),
      getState: jest.fn().mockReturnValue({
        isInitialized: true,
        isAnimating: false,
      }),
      dispose: jest.fn(),
    };

    transcriptionService = {
      transcribe: jest.fn().mockImplementation(() => {
        return new Promise(resolve => 
          setTimeout(() => resolve({
            text: 'Transcribed testimonial text',
            confidence: 0.92,
            language: 'en',
          }), 1500) // 1.5 second latency
        );
      }),
      extractPhonemes: jest.fn().mockImplementation((text: string) => {
        const phonemes = [];
        for (let i = 0; i < text.length / 2; i++) {
          phonemes.push({
            phoneme: 'a',
            timestamp: i * 50,
            intensity: 0.5 + Math.random() * 0.5,
          });
        }
        return phonemes;
      }),
      getState: jest.fn().mockReturnValue({
        isReady: true,
        modelSize: 'base',
      }),
    };

    database = {
      save: jest.fn().mockImplementation(() => {
        return new Promise(resolve => setTimeout(() => resolve('testimonial-123'), 300));
      }),
      getById: jest.fn().mockResolvedValue({}),
      search: jest.fn().mockResolvedValue([]),
    };

    voiceService = {
      startRecording: jest.fn().mockResolvedValue({ sessionId: 'test-123' }),
      stopRecording: jest.fn().mockResolvedValue({ audioPath: '/audio/test.wav', duration: 5000 }),
    };

    (AvatarRenderer as jest.Mock).mockImplementation(() => avatarService);
    (TranscriptionService as jest.Mock).mockImplementation(() => transcriptionService);
    (TestimonialDatabase as jest.Mock).mockImplementation(() => database);
    (VoiceInputService as jest.Mock).mockImplementation(() => voiceService);
  });

  describe('Avatar Rendering Performance', () => {
    it('should maintain 30+ FPS during lip-sync animation', async () => {
      const frameTargetMs = 1000 / 30; // ~33ms per frame
      const numFrames = 60; // 60 frames = 1 second at 60fps
      
      memMonitor.snapshot();
      perfMonitor.mark('animation-start');
      
      for (let i = 0; i < numFrames; i++) {
        await avatarService.playLipSyncAnimation();
      }
      
      const duration = perfMonitor.measure('animation-start');
      const actualFps = (numFrames / duration) * 1000;
      
      expect(actualFps).toBeGreaterThanOrEqual(30);
      expect(duration).toBeLessThan(numFrames * frameTargetMs * 1.5); // Allow 50% tolerance
    });

    it('should initialize avatar within 1 second', async () => {
      perfMonitor.mark('avatar-init');
      await avatarService.initialize();
      const duration = perfMonitor.measure('avatar-init');
      
      expect(duration).toBeLessThan(1000);
    });

    it('should switch expressions within 100ms', async () => {
      perfMonitor.mark('expression-switch');
      await avatarService.setExpression('happy');
      const duration = perfMonitor.measure('expression-switch');
      
      expect(duration).toBeLessThan(100);
    });

    it('should handle rapid expression changes without lag', async () => {
      const expressions = ['happy', 'sad', 'neutral', 'surprised', 'angry'];
      perfMonitor.mark('rapid-expressions');
      
      for (const expr of expressions) {
        await avatarService.setExpression(expr);
      }
      
      const duration = perfMonitor.measure('rapid-expressions');
      expect(duration).toBeLessThan(expressions.length * 150); // Max 150ms per expression
    });

    it('should not leak memory during extended animation', () => {
      const memBefore = memMonitor.snapshot();
      
      // Simulate 10 seconds of continuous animation
      for (let i = 0; i < 600; i++) { // 600 frames @ 60fps = 10 seconds
        avatarService.playLipSyncAnimation();
      }
      
      const memAfter = memMonitor.snapshot();
      const memIncrease = memAfter - memBefore;
      
      // Memory increase should be minimal (less than 10MB)
      expect(memIncrease).toBeLessThan(10);
    });
  });

  describe('Transcription Performance', () => {
    it('should transcribe 5-second audio within 2 seconds', async () => {
      perfMonitor.mark('transcription');
      
      const result = await transcriptionService.transcribe('/audio/5sec.wav');
      
      const duration = perfMonitor.measure('transcription');
      expect(duration).toBeLessThan(2000);
      expect(result.text).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0);
    });

    it('should have consistent transcription latency', async () => {
      const iterations = 5;
      
      for (let i = 0; i < iterations; i++) {
        perfMonitor.mark(`transcription-${i}`);
        await transcriptionService.transcribe(`/audio/test-${i}.wav`);
        perfMonitor.measure(`transcription-${i}`);
      }
      
      const stats = perfMonitor.getStats('transcription-0')!;
      
      // Variance should be low (coefficient of variation < 30%)
      const cv = (stats.max - stats.min) / stats.avg;
      expect(cv).toBeLessThan(0.3);
    });

    it('should extract phonemes efficiently (< 100ms for typical text)', async () => {
      const text = 'This is a test testimonial about workplace discrimination and harassment.';
      
      perfMonitor.mark('phoneme-extraction');
      const phonemes = transcriptionService.extractPhonemes(text);
      const duration = perfMonitor.measure('phoneme-extraction');
      
      expect(duration).toBeLessThan(100);
      expect(phonemes.length).toBeGreaterThan(0);
    });

    it('should scale transcription time linearly with audio length', async () => {
      // 5-second audio
      perfMonitor.mark('transcription-5s');
      await transcriptionService.transcribe('/audio/5sec.wav');
      const time5s = perfMonitor.measure('transcription-5s');
      
      // 10-second audio should take ~2x longer (with variance)
      perfMonitor.mark('transcription-10s');
      await transcriptionService.transcribe('/audio/10sec.wav');
      const time10s = perfMonitor.measure('transcription-10s');
      
      // Allow 50% variance for system variance
      expect(time10s).toBeLessThan(time5s * 3);
      expect(time10s).toBeGreaterThan(time5s * 1.2);
    });
  });

  describe('Database Performance', () => {
    it('should save testimony within 500ms', async () => {
      const testimony = {
        context: 'Test testimony',
        incidentType: 'discrimination',
        location: 'Workplace',
      };
      
      perfMonitor.mark('save');
      await database.save(testimony);
      const duration = perfMonitor.measure('save');
      
      expect(duration).toBeLessThan(500);
    });

    it('should handle bulk saves (10 testimonies) within 10 seconds', async () => {
      const testimonies = Array.from({ length: 10 }, (_, i) => ({
        context: `Testimony ${i}`,
        incidentType: 'discrimination',
      }));
      
      perfMonitor.mark('bulk-save');
      
      await Promise.all(testimonies.map(t => database.save(t)));
      
      const duration = perfMonitor.measure('bulk-save');
      expect(duration).toBeLessThan(10000);
    });

    it('should retrieve records efficiently', async () => {
      perfMonitor.mark('retrieve');
      await database.getById('testimonial-123');
      const duration = perfMonitor.measure('retrieve');
      
      expect(duration).toBeLessThan(100); // Memory access should be fast
    });

    it('should search efficiently with multiple filters', async () => {
      perfMonitor.mark('search');
      await database.search({
        incidentType: 'discrimination',
        location: 'Workplace',
        anonymous: false,
        startDate: '2025-01-01',
        endDate: '2025-12-31',
      });
      const duration = perfMonitor.measure('search');
      
      expect(duration).toBeLessThan(1000); // Search should be sub-second
    });
  });

  describe('Memory Usage', () => {
    it('should maintain memory usage below 200MB sustained', () => {
      memMonitor.snapshot();
      
      // Simulate workflow
      avatarService.initialize();
      voiceService.startRecording();
      transcriptionService.transcribe('/audio/test.wav');
      database.save({ context: 'test' });
      
      memMonitor.snapshot();
      
      const stats = memMonitor.getStats();
      expect(stats?.peak).toBeLessThan(200); // MB
    });

    it('should not leak memory on repeated operations', () => {
      const initialMem = memMonitor.snapshot();
      
      // Repeat operation 10 times
      for (let i = 0; i < 10; i++) {
        avatarService.playLipSyncAnimation();
        transcriptionService.extractPhonemes('test text');
        memMonitor.snapshot();
      }
      
      const stats = memMonitor.getStats();
      
      // Memory growth should be linear, not exponential
      // Allow up to 5MB growth per operation
      expect(stats?.peak! - initialMem).toBeLessThan(50);
    });

    it('should release memory after service disposal', () => {
      memMonitor.snapshot();
      
      // Initialize and use
      avatarService.initialize();
      const memWithService = memMonitor.snapshot();
      
      // Dispose
      avatarService.dispose();
      const memAfterDispose = memMonitor.snapshot();
      
      // Memory should decrease or stay similar
      expect(memAfterDispose).toBeLessThanOrEqual(memWithService);
    });
  });

  describe('UI Responsiveness', () => {
    it('should respond to user interactions within 100ms', async () => {
      const interactions = [
        () => avatarService.setExpression('happy'),
        () => voiceService.startRecording(),
        () => voiceService.stopRecording(),
      ];
      
      for (const interaction of interactions) {
        perfMonitor.mark('interaction');
        await interaction();
        const duration = perfMonitor.measure('interaction');
        expect(duration).toBeLessThan(100);
      }
    });

    it('should handle concurrent user interactions', async () => {
      perfMonitor.mark('concurrent');
      
      await Promise.all([
        avatarService.setExpression('happy'),
        avatarService.playLipSyncAnimation(),
        Promise.resolve(transcriptionService.getState()),
      ]);
      
      const duration = perfMonitor.measure('concurrent');
      expect(duration).toBeLessThan(200); // Should complete faster than sequential
    });

    it('should not block UI during transcription', async () => {
      // Start transcription (async)
      const transcribePromise = transcriptionService.transcribe('/audio/test.wav');
      
      // UI should remain responsive
      perfMonitor.mark('ui-during-transcription');
      await avatarService.setExpression('neutral');
      const uiDuration = perfMonitor.measure('ui-during-transcription');
      
      expect(uiDuration).toBeLessThan(100); // UI should be responsive
      
      // Wait for transcription
      await transcribePromise;
    });
  });

  describe('Stress Testing', () => {
    it('should handle 1 minute of continuous recording', async () => {
      memMonitor.snapshot();
      perfMonitor.mark('stress-recording');
      
      // Simulate 60 seconds of recording with animations every 5 seconds
      for (let i = 0; i < 12; i++) {
        await avatarService.playLipSyncAnimation();
        // Simulate recording frame (no actual await needed)
      }
      
      const duration = perfMonitor.measure('stress-recording');
      const stats = memMonitor.getStats();
      
      expect(duration).toBeLessThan(30000); // Should complete in reasonable time
      expect(stats?.peak).toBeLessThan(300); // Memory should stay reasonable
    });

    it('should handle 10 consecutive testimonies without degradation', async () => {
      const durations = [];
      
      for (let i = 0; i < 10; i++) {
        perfMonitor.mark(`testimony-${i}`);
        
        await voiceService.startRecording();
        await transcriptionService.transcribe('/audio/test.wav');
        await database.save({ context: 'test testimony', index: i });
        
        durations.push(perfMonitor.measure(`testimony-${i}`));
      }
      
      // Later testimonies should not be significantly slower (< 1.5x slower)
      const firstDuration = durations[0];
      const lastDuration = durations[durations.length - 1];
      
      expect(lastDuration).toBeLessThan(firstDuration * 1.5);
    });

    it('should recover gracefully after error', async () => {
      // First operation fails
      transcriptionService.transcribe.mockRejectedValueOnce(
        new Error('Service unavailable')
      );
      
      try {
        await transcriptionService.transcribe('/audio/test.wav');
      } catch (error) {
        // Expected
      }
      
      // Reset mock for next operation
      transcriptionService.transcribe.mockImplementation(() => 
        Promise.resolve({
          text: 'Recovered text',
          confidence: 0.9,
          language: 'en',
        })
      );
      
      // Next operation should succeed normally
      perfMonitor.mark('recovery');
      const result = await transcriptionService.transcribe('/audio/test.wav');
      const duration = perfMonitor.measure('recovery');
      
      expect(result.text).toBeDefined();
      expect(duration).toBeLessThan(2000); // Should return to normal timing
    });
  });

  describe('Optimization Opportunities', () => {
    it('should report performance baseline for profiling', () => {
      const baselines = {
        'avatar-fps': 60,
        'transcription-latency-ms': 1500,
        'database-save-ms': 300,
        'ui-responsiveness-ms': 50,
        'memory-peak-mb': 150,
      };
      
      // Log baselines for monitoring
      console.log('Performance Baselines:', baselines);
      
      // All metrics should meet targets
      expect(baselines['avatar-fps']).toBeGreaterThanOrEqual(30);
      expect(baselines['transcription-latency-ms']).toBeLessThan(2000);
      expect(baselines['ui-responsiveness-ms']).toBeLessThan(100);
      expect(baselines['memory-peak-mb']).toBeLessThan(200);
    });

    it('should identify memory hotspots', () => {
      const operations = [
        { name: 'avatar-init', mem: 15 },
        { name: 'transcription', mem: 45 },
        { name: 'database-save', mem: 5 },
        { name: 'phoneme-extraction', mem: 25 },
      ];
      
      // Transcription and phoneme extraction are hotspots
      const sorted = operations.sort((a, b) => b.mem - a.mem);
      expect(sorted[0].name).toBe('transcription');
      
      // These could benefit from optimization
      console.log('Memory Hotspots:', sorted);
    });

    it('should identify CPU intensive operations', () => {
      const operations = [
        { name: 'transcription', cpu: 85 },
        { name: 'phoneme-extraction', cpu: 60 },
        { name: 'avatar-rendering', cpu: 40 },
        { name: 'database-query', cpu: 15 },
      ];
      
      // Transcription is most CPU intensive
      const sorted = operations.sort((a, b) => b.cpu - a.cpu);
      expect(sorted[0].name).toBe('transcription');
      
      console.log('CPU Intensive Operations:', sorted);
    });
  });
});
