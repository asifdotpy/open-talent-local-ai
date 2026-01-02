/**
 * PhonemeIntensityMatrix - Dynamic intensity calculation engine for phoneme animations
 *
 * Provides intelligent intensity modulation based on audio features, prosody, and emotional context.
 * Implements coarticulation effects and adaptive intensity scaling for realistic lip-sync.
 *
 * Features:
 * - Audio amplitude-based intensity scaling
 * - Prosodic feature integration (pitch, stress, speaking rate)
 * - Emotional expression modulation
 * - Coarticulation blending between phonemes
 * - Adaptive learning from user feedback
 */

import { Logger } from '../utils/Logger.js';
import SIMDHelper from '../utils/SIMDHelper.js';

export class PhonemeIntensityMatrix {
  constructor(config = {}) {
    // Initialize logger safely
    try {
      this.logger = new Logger();
    } catch (error) {
      // Fallback logger for testing environments
      this.logger = {
        log: (...args) => console.log('[LOG]', ...args),
        debug: (...args) => console.debug('[DEBUG]', ...args),
        error: (...args) => console.error('[ERROR]', ...args),
      };
    }

    this.config = {
      baseIntensityRange: config.baseIntensityRange || [0.1, 1.0],
      amplitudeSensitivity: config.amplitudeSensitivity || 0.8,
      prosodyWeight: config.prosodyWeight || 0.6,
      emotionWeight: config.emotionWeight || 0.4,
      coarticulationLookahead: config.coarticulationLookahead || 2,
      adaptiveLearning: config.adaptiveLearning !== false,
      ...config,
    };

    // Initialize SIMD helper for hardware acceleration
    this.simdHelper = new SIMDHelper();

    // Base intensity matrix: phoneme -> morph target -> base intensity
    this.baseIntensityMatrix = this.initializeBaseIntensityMatrix();

    // Dynamic modifiers
    this.audioModifiers = {
      amplitude: 1.0,
      pitch: 1.0,
      stress: 1.0,
      speakingRate: 1.0,
    };

    this.emotionModifiers = {
      valence: 0.0, // -1 (negative) to +1 (positive)
      arousal: 0.0, // 0 (calm) to 1 (excited)
      dominance: 0.0, // 0 (submissive) to 1 (dominant)
    };

    // Coarticulation transition matrix
    this.coarticulationMatrix = this.initializeCoarticulationMatrix();

    // Adaptive learning data
    this.userPreferences = new Map();
    this.performanceHistory = [];

    this.logger.log('PhonemeIntensityMatrix initialized', {
      matrixSize: `${Object.keys(this.baseIntensityMatrix).length}×${this.getMorphTargetCount()}`,
      features: ['amplitude', 'prosody', 'emotion', 'coarticulation', 'adaptive'],
    });
  }

  /**
   * Initialize base intensity matrix for all phonemes and morph targets
   */
  initializeBaseIntensityMatrix() {
    const matrix = {};

    // Define base intensities for each phoneme across all 52 ARKit morph targets
    const phonemes = [
      'aa', 'ae', 'ah', 'ao', 'ee', 'eh', 'er', 'ih', 'iy', 'oh', 'ow', 'oy', 'uh', 'uw', // vowels
      'b', 'ch', 'd', 'f', 'g', 'hh', 'jh', 'k', 'l', 'm', 'n', 'ng', 'p', 'r', 's', 'sh', 't', 'th', 'v', 'w', 'y', 'z', 'zh', // consonants
      'sil', 'pau' // special
    ];

    const morphTargets = this.getAllMorphTargets();

    phonemes.forEach(phoneme => {
      matrix[phoneme] = {};
      morphTargets.forEach(target => {
        matrix[phoneme][target] = this.calculateBaseIntensity(phoneme, target);
      });
    });

    return matrix;
  }

