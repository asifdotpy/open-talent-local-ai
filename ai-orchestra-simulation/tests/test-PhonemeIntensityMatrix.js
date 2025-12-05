/**
 * Test PhonemeIntensityMatrix - Comprehensive testing for dynamic intensity calculation
 *
 * Tests audio modulation, emotion integration, coarticulation effects, and adaptive learning.
 */

import { PhonemeIntensityMatrix } from '../src/animation/PhonemeIntensityMatrix.js';
import { Logger } from '../src/utils/Logger.js';

describe('PhonemeIntensityMatrix', () => {
  let matrix;
  let mockLogger;

  beforeEach(() => {
    mockLogger = {
      log: jest.fn(),
      debug: jest.fn(),
      error: jest.fn(),
    };

    // Mock Logger constructor
    jest.spyOn(Logger.prototype, 'log').mockImplementation(mockLogger.log);
    jest.spyOn(Logger.prototype, 'debug').mockImplementation(mockLogger.debug);
    jest.spyOn(Logger.prototype, 'error').mockImplementation(mockLogger.error);

    matrix = new PhonemeIntensityMatrix();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Initialization', () => {
    test('should initialize with default config', () => {
      expect(matrix.config.baseIntensityRange).toEqual([0.1, 1.0]);
      expect(matrix.config.amplitudeSensitivity).toBe(0.8);
      expect(matrix.config.adaptiveLearning).toBe(true);
    });

    test('should initialize base intensity matrix for all phonemes', () => {
      const stats = matrix.getStatistics();
      expect(stats.phonemes).toBe(41); // 39 phonemes + sil + pau
      expect(stats.morphTargets).toBe(52);
      expect(stats.totalMappings).toBe(2132); // 41 * 52
      expect(stats.activeMappings).toBeGreaterThan(0);
    });

    test('should initialize coarticulation matrix', () => {
      expect(matrix.coarticulationMatrix).toBeDefined();
      expect(Object.keys(matrix.coarticulationMatrix)).toHaveLength(41);
    });

    test('should log initialization', () => {
      expect(mockLogger.log).toHaveBeenCalledWith(
        'PhonemeIntensityMatrix initialized',
        expect.objectContaining({
          matrixSize: '41×52',
          features: expect.arrayContaining(['amplitude', 'prosody', 'emotion', 'coarticulation', 'adaptive']),
        })
      );
    });
  });

  describe('Base Intensity Calculation', () => {
    test('should calculate base intensity for vowel phonemes', () => {
      const aaIntensity = matrix.baseIntensityMatrix['aa']['jawOpen'];
      const eeIntensity = matrix.baseIntensityMatrix['ee']['jawOpen'];

      expect(aaIntensity).toBeGreaterThan(eeIntensity); // 'aa' has higher jaw opening
    });

    test('should calculate base intensity for consonant phonemes', () => {
      const mIntensity = matrix.baseIntensityMatrix['m']['mouthClose'];
      const fIntensity = matrix.baseIntensityMatrix['f']['mouthClose'];

      expect(mIntensity).toBeGreaterThan(fIntensity); // 'm' has higher lip compression
    });

    test('should return zero intensity for unrelated phoneme-target pairs', () => {
      const intensity = matrix.baseIntensityMatrix['aa']['cheekPuff'];
      expect(intensity).toBeLessThan(0.1);
    });
  });

  describe('Audio Modifiers', () => {
    test('should update audio modifiers from audio data', () => {
      const audioData = {
        amplitude: 0.8,
        pitch: 250,
        stress: 0.9,
        speakingRate: 5.0,
      };

      matrix.updateAudioModifiers(audioData);

      expect(matrix.audioModifiers.amplitude).toBeGreaterThan(1.0);
      expect(matrix.audioModifiers.pitch).toBeGreaterThan(0.8);
      expect(matrix.audioModifiers.stress).toBe(0.9);
      expect(matrix.audioModifiers.speakingRate).toBeGreaterThan(0.9);
    });

    test('should handle missing audio data gracefully', () => {
      matrix.updateAudioModifiers(null);
      matrix.updateAudioModifiers({});

      expect(matrix.audioModifiers.amplitude).toBe(1.0);
    });

    test('should normalize amplitude correctly', () => {
      expect(matrix.normalizeAmplitude(0)).toBe(0.5);
      expect(matrix.normalizeAmplitude(0.5)).toBe(1.0);
      expect(matrix.normalizeAmplitude(1)).toBe(1.5);
    });

    test('should normalize pitch correctly', () => {
      expect(matrix.normalizePitch(80)).toBeCloseTo(0.8, 1);
      expect(matrix.normalizePitch(240)).toBeCloseTo(1.0, 1);
      expect(matrix.normalizePitch(400)).toBeCloseTo(1.3, 1);
    });
  });

  describe('Emotion Modifiers', () => {
    test('should update emotion modifiers', () => {
      const emotionData = {
        valence: 0.8,
        arousal: 0.7,
        dominance: 0.6,
      };

      matrix.updateEmotionModifiers(emotionData);

      expect(matrix.emotionModifiers.valence).toBe(0.8);
      expect(matrix.emotionModifiers.arousal).toBe(0.7);
      expect(matrix.emotionModifiers.dominance).toBe(0.6);
    });

    test('should clamp emotion values to valid ranges', () => {
      matrix.updateEmotionModifiers({
        valence: 2.0,    // Should clamp to 1.0
        arousal: -0.5,   // Should clamp to 0.0
        dominance: 1.5,  // Should clamp to 1.0
      });

      expect(matrix.emotionModifiers.valence).toBe(1.0);
      expect(matrix.emotionModifiers.arousal).toBe(0.0);
      expect(matrix.emotionModifiers.dominance).toBe(1.0);
    });

    test('should calculate emotion factors for morph targets', () => {
      matrix.updateEmotionModifiers({ valence: 1.0, arousal: 1.0 });

      const smileFactor = matrix.calculateEmotionFactor('mouthSmile');
      const frownFactor = matrix.calculateEmotionFactor('mouthFrown_L');

      expect(smileFactor).toBeGreaterThan(0);
      expect(frownFactor).toBe(0); // No negative valence
    });
  });

  describe('Dynamic Intensity Calculation', () => {
    test('should calculate dynamic intensity with audio modifiers', () => {
      matrix.updateAudioModifiers({ amplitude: 0.8 });

      const baseIntensity = matrix.baseIntensityMatrix['aa']['jawOpen'];
      const dynamicIntensity = matrix.calculateDynamicIntensity('aa', 'jawOpen');

      expect(dynamicIntensity).toBeGreaterThan(baseIntensity);
    });

    test('should apply emotion modifiers to intensity', () => {
      matrix.updateEmotionModifiers({ valence: 1.0 });

      const neutralIntensity = matrix.calculateDynamicIntensity('aa', 'mouthSmile');
      matrix.updateEmotionModifiers({ valence: 1.0 });
      const positiveIntensity = matrix.calculateDynamicIntensity('aa', 'mouthSmile');

      expect(positiveIntensity).toBeGreaterThan(neutralIntensity);
    });

    test('should apply coarticulation effects', () => {
      const context = { previousPhoneme: 'b' }; // Bilabial stop
      const intensity = matrix.calculateDynamicIntensity('aa', 'mouthClose', context);

      // Should be reduced due to coarticulation from 'b' to 'aa'
      expect(intensity).toBeLessThan(matrix.baseIntensityMatrix['aa']['mouthClose']);
    });

    test('should clamp intensity to valid range', () => {
      matrix.updateAudioModifiers({ amplitude: 2.0 }); // Very high amplitude

      const intensity = matrix.calculateDynamicIntensity('aa', 'jawOpen');

      expect(intensity).toBeLessThanOrEqual(1.0);
      expect(intensity).toBeGreaterThanOrEqual(0.1);
    });
  });

  describe('Intensity Profile Generation', () => {
    test('should generate intensity profile for phoneme sequence', () => {
      const phonemeSequence = ['aa', 'b', 'ee', 's'];
      const profile = matrix.getIntensityProfile(phonemeSequence);

      expect(profile).toHaveLength(4);
      expect(profile[0].phoneme).toBe('aa');
      expect(profile[0].intensities).toBeDefined();
      expect(profile[0].context.previousPhoneme).toBeNull();
      expect(profile[0].context.nextPhoneme).toBe('b');
    });

    test('should include coarticulation context in profile', () => {
      const phonemeSequence = ['p', 'aa']; // Plosive to vowel
      const profile = matrix.getIntensityProfile(phonemeSequence);

      expect(profile[1].context.previousPhoneme).toBe('p');
      expect(profile[1].context.nextPhoneme).toBeNull();
    });
  });

  describe('Adaptive Learning', () => {
    test('should learn from user feedback', () => {
      const initialMultiplier = matrix.getUserPreferenceMultiplier('aa', 'jawOpen');
      expect(initialMultiplier).toBe(1.0);

      matrix.learnFromFeedback('aa', 'jawOpen', 1.5);
      const updatedMultiplier = matrix.getUserPreferenceMultiplier('aa', 'jawOpen');

      expect(updatedMultiplier).toBeGreaterThan(1.0);
    });

    test('should maintain performance history', () => {
      matrix.learnFromFeedback('aa', 'jawOpen', 1.2);

      expect(matrix.performanceHistory).toHaveLength(1);
      expect(matrix.performanceHistory[0]).toMatchObject({
        phoneme: 'aa',
        morphTarget: 'jawOpen',
        userRating: 1.2,
        newMultiplier: expect.any(Number),
      });
    });

    test('should limit performance history size', () => {
      // Add more than 1000 entries
      for (let i = 0; i < 1100; i++) {
        matrix.learnFromFeedback('aa', 'jawOpen', 1.0);
      }

      expect(matrix.performanceHistory.length).toBeLessThanOrEqual(1000);
    });

    test('should skip learning when disabled', () => {
      const matrixNoLearning = new PhonemeIntensityMatrix({ adaptiveLearning: false });
      const initialMultiplier = matrixNoLearning.getUserPreferenceMultiplier('aa', 'jawOpen');

      matrixNoLearning.learnFromFeedback('aa', 'jawOpen', 1.5);
      const updatedMultiplier = matrixNoLearning.getUserPreferenceMultiplier('aa', 'jawOpen');

      expect(updatedMultiplier).toBe(initialMultiplier);
    });
  });

  describe('Statistics and Export', () => {
    test('should provide comprehensive statistics', () => {
      const stats = matrix.getStatistics();

      expect(stats).toMatchObject({
        phonemes: 41,
        morphTargets: 52,
        totalMappings: 2132,
        activeMappings: expect.any(Number),
        averageIntensity: expect.any(Number),
        maxIntensity: expect.any(Number),
        userPreferencesLearned: 0,
        performanceHistorySize: 0,
      });

      expect(stats.activeMappings).toBeGreaterThan(1000);
      expect(stats.averageIntensity).toBeGreaterThan(0);
      expect(stats.maxIntensity).toBeLessThanOrEqual(1.0);
    });

    test('should export matrix data', () => {
      matrix.learnFromFeedback('aa', 'jawOpen', 1.2);

      const exportData = matrix.exportMatrix();

      expect(exportData).toMatchObject({
        baseIntensityMatrix: expect.any(Object),
        coarticulationMatrix: expect.any(Object),
        audioModifiers: expect.any(Object),
        emotionModifiers: expect.any(Object),
        userPreferences: expect.any(Object),
        statistics: expect.any(Object),
      });

      expect(exportData.statistics.userPreferencesLearned).toBe(1);
    });

    test('should reset learning data', () => {
      matrix.learnFromFeedback('aa', 'jawOpen', 1.2);
      expect(matrix.userPreferences.size).toBe(1);

      matrix.resetLearning();

      expect(matrix.userPreferences.size).toBe(0);
      expect(matrix.performanceHistory).toHaveLength(0);
    });
  });

  describe('Phoneme Features', () => {
    test('should provide articulatory features for vowels', () => {
      const aaFeatures = matrix.getPhonemeFeatures('aa');
      const eeFeatures = matrix.getPhonemeFeatures('ee');

      expect(aaFeatures.jawOpening).toBeGreaterThan(eeFeatures.jawOpening);
      expect(eeFeatures.tongueHeight).toBeGreaterThan(aaFeatures.tongueHeight);
    });

    test('should provide articulatory features for consonants', () => {
      const mFeatures = matrix.getPhonemeFeatures('m');
      const fFeatures = matrix.getPhonemeFeatures('f');

      expect(mFeatures.lipCompression).toBeGreaterThan(fFeatures.lipCompression);
      expect(fFeatures.lipWidth).toBeGreaterThan(mFeatures.lipWidth);
    });
  });

  describe('Morph Target Features', () => {
    test('should map morph targets to articulatory features', () => {
      const jawOpenFeatures = matrix.getMorphTargetFeatures('jawOpen');
      const mouthSmileFeatures = matrix.getMorphTargetFeatures('mouthSmile');

      expect(jawOpenFeatures.jawOpening).toBe(1.0);
      expect(mouthSmileFeatures.lipWidth).toBeGreaterThan(0);
    });
  });

  describe('Coarticulation Matrix', () => {
    test('should calculate coarticulation factors', () => {
      const factor = matrix.coarticulationMatrix['p']['aa']; // Plosive to vowel

      expect(factor).toBeGreaterThan(0);
      expect(factor).toBeLessThanOrEqual(1.0);
    });

    test('should have higher coarticulation for dissimilar phonemes', () => {
      const similarFactor = matrix.coarticulationMatrix['aa']['ae']; // Similar vowels
      const dissimilarFactor = matrix.coarticulationMatrix['p']['s']; // Different consonants

      expect(dissimilarFactor).toBeGreaterThanOrEqual(similarFactor);
    });
  });
});