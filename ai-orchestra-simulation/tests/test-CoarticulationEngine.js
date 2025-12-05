/**
 * Test CoarticulationEngine - Comprehensive testing for advanced phoneme blending
 *
 * Tests look-ahead processing, transition smoothing, assimilation effects, and cluster optimization.
 */

import { CoarticulationEngine } from '../src/animation/CoarticulationEngine.js';

describe('CoarticulationEngine', () => {
  let engine;
  let mockLogger;

  beforeEach(() => {
    mockLogger = {
      log: jest.fn(),
    };

    // Mock Logger constructor
    jest.spyOn(console, 'log').mockImplementation(() => {});

    engine = new CoarticulationEngine();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Initialization', () => {
    test('should initialize with default config', () => {
      expect(engine.config.lookAheadPhonemes).toBe(3);
      expect(engine.config.transitionDuration).toBe(150);
      expect(engine.config.smoothingFactor).toBe(0.7);
    });

    test('should initialize coarticulation rules database', () => {
      expect(engine.coarticulationRules).toBeDefined();
      expect(Object.keys(engine.coarticulationRules).length).toBeGreaterThan(100);
    });

    test('should initialize assimilation patterns', () => {
      expect(engine.assimilationPatterns).toBeDefined();
      expect(engine.assimilationPatterns.place).toBeDefined();
      expect(engine.assimilationPatterns.manner).toBeDefined();
      expect(engine.assimilationPatterns.voicing).toBeDefined();
    });

    test('should log initialization', () => {
      // Check that some logging occurred during initialization
      expect(console.log).toHaveBeenCalled();
    });
  });

  describe('Phoneme Sequence Processing', () => {
    test('should process empty sequence', () => {
      const result = engine.processPhonemeSequence([]);
      expect(result).toEqual([]);
    });

    test('should process single phoneme', () => {
      const sequence = [{ phoneme: 'aa', intensities: { jawOpen: 0.8 } }];
      const result = engine.processPhonemeSequence(sequence);

      expect(result).toHaveLength(1);
      expect(result[0].phoneme).toBe('aa');
    });

    test('should process vowel sequence with smoothing', () => {
      const sequence = [
        { phoneme: 'aa', intensities: { jawOpen: 0.9 } },
        { phoneme: 'ee', intensities: { jawOpen: 0.6 } },
      ];
      const result = engine.processPhonemeSequence(sequence);

      expect(result).toHaveLength(2);
      expect(result[0].phoneme).toBe('aa');
      expect(result[1].phoneme).toBe('ee');
    });

    test('should build look-ahead buffer', () => {
      const sequence = ['aa', 'b', 'ee', 's'];
      const buffer = engine.buildLookAheadBuffer(sequence);

      expect(buffer).toHaveLength(4);
      expect(buffer[0]).toHaveLength(3); // Look ahead 3 phonemes
      expect(buffer[0][0].phoneme).toBe('b');
      expect(buffer[0][0].distance).toBe(1);
      expect(buffer[0][0].weight).toBeLessThan(1);
    });
  });

  describe('Context Building', () => {
    test('should build context for middle phoneme', () => {
      const sequence = ['aa', 'b', 'ee'];
      const lookAheadBuffer = engine.buildLookAheadBuffer(sequence);
      const timingData = [{ duration: 100 }, { duration: 80 }, { duration: 120 }];

      const context = engine.buildContext(1, sequence, lookAheadBuffer, timingData);

      expect(context.index).toBe(1);
      expect(context.previousPhoneme).toBe('aa');
      expect(context.nextPhoneme).toBe('ee');
      expect(context.lookAhead).toHaveLength(2);
      expect(context.timing.duration).toBe(80);
      expect(context.position).toBeCloseTo(0.5, 1);
    });

    test('should build context for first phoneme', () => {
      const sequence = ['aa', 'b'];
      const lookAheadBuffer = engine.buildLookAheadBuffer(sequence);
      const timingData = [];

      const context = engine.buildContext(0, sequence, lookAheadBuffer, timingData);

      expect(context.previousPhoneme).toBeNull();
      expect(context.nextPhoneme).toBe('b');
      expect(context.position).toBe(0);
    });

    test('should build context for last phoneme', () => {
      const sequence = ['aa', 'b'];
      const lookAheadBuffer = engine.buildLookAheadBuffer(sequence);
      const timingData = [];

      const context = engine.buildContext(1, sequence, lookAheadBuffer, timingData);

      expect(context.previousPhoneme).toBe('aa');
      expect(context.nextPhoneme).toBeNull();
      expect(context.lookAhead).toHaveLength(0);
      expect(context.position).toBe(1);
    });
  });

  describe('Transition Smoothing', () => {
    test('should apply vowel-to-vowel smoothing', () => {
      const phoneme = {
        phoneme: 'ee',
        intensities: { jawOpen: 0.6 },
        timing: { duration: 100 },
      };
      const context = {
        previousPhoneme: 'aa',
        nextPhoneme: 'ih',
        position: 0.5,
      };

      const result = engine.applyTransitionSmoothing(phoneme, context);

      expect(result.intensities.jawOpen).toBeDefined();
      expect(result.timing.transitionType).toBe('smooth');
    });

    test('should apply consonant-to-vowel smoothing', () => {
      const phoneme = {
        phoneme: 'aa',
        intensities: { jawOpen: 0.9 },
        timing: { duration: 100 },
      };
      const context = {
        previousPhoneme: 'b',
        nextPhoneme: 'ee',
        position: 0.3,
      };

      const result = engine.applyTransitionSmoothing(phoneme, context);

      expect(result.timing.transitionType).toBe('burst_release');
      expect(result.timing.duration).toBe(80);
    });

    test('should handle missing transition rules', () => {
      const phoneme = {
        phoneme: 'unknown',
        intensities: { jawOpen: 0.5 },
      };
      const context = {
        previousPhoneme: 'also_unknown',
        position: 0.5,
      };

      const result = engine.applyTransitionSmoothing(phoneme, context);

      expect(result.intensities.jawOpen).toBe(0.5);
    });
  });

  describe('Anticipatory Coarticulation', () => {
    test('should apply anticipatory effects from look-ahead', () => {
      const phoneme = {
        phoneme: 'aa',
        intensities: { mouthPucker: 0.3, mouthFunnel: 0.2 },
      };
      const context = {
        lookAhead: [
          { phoneme: 'ow', distance: 1, weight: 0.8 },
          { phoneme: 'ee', distance: 2, weight: 0.6 },
        ],
      };

      const result = engine.applyAnticipatoryCoarticulation(phoneme, context);

      // Should show some influence from rounded vowel 'ow'
      expect(result.intensities.mouthPucker).toBeGreaterThan(0.3);
    });

    test('should calculate anticipatory influence', () => {
      const influence = engine.calculateAnticipatoryInfluence('aa', {
        phoneme: 'ow',
        distance: 1,
        weight: 0.8,
      });

      expect(influence.lipProtrusion).toBeDefined();
      expect(influence.lipProtrusion).toBeGreaterThan(0);
    });

    test('should handle empty look-ahead', () => {
      const phoneme = {
        phoneme: 'aa',
        intensities: { jawOpen: 0.8 },
      };
      const context = { lookAhead: [] };

      const result = engine.applyAnticipatoryCoarticulation(phoneme, context);

      expect(result.intensities.jawOpen).toBe(0.8);
    });
  });

  describe('Perseveratory Coarticulation', () => {
    test('should apply perseveratory effects from previous phoneme', () => {
      const phoneme = {
        phoneme: 'b',
        intensities: { mouthClose: 0.8 },
      };
      const context = {
        previousPhoneme: 'aa',
        nextPhoneme: 'ee',
      };

      const result = engine.applyPerseveratoryCoarticulation(phoneme, context);

      // Should show reduced intensity due to vowel-to-consonant transition
      expect(result.intensities.mouthClose).toBeLessThan(0.8);
    });

    test('should handle missing previous phoneme', () => {
      const phoneme = {
        phoneme: 'aa',
        intensities: { jawOpen: 0.9 },
      };
      const context = { previousPhoneme: null };

      const result = engine.applyPerseveratoryCoarticulation(phoneme, context);

      expect(result.intensities.jawOpen).toBe(0.9);
    });
  });

  describe('Assimilation Effects', () => {
    test('should apply place assimilation', () => {
      const phoneme = {
        phoneme: 'f',
        intensities: { mouthClose: 0.6 },
      };
      const context = { previousPhoneme: 'b' };

      const result = engine.applyAssimilationEffects(phoneme, context);

      // Should show some assimilation effect
      expect(result.intensities.mouthClose).not.toBe(0.6);
    });

    test('should find assimilation patterns', () => {
      const pattern = engine.findAssimilationPattern('b->f');
      expect(pattern).toBeTruthy();
      expect(pattern.strength).toBeGreaterThan(0);
      expect(pattern.features).toContain('lipProtrusion');
    });

    test('should return null for unknown transitions', () => {
      const pattern = engine.findAssimilationPattern('unknown->transition');
      expect(pattern).toBeNull();
    });
  });

  describe('Cluster Optimization', () => {
    test('should optimize consonant clusters', () => {
      const phoneme = {
        phoneme: 's',
        intensities: { mouthClose: 0.7 },
        timing: { duration: 100 },
      };
      const context = {
        previousPhoneme: 't',
        nextPhoneme: 'r',
      };

      const result = engine.applyClusterOptimization(phoneme, context);

      // Should reduce intensity and duration for cluster
      expect(result.intensities.mouthClose).toBeLessThan(0.7);
      expect(result.timing.duration).toBeLessThan(100);
    });

    test('should not optimize non-clusters', () => {
      const phoneme = {
        phoneme: 'aa',
        intensities: { jawOpen: 0.9 },
        timing: { duration: 100 },
      };
      const context = {
        previousPhoneme: 's',
        nextPhoneme: 'ee',
      };

      const result = engine.applyClusterOptimization(phoneme, context);

      expect(result.intensities.jawOpen).toBe(0.9);
      expect(result.timing.duration).toBe(100);
    });
  });

  describe('Utility Functions', () => {
    test('should identify vowels correctly', () => {
      expect(engine.isVowel('aa')).toBe(true);
      expect(engine.isVowel('ee')).toBe(true);
      expect(engine.isVowel('b')).toBe(false);
      expect(engine.isVowel('s')).toBe(false);
      expect(engine.isVowel('sil')).toBe(false);
    });

    test('should identify consonants correctly', () => {
      expect(engine.isConsonant('b')).toBe(true);
      expect(engine.isConsonant('s')).toBe(true);
      expect(engine.isConsonant('aa')).toBe(false);
      expect(engine.isConsonant('sil')).toBe(false);
      expect(engine.isConsonant('pau')).toBe(false);
    });

    test('should smooth transitions', () => {
      const smoothed = engine.smoothTransition(0.8, 0.5, 0.5);
      expect(smoothed).toBeGreaterThan(0.7);
      expect(smoothed).toBeLessThan(0.9);
    });

    test('should ease in-out quad', () => {
      expect(engine.easeInOutQuad(0)).toBe(0);
      expect(engine.easeInOutQuad(0.5)).toBe(0.5);
      expect(engine.easeInOutQuad(1)).toBe(1);
    });
  });

  describe('Statistics and Export', () => {
    test('should provide comprehensive statistics', () => {
      const stats = engine.getStatistics();

      expect(stats).toMatchObject({
        rulesCount: expect.any(Number),
        assimilationPatterns: 3,
        lookAheadBuffer: 0,
        transitionBuffer: 0,
        config: expect.any(Object),
      });

      expect(stats.rulesCount).toBeGreaterThan(100);
    });

    test('should export configuration', () => {
      const config = engine.exportConfiguration();

      expect(config).toMatchObject({
        config: expect.any(Object),
        coarticulationRules: expect.any(Object),
        assimilationPatterns: expect.any(Object),
        statistics: expect.any(Object),
      });
    });

    test('should reset engine state', () => {
      // Add some state
      engine.transitionBuffer.set('test', 'value');
      engine.lookAheadBuffer = ['test'];

      engine.reset();

      expect(engine.transitionBuffer.size).toBe(0);
      expect(engine.lookAheadBuffer).toEqual([]);
    });
  });

  describe('Coarticulation Rules', () => {
    test('should have vowel glide rules', () => {
      const rule = engine.coarticulationRules['aa->ee'];
      expect(rule).toBeDefined();
      expect(rule.type).toBe('vowel_glide');
      expect(rule.smoothingFactor).toBe(0.8);
    });

    test('should have CV transition rules', () => {
      const rule = engine.coarticulationRules['b->aa'];
      expect(rule).toBeDefined();
      expect(rule.type).toBe('cv_transition');
      expect(rule.transitionType).toBe('burst_release');
    });

    test('should have VC transition rules', () => {
      const rule = engine.coarticulationRules['aa->b'];
      expect(rule).toBeDefined();
      expect(rule.type).toBe('vc_transition');
      expect(rule.transitionType).toBe('anticipatory');
    });

    test('should have consonant assimilation rules', () => {
      const rule = engine.coarticulationRules['b->p'];
      expect(rule).toBeDefined();
      expect(rule.type).toBe('consonant_assimilation');
      expect(rule.assimilationStrength).toBe(0.8);
    });
  });
});