  /**
   * Calculate base intensity for phoneme-morph target pair (SIMD-optimized)
   */
  calculateBaseIntensity(phoneme, morphTarget) {
    // Primary articulatory features for each phoneme
    const phonemeFeatures = this.getPhonemeFeatures(phoneme);
    const targetFeatures = this.getMorphTargetFeatures(morphTarget);

    // SIMD-optimized feature similarity calculation
    return this.calculateFeatureSimilaritySIMD(phonemeFeatures, targetFeatures);
  }

  /**
   * SIMD-optimized feature similarity calculation
   */
  calculateFeatureSimilaritySIMD(phonemeFeatures, targetFeatures) {
    // Convert feature objects to Float32Array vectors
    const phonemeVector = this.simdHelper.objectToVector(phonemeFeatures);
    const targetVector = this.simdHelper.objectToVector(targetFeatures);

    // Calculate cosine similarity between feature vectors
    const similarity = this.simdHelper.cosineSimilarity(phonemeVector, targetVector);

    // Weight by phoneme feature magnitudes for intensity scaling
    const phonemeWeights = new Float32Array([
      phonemeFeatures.jawOpening || 0,
      phonemeFeatures.lipProtrusion || 0,
      phonemeFeatures.lipWidth || 0,
      phonemeFeatures.tongueHeight || 0,
      phonemeFeatures.tongueBackness || 0,
      phonemeFeatures.lipCompression || 0,
    ]);

    const weightSum = phonemeWeights.reduce((sum, w) => sum + w, 0);
    const intensityWeights = new Float32Array(phonemeWeights.map(w => w / Math.max(weightSum, 1)));

    // Apply weighted similarity using SIMD
    const similarities = phonemeVector.map((_, i) =>
      1 - Math.abs(phonemeVector[i] - targetVector[i])
    );

    return this.simdHelper.weightedSum(intensityWeights, similarities);
  }

