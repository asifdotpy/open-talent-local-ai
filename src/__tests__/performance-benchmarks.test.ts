/**
 * Performance Benchmark Suite: Avatar Rendering, Transcription, Memory Usage
 */

import { AvatarRenderer } from '../services/avatar-renderer';
import { TranscriptionService } from '../services/transcription-service';
import { TestimonialDatabase } from '../services/testimonial-database';
import { VoiceInputService } from '../services/voice-input';

jest.mock('../services/avatar-renderer');
jest.mock('../services/transcription-service');
jest.mock('../services/testimonial-database');
jest.mock('../services/voice-input');

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
      count: values.length,
    };
  }

  clear(): void {
    this.marks.clear();
    this.measures.clear();
  }
}

describe('Performance Benchmarks', () => {
  let avatarService: any;
  let transcriptionService: any;
  let database: any;
  let voiceService: any;
  let perfMonitor: PerformanceMonitor;

  beforeEach(() => {
    perfMonitor = new PerformanceMonitor();

    avatarService = {
      initialize: jest.fn().mockResolvedValue(true),
      playLipSyncAnimation: jest.fn().mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 16));
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
          }), 1500)
        );
      }),
      extractPhonemes: jest.fn().mockImplementation((text: string) => {
        const phonemes = [];
        for (let i = 0; i < Math.min(text.length / 2, 20); i++) {
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

    it('should handle rapid expression changes', async () => {
      const expressions = ['happy', 'sad', 'neutral'];
      perfMonitor.mark('rapid-expressions');
      
      for (const expr of expressions) {
        await avatarService.setExpression(expr);
      }
      
      const duration = perfMonitor.measure('rapid-expressions');
      expect(duration).toBeLessThan(500);
    });
  });

  describe('Transcription Performance', () => {
    it('should transcribe audio within 2 seconds', async () => {
      perfMonitor.mark('transcription');
      
      const result = await transcriptionService.transcribe('/audio/5sec.wav');
      
      const duration = perfMonitor.measure('transcription');
      expect(duration).toBeLessThan(2000);
      expect(result.text).toBeDefined();
    });

    it('should extract phonemes efficiently', async () => {
      const text = 'This is a test testimonial about workplace discrimination.';
      
      perfMonitor.mark('phoneme-extraction');
      const phonemes = transcriptionService.extractPhonemes(text);
      const duration = perfMonitor.measure('phoneme-extraction');
      
      expect(duration).toBeLessThan(100);
      expect(phonemes.length).toBeGreaterThan(0);
    });
  });

  describe('Database Performance', () => {
    it('should save testimony within 500ms', async () => {
      const testimony = {
        context: 'Test testimony',
        incidentType: 'discrimination',
      };
      
      perfMonitor.mark('save');
      await database.save(testimony);
      const duration = perfMonitor.measure('save');
      
      expect(duration).toBeLessThan(500);
    });

    it('should handle bulk saves within reasonable time', async () => {
      const testimonies = Array.from({ length: 10 }, (_, i) => ({
        context: `Testimony ${i}`,
      }));
      
      perfMonitor.mark('bulk-save');
      
      await Promise.all(testimonies.map(t => database.save(t)));
      
      const duration = perfMonitor.measure('bulk-save');
      expect(duration).toBeLessThan(10000);
    });
  });

  describe('UI Responsiveness', () => {
    it('should respond to user interactions within 100ms', async () => {
      const interactions = [
        () => avatarService.setExpression('happy'),
        () => voiceService.startRecording(),
      ];
      
      for (const interaction of interactions) {
        perfMonitor.mark('interaction');
        await interaction();
        const duration = perfMonitor.measure('interaction');
        expect(duration).toBeLessThan(100);
      }
    });

    it('should handle concurrent operations', async () => {
      perfMonitor.mark('concurrent');
      
      await Promise.all([
        avatarService.setExpression('happy'),
        avatarService.playLipSyncAnimation(),
        Promise.resolve(transcriptionService.getState()),
      ]);
      
      const duration = perfMonitor.measure('concurrent');
      expect(duration).toBeLessThan(200);
    });
  });

  describe('Full Workflow Performance', () => {
    it('should complete full workflow within target time', async () => {
      perfMonitor.mark('full-workflow');
      
      await voiceService.startRecording();
      await transcriptionService.transcribe('/audio/test.wav');
      await avatarService.playLipSyncAnimation();
      await database.save({ context: 'test' });
      
      const duration = perfMonitor.measure('full-workflow');
      expect(duration).toBeLessThan(5000);
    });
  });
});