  /**
   * Get articulatory features for phoneme
   */
  getPhonemeFeatures(phoneme) {
    const features = {
      // Articulatory dimensions (0-1 scale)
      jawOpening: 0,      // Vertical mouth opening
      lipProtrusion: 0,   // Lip rounding/puckering
      lipWidth: 0,        // Horizontal lip stretching
      tongueHeight: 0,    // Tongue position
      tongueBackness: 0,  // Tongue advancement
      lipCompression: 0,  // Lip pressing together
    };

    // Define features for each phoneme based on IPA characteristics
    const phonemeProfiles = {
      // Vowels - high jaw opening, varied lip shapes
      'aa': { jawOpening: 0.9, lipProtrusion: 0.3, lipWidth: 0.7, tongueHeight: 0.2, tongueBackness: 0.5 },
      'ae': { jawOpening: 0.8, lipProtrusion: 0.1, lipWidth: 0.9, tongueHeight: 0.3, tongueBackness: 0.7 },
      'ah': { jawOpening: 0.7, lipProtrusion: 0.2, lipWidth: 0.6, tongueHeight: 0.4, tongueBackness: 0.5 },
      'ao': { jawOpening: 0.8, lipProtrusion: 0.8, lipWidth: 0.4, tongueHeight: 0.3, tongueBackness: 0.3 },
      'ee': { jawOpening: 0.6, lipProtrusion: 0.1, lipWidth: 0.8, tongueHeight: 0.8, tongueBackness: 0.7 },
      'eh': { jawOpening: 0.5, lipProtrusion: 0.1, lipWidth: 0.7, tongueHeight: 0.6, tongueBackness: 0.6 },
      'er': { jawOpening: 0.4, lipProtrusion: 0.2, lipWidth: 0.5, tongueHeight: 0.7, tongueBackness: 0.4 },
      'ih': { jawOpening: 0.3, lipProtrusion: 0.1, lipWidth: 0.6, tongueHeight: 0.8, tongueBackness: 0.6 },
      'iy': { jawOpening: 0.2, lipProtrusion: 0.1, lipWidth: 0.9, tongueHeight: 0.9, tongueBackness: 0.7 },
      'oh': { jawOpening: 0.7, lipProtrusion: 0.7, lipWidth: 0.5, tongueHeight: 0.5, tongueBackness: 0.3 },
      'ow': { jawOpening: 0.6, lipProtrusion: 0.6, lipWidth: 0.6, tongueHeight: 0.6, tongueBackness: 0.4 },
      'oy': { jawOpening: 0.5, lipProtrusion: 0.4, lipWidth: 0.8, tongueHeight: 0.7, tongueBackness: 0.6 },
      'uh': { jawOpening: 0.4, lipProtrusion: 0.5, lipWidth: 0.4, tongueHeight: 0.5, tongueBackness: 0.2 },
      'uw': { jawOpening: 0.3, lipProtrusion: 0.8, lipWidth: 0.3, tongueHeight: 0.6, tongueBackness: 0.1 },

      // Consonants - varied lip compression and tongue positions
      'b': { jawOpening: 0.1, lipCompression: 0.9, tongueHeight: 0.3, tongueBackness: 0.6 },
      'ch': { jawOpening: 0.2, lipCompression: 0.7, tongueHeight: 0.8, tongueBackness: 0.8 },
      'd': { jawOpening: 0.1, lipCompression: 0.8, tongueHeight: 0.4, tongueBackness: 0.6 },
      'f': { jawOpening: 0.1, lipCompression: 0.6, lipWidth: 0.3, tongueHeight: 0.2, tongueBackness: 0.8 },
      'g': { jawOpening: 0.1, lipCompression: 0.7, tongueHeight: 0.3, tongueBackness: 0.2 },
      'hh': { jawOpening: 0.8, lipWidth: 0.9, tongueHeight: 0.1, tongueBackness: 0.5 },
      'jh': { jawOpening: 0.2, lipCompression: 0.6, tongueHeight: 0.7, tongueBackness: 0.7 },
      'k': { jawOpening: 0.1, lipCompression: 0.8, tongueHeight: 0.3, tongueBackness: 0.1 },
      'l': { jawOpening: 0.3, lipWidth: 0.5, tongueHeight: 0.6, tongueBackness: 0.8 },
      'm': { jawOpening: 0.1, lipCompression: 1.0, tongueHeight: 0.2, tongueBackness: 0.6 },
      'n': { jawOpening: 0.1, lipCompression: 0.8, tongueHeight: 0.4, tongueBackness: 0.6 },
      'ng': { jawOpening: 0.1, lipCompression: 0.7, tongueHeight: 0.2, tongueBackness: 0.2 },
      'p': { jawOpening: 0.1, lipCompression: 1.0, tongueHeight: 0.3, tongueBackness: 0.6 },
      'r': { jawOpening: 0.4, lipProtrusion: 0.3, tongueHeight: 0.5, tongueBackness: 0.4 },
      's': { jawOpening: 0.1, lipCompression: 0.5, lipWidth: 0.4, tongueHeight: 0.7, tongueBackness: 0.8 },
      'sh': { jawOpening: 0.2, lipCompression: 0.4, lipWidth: 0.5, tongueHeight: 0.6, tongueBackness: 0.9 },
      't': { jawOpening: 0.1, lipCompression: 0.9, tongueHeight: 0.4, tongueBackness: 0.6 },
      'th': { jawOpening: 0.1, lipCompression: 0.5, lipWidth: 0.6, tongueHeight: 0.3, tongueBackness: 0.7 },
      'v': { jawOpening: 0.1, lipCompression: 0.4, lipWidth: 0.4, tongueHeight: 0.2, tongueBackness: 0.8 },
      'w': { jawOpening: 0.3, lipProtrusion: 0.6, lipWidth: 0.4, tongueHeight: 0.4, tongueBackness: 0.3 },
      'y': { jawOpening: 0.2, lipWidth: 0.7, tongueHeight: 0.8, tongueBackness: 0.7 },
      'z': { jawOpening: 0.1, lipCompression: 0.4, lipWidth: 0.5, tongueHeight: 0.6, tongueBackness: 0.8 },
      'zh': { jawOpening: 0.2, lipCompression: 0.3, lipWidth: 0.6, tongueHeight: 0.5, tongueBackness: 0.9 },

      // Special phonemes
      'sil': { jawOpening: 0.05, lipCompression: 0.1, lipWidth: 0.1 },
      'pau': { jawOpening: 0.1, lipCompression: 0.2, lipWidth: 0.3 },
    };

    return { ...features, ...(phonemeProfiles[phoneme] || {}) };
  }

  /**
   * Get morph target features
   */
  getMorphTargetFeatures(morphTarget) {
    const features = {
      jawOpening: 0,
      lipProtrusion: 0,
      lipWidth: 0,
      tongueHeight: 0,
      tongueBackness: 0,
      lipCompression: 0,
    };

    // Map ARKit morph targets to articulatory features
    const targetProfiles = {
      jawOpen: { jawOpening: 1.0 },
      jawForward: { jawOpening: 0.3, tongueBackness: -0.2 },
      mouthFunnel: { lipProtrusion: 1.0, lipWidth: -0.3 },
      mouthPucker: { lipProtrusion: 0.8, lipCompression: 0.5 },
      mouthRollUpper: { lipWidth: 0.4, tongueHeight: 0.3 },
      mouthRollLower: { lipWidth: 0.4, tongueHeight: -0.2 },
      mouthClose: { lipCompression: 1.0, jawOpening: -0.5 },
      mouthSmile: { lipWidth: 0.8, jawOpening: 0.2 },
      mouthSmile_L: { lipWidth: 0.6 },
      mouthSmile_R: { lipWidth: 0.6 },
      mouthFrown_L: { lipWidth: 0.3, jawOpening: -0.1 },
      mouthFrown_R: { lipWidth: 0.3, jawOpening: -0.1 },
      mouthUpperUp_L: { jawOpening: 0.1, lipWidth: 0.2 },
      mouthUpperUp_R: { jawOpening: 0.1, lipWidth: 0.2 },
      mouthLowerDown_L: { jawOpening: 0.2, lipWidth: 0.1 },
      mouthLowerDown_R: { jawOpening: 0.2, lipWidth: 0.1 },
      mouthPress_L: { lipCompression: 0.7 },
      mouthPress_R: { lipCompression: 0.7 },
      mouthStretch_L: { lipWidth: 0.6 },
      mouthStretch_R: { lipWidth: 0.6 },
      tongueOut: { tongueHeight: -0.5, tongueBackness: 0.3 },
    };

    return { ...features, ...(targetProfiles[morphTarget] || {}) };
  }

  /**
   * Initialize coarticulation transition matrix (SIMD batch-optimized)
   */
  initializeCoarticulationMatrix() {
    // Define phonemes list (same as in initializeBaseIntensityMatrix)
    const phonemes = [
      'aa', 'ae', 'ah', 'ao', 'ee', 'eh', 'er', 'ih', 'iy', 'oh', 'ow', 'oy', 'uh', 'uw', // vowels
      'b', 'ch', 'd', 'f', 'g', 'hh', 'jh', 'k', 'l', 'm', 'n', 'ng', 'p', 'r', 's', 'sh', 't', 'th', 'v', 'w', 'y', 'z', 'zh', // consonants
      'sil', 'pau' // special
    ];

    const matrix = {};

    // Batch process all phoneme pairs for SIMD optimization
    const phonemeFeatures = {};
    phonemes.forEach(phoneme => {
      phonemeFeatures[phoneme] = this.getPhonemeFeatures(phoneme);
    });

    // Use SIMD batch processing for all coarticulation factors
    const coarticulationFactors = this.simdHelper.batchCoarticulationFactors(
      phonemes.map(p => phonemeFeatures[p])
    );

    let index = 0;
    phonemes.forEach(fromPhoneme => {
      matrix[fromPhoneme] = {};
      phonemes.forEach(toPhoneme => {
        matrix[fromPhoneme][toPhoneme] = coarticulationFactors[index];
        index++;
      });
    });

    return matrix;
  }

  /**
   * Calculate coarticulation factor between phonemes (SIMD-optimized)
   */
  calculateCoarticulationFactor(fromPhoneme, toPhoneme) {
    const fromFeatures = this.getPhonemeFeatures(fromPhoneme);
    const toFeatures = this.getPhonemeFeatures(toPhoneme);

    // SIMD-optimized articulatory distance calculation
    const fromVector = this.simdHelper.objectToVector(fromFeatures);
    const toVector = this.simdHelper.objectToVector(toFeatures);

    const distance = this.simdHelper.euclideanDistance(fromVector, toVector);

    // Convert distance to coarticulation factor (0-1, higher = more blending needed)
    return Math.min(distance * 2, 1.0);
  }

  /**
   * Get all morph target names
   */
  getAllMorphTargets() {
    return [
      'jawOpen', 'jawForward', 'jawLeft', 'jawRight',
      'mouthFunnel', 'mouthPucker', 'mouthLeft', 'mouthRight',
      'mouthRollUpper', 'mouthRollLower', 'mouthShrugUpper', 'mouthShrugLower',
      'mouthClose', 'mouthSmile_L', 'mouthSmile', 'mouthSmile_R',
      'mouthFrown_L', 'mouthFrown_R', 'mouthDimple_L', 'mouthDimple_R',
      'mouthUpperUp_L', 'mouthUpperUp_R', 'mouthLowerDown_L', 'mouthLowerDown_R',
      'mouthPress_L', 'mouthPress_R', 'mouthStretch_L', 'mouthStretch_R',
      'tongueOut', 'browInnerUp', 'browDown_L', 'browDown_R',
      'browOuterUp_L', 'browOuterUp_R', 'eyeLookUp_L', 'eyeLookUp_R',
      'eyeLookDown_L', 'eyeLookDown_R', 'eyeLookIn_L', 'eyeLookIn_R',
      'eyeLookOut_L', 'eyeLookOut_R', 'eyeBlink_L', 'eyeBlink_R',
      'eyeSquint_L', 'eyeSquint_R', 'eyeWide_L', 'eyeWide_R',
      'cheekPuff', 'cheekSquint_L', 'cheekSquint_R',
      'noseSneer_L', 'noseSneer_R'
    ];
  }

  /**
   * Get morph target count
   */
  getMorphTargetCount() {
    return this.getAllMorphTargets().length;
  }

  /**
   * Update audio modifiers from real-time audio analysis
   */
  updateAudioModifiers(audioData) {
    if (!audioData) return;

    // Extract amplitude (RMS)
    if (audioData.amplitude !== undefined) {
      this.audioModifiers.amplitude = this.normalizeAmplitude(audioData.amplitude);
    }

    // Extract pitch
    if (audioData.pitch !== undefined) {
      this.audioModifiers.pitch = this.normalizePitch(audioData.pitch);
    }

    // Extract stress/energy
    if (audioData.stress !== undefined) {
      this.audioModifiers.stress = audioData.stress;
    }

    // Extract speaking rate
    if (audioData.speakingRate !== undefined) {
      this.audioModifiers.speakingRate = this.normalizeSpeakingRate(audioData.speakingRate);
    }

    this.logger.log('INFO', 'Audio modifiers updated', this.audioModifiers);
  }

  /**
   * Update emotion modifiers
   */
  updateEmotionModifiers(emotionData) {
    if (!emotionData) return;

    if (emotionData.valence !== undefined) {
      this.emotionModifiers.valence = Math.max(-1, Math.min(1, emotionData.valence));
    }

    if (emotionData.arousal !== undefined) {
      this.emotionModifiers.arousal = Math.max(0, Math.min(1, emotionData.arousal));
    }

    if (emotionData.dominance !== undefined) {
      this.emotionModifiers.dominance = Math.max(0, Math.min(1, emotionData.dominance));
    }

    this.logger.log('INFO', 'Emotion modifiers updated', this.emotionModifiers);
  }

  /**
   * Calculate dynamic intensity for phoneme with all modifiers (SIMD-optimized)
   */
  calculateDynamicIntensity(phoneme, morphTarget, context = {}) {
    const baseIntensity = this.baseIntensityMatrix[phoneme]?.[morphTarget] || 0;

    // SIMD-optimized modifier application
    const intensity = this.applySIMDModifiers(baseIntensity, phoneme, morphTarget, context);

    // Clamp to valid range
    return Math.max(this.config.baseIntensityRange[0],
                   Math.min(this.config.baseIntensityRange[1], intensity));
  }

  /**
   * Apply all modifiers using SIMD-accelerated calculations
   */
  applySIMDModifiers(baseIntensity, phoneme, morphTarget, context) {
    let intensity = baseIntensity * this.audioModifiers.amplitude;

    // SIMD-optimized prosodic weighting
    const prosodicWeights = new Float32Array([0.3, 0.4, 0.3]); // pitch, stress, speakingRate
    const prosodicValues = new Float32Array([
      this.audioModifiers.pitch,
      this.audioModifiers.stress,
      this.audioModifiers.speakingRate
    ]);

    const prosodicFactor = this.simdHelper.weightedSum(prosodicWeights, prosodicValues);
    intensity *= (1 + this.config.prosodyWeight * (prosodicFactor - 1));

    // SIMD-optimized emotion modifiers
    const emotionFactor = this.calculateEmotionFactorSIMD(morphTarget);
    intensity *= (1 + this.config.emotionWeight * emotionFactor);

    // Apply coarticulation effects
    if (context.previousPhoneme) {
      const coarticulationFactor = this.coarticulationMatrix[context.previousPhoneme]?.[phoneme] || 0;
      intensity *= (1 - coarticulationFactor * 0.3); // Reduce intensity for smoother transitions
    }

    // Apply user preferences
    if (this.config.adaptiveLearning) {
      intensity *= this.getUserPreferenceMultiplier(phoneme, morphTarget);
    }

    return intensity;
  }

  /**
   * SIMD-optimized emotion factor calculation
   */
  calculateEmotionFactorSIMD(morphTarget) {
    const { valence, arousal, dominance } = this.emotionModifiers;

    // Emotion-specific morph target mappings as vectors
    const emotionVectors = {
      mouthSmile: new Float32Array([valence > 0 ? valence * 0.8 : 0, 0, 0]),
      mouthSmile_L: new Float32Array([valence > 0 ? valence * 0.6 : 0, 0, 0]),
      mouthSmile_R: new Float32Array([valence > 0 ? valence * 0.6 : 0, 0, 0]),
      browInnerUp: new Float32Array([valence > 0 ? valence * 0.4 : 0, 0, 0]),

      jawOpen: new Float32Array([0, arousal > 0.5 ? arousal * 0.6 : 0, 0]),
      eyeWide_L: new Float32Array([0, arousal > 0.5 ? arousal * 0.5 : 0, 0]),
      eyeWide_R: new Float32Array([0, arousal > 0.5 ? arousal * 0.5 : 0, 0]),

      mouthFrown_L: new Float32Array([valence < 0 ? -valence * 0.7 : 0, 0, 0]),
      mouthFrown_R: new Float32Array([valence < 0 ? -valence * 0.7 : 0, 0, 0]),
      browDown_L: new Float32Array([valence < 0 ? -valence * 0.5 : 0, 0, 0]),
      browDown_R: new Float32Array([valence < 0 ? -valence * 0.5 : 0, 0, 0]),

      browOuterUp_L: new Float32Array([0, 0, dominance > 0.5 ? dominance * 0.4 : 0]),
      browOuterUp_R: new Float32Array([0, 0, dominance > 0.5 ? dominance * 0.4 : 0]),
    };

    const emotionVector = emotionVectors[morphTarget] || new Float32Array([0, 0, 0]);
    const emotionWeights = new Float32Array([1.0, 1.0, 1.0]); // Equal weighting for valence, arousal, dominance

    return this.simdHelper.weightedSum(emotionWeights, emotionVector);
  }

  /**
   * Calculate emotion factor for morph target
   */
  calculateEmotionFactor(morphTarget) {
    const { valence, arousal, dominance } = this.emotionModifiers;

    // Emotion-specific morph target mappings
    const emotionMappings = {
      // Positive valence (joy, happiness)
      mouthSmile: valence > 0 ? valence * 0.8 : 0,
      mouthSmile_L: valence > 0 ? valence * 0.6 : 0,
      mouthSmile_R: valence > 0 ? valence * 0.6 : 0,
      browInnerUp: valence > 0 ? valence * 0.4 : 0,

      // High arousal (excitement, anger)
      jawOpen: arousal > 0.5 ? arousal * 0.6 : 0,
      eyeWide_L: arousal > 0.5 ? arousal * 0.5 : 0,
      eyeWide_R: arousal > 0.5 ? arousal * 0.5 : 0,

      // Negative valence (sadness, anger)
      mouthFrown_L: valence < 0 ? -valence * 0.7 : 0,
      mouthFrown_R: valence < 0 ? -valence * 0.7 : 0,
      browDown_L: valence < 0 ? -valence * 0.5 : 0,
      browDown_R: valence < 0 ? -valence * 0.5 : 0,

      // High dominance (confidence)
      browOuterUp_L: dominance > 0.5 ? dominance * 0.4 : 0,
      browOuterUp_R: dominance > 0.5 ? dominance * 0.4 : 0,
    };

    return emotionMappings[morphTarget] || 0;
  }

  /**
   * Get user preference multiplier
   */
  getUserPreferenceMultiplier(phoneme, morphTarget) {
    const key = `${phoneme}:${morphTarget}`;
    return this.userPreferences.get(key) || 1.0;
  }

  /**
   * Learn from user feedback
   */
  learnFromFeedback(phoneme, morphTarget, userRating) {
    if (!this.config.adaptiveLearning) return;

    const key = `${phoneme}:${morphTarget}`;
    const current = this.userPreferences.get(key) || 1.0;

    // Simple exponential moving average
    const alpha = 0.1;
    const newMultiplier = current * (1 - alpha) + userRating * alpha;

    this.userPreferences.set(key, newMultiplier);

    // Store performance history
    this.performanceHistory.push({
      timestamp: Date.now(),
      phoneme,
      morphTarget,
      userRating,
      newMultiplier,
    });

    // Keep only recent history
    if (this.performanceHistory.length > 1000) {
      this.performanceHistory = this.performanceHistory.slice(-500);
    }

    this.logger.log('INFO', 'Learned from user feedback', { key, userRating, newMultiplier });
  }

  /**
   * Get intensity profile for phoneme sequence with coarticulation
   */
  getIntensityProfile(phonemeSequence) {
    const profile = [];

    for (let i = 0; i < phonemeSequence.length; i++) {
      const phoneme = phonemeSequence[i];
      const context = {
        previousPhoneme: i > 0 ? phonemeSequence[i - 1] : null,
        nextPhoneme: i < phonemeSequence.length - 1 ? phonemeSequence[i + 1] : null,
        position: i / phonemeSequence.length,
      };

      const intensities = {};
      this.getAllMorphTargets().forEach(target => {
        intensities[target] = this.calculateDynamicIntensity(phoneme, target, context);
      });

      profile.push({
        phoneme,
        intensities,
        context,
      });
    }

    return profile;
  }

  /**
   * Normalize amplitude to intensity multiplier
   */
  normalizeAmplitude(amplitude) {
    // Convert dB or linear amplitude to 0.5-2.0 range
    const normalized = Math.max(0, Math.min(1, amplitude));
    return 0.5 + normalized * 1.5;
  }

  /**
   * Normalize pitch to intensity multiplier
   */
  normalizePitch(pitch) {
    // Higher pitch = more intensity (0.8-1.3 range)
    const normalized = Math.max(80, Math.min(400, pitch)) / 400;
    return 0.8 + normalized * 0.5;
  }

  /**
   * Normalize speaking rate to intensity multiplier
   */
  normalizeSpeakingRate(rate) {
    // Faster speaking = slightly more intensity (0.9-1.2 range)
    const normalized = Math.max(2, Math.min(8, rate)) / 8;
    return 0.9 + normalized * 0.3;
  }

  /**
   * Get matrix statistics
   */
  getStatistics() {
    const phonemes = Object.keys(this.baseIntensityMatrix);
    const morphTargets = this.getAllMorphTargets();

    let totalIntensities = 0;
    let maxIntensity = 0;
    let activeMappings = 0;

    phonemes.forEach(phoneme => {
      morphTargets.forEach(target => {
        const intensity = this.baseIntensityMatrix[phoneme][target];
        totalIntensities += intensity;
        maxIntensity = Math.max(maxIntensity, intensity);
        if (intensity > 0.01) activeMappings++;
      });
    });

    return {
      phonemes: phonemes.length,
      morphTargets: morphTargets.length,
      totalMappings: phonemes.length * morphTargets.length,
      activeMappings,
      averageIntensity: totalIntensities / (phonemes.length * morphTargets.length),
      maxIntensity,
      userPreferencesLearned: this.userPreferences.size,
      performanceHistorySize: this.performanceHistory.length,
      simdEnabled: this.simdHelper.getStats().hasSIMD,
      simdMethod: this.simdHelper.getStats().method,
    };
  }

  /**
   * Benchmark SIMD performance improvements
   */
  async benchmarkSIMD(iterations = 100) {
    const testPhoneme = 'aa';
    const testMorphTarget = 'jawOpen';
    const testContext = { previousPhoneme: 'ah' };

    console.log('Benchmarking SIMD optimizations...');

    // Benchmark dynamic intensity calculation
    const startSIMD = performance.now();
    for (let i = 0; i < iterations; i++) {
      this.calculateDynamicIntensity(testPhoneme, testMorphTarget, testContext);
    }
    const timeSIMD = performance.now() - startSIMD;

    // Benchmark SIMD helper operations
    const benchmark = await this.simdHelper.benchmark(iterations * 10);

    return {
      iterations,
      dynamicIntensityTime: timeSIMD,
      averageDynamicIntensityTime: timeSIMD / iterations,
      vectorOperations: benchmark,
      totalSpeedup: benchmark.speedup,
      hasSIMD: this.simdHelper.getStats().hasSIMD,
    };
  }

  /**
   * Reset adaptive learning data
   */
  resetLearning() {
    this.userPreferences.clear();
    this.performanceHistory = [];
    this.logger.log('Adaptive learning data reset');
  }

  /**
   * Export matrix data for debugging
   */
  exportMatrix() {
    return {
      baseIntensityMatrix: this.baseIntensityMatrix,
      coarticulationMatrix: this.coarticulationMatrix,
      audioModifiers: this.audioModifiers,
      emotionModifiers: this.emotionModifiers,
      userPreferences: Object.fromEntries(this.userPreferences),
      statistics: this.getStatistics(),
    };
  }
}

export default PhonemeIntensityMatrix;
