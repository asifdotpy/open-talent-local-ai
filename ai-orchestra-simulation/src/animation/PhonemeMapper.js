/**
 * PhonemeMapper - Maps phonemes to ARKit morph targets (face.glb)
 *
 * Uses 52 named ARKit blendshapes from face.glb for production-grade lip-sync
 * Supports blended morph targets (primary + secondary) for realistic animations
 *
 * Phoneme set: 14 vowels + 23 consonants + 2 special = 39 phonemes
 */

import { Logger } from '../utils/Logger.js';
import { PerformanceMonitor } from '../utils/PerformanceMonitor.js';
import CoarticulationEngine from './CoarticulationEngine.js';
import MorphTargetBlender from './MorphTargetBlender.js';
import PhonemeCacheManager from './PhonemeCacheManager.js';
import PhonemeIntensityMatrix from './PhonemeIntensityMatrix.js';

export class PhonemeMapper {
  constructor(animationController, config = {}) {
    this.animationController = animationController;
    this.logger = new Logger('PhonemeMapper');

    // Initialize Phase 2 advanced components
    this.intensityMatrix = new PhonemeIntensityMatrix({ logger: this.logger });
    this.coarticulationEngine = new CoarticulationEngine({ logger: this.logger });
    this.morphTargetBlender = new MorphTargetBlender({ logger: this.logger });

    // Initialize Phase 3 caching system
    this.cacheManager = new PhonemeCacheManager({
      l1MaxSize: config.l1CacheSize || 100,
      l2MaxSize: config.l2CacheSize || 500,
      l3Enabled: config.enableL3Cache !== false,
      logger: this.logger,
    });

    // Initialize Phase 3 performance monitoring
    this.performanceMonitor = config.performanceMonitor || new PerformanceMonitor(config);

    this.config = {
      smoothingFactor: config.smoothingFactor || 0.1,
      transitionDuration: config.transitionDuration || 50,
      useFaceGLB: config.useFaceGLB !== false,
      ...config,
    };

    // Phoneme to ARKit blendshape mapping (52 named targets)
    // Primary: main mouth shape | Secondary: secondary shape for blending | Tertiary: additional refinement
    this.phonemeMap = {
      // VOWELS (14) - Enhanced with asymmetric and detailed mouth shapes
      'aa': {
        primary: 'jawOpen',
        secondary: 'mouthFunnel',
        tertiary: 'mouthStretch_L',
        primaryIntensity: 1.0,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0.2
      },
      'ae': {
        primary: 'jawOpen',
        secondary: 'mouthSmile',
        tertiary: 'mouthStretch_R',
        primaryIntensity: 0.8,
        secondaryIntensity: 0.5,
        tertiaryIntensity: 0.1
      },
      'ah': {
        primary: 'jawOpen',
        secondary: null,
        tertiary: 'mouthRollLower',
        primaryIntensity: 1.0,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.3
      },
      'ao': {
        primary: 'mouthFunnel',
        secondary: 'jawOpen',
        tertiary: 'mouthPucker',
        primaryIntensity: 0.9,
        secondaryIntensity: 0.6,
        tertiaryIntensity: 0.4
      },
      'ee': {
        primary: 'mouthSmile',
        secondary: 'mouthStretch_L',
        tertiary: 'mouthUpperUp_L',
        primaryIntensity: 0.9,
        secondaryIntensity: 0.5,
        tertiaryIntensity: 0.3
      },
      'eh': {
        primary: 'jawOpen',
        secondary: 'mouthSmile_L',
        tertiary: null,
        primaryIntensity: 0.7,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0
      },
      'er': {
        primary: 'mouthRollUpper',
        secondary: 'jawOpen',
        tertiary: null,
        primaryIntensity: 0.6,
        secondaryIntensity: 0.3,
        tertiaryIntensity: 0
      },
      'ih': {
        primary: 'jawOpen',
        secondary: 'mouthSmile_R',
        tertiary: null,
        primaryIntensity: 0.5,
        secondaryIntensity: 0.3,
        tertiaryIntensity: 0
      },
      'iy': {
        primary: 'mouthSmile',
        secondary: 'mouthUpperUp_R',
        tertiary: 'mouthStretch_R',
        primaryIntensity: 1.0,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0.2
      },
      'oh': {
        primary: 'mouthFunnel',
        secondary: 'jawOpen',
        tertiary: 'mouthRollUpper',
        primaryIntensity: 1.0,
        secondaryIntensity: 0.6,
        tertiaryIntensity: 0.3
      },
      'ow': {
        primary: 'mouthFunnel',
        secondary: 'jawOpen',
        tertiary: 'mouthPucker',
        primaryIntensity: 0.8,
        secondaryIntensity: 0.5,
        tertiaryIntensity: 0.4
      },
      'oy': {
        primary: 'mouthSmile',
        secondary: 'jawOpen',
        tertiary: 'mouthFunnel',
        primaryIntensity: 0.7,
        secondaryIntensity: 0.5,
        tertiaryIntensity: 0.3
      },
      'uh': {
        primary: 'mouthPucker',
        secondary: 'jawOpen',
        tertiary: null,
        primaryIntensity: 0.8,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0
      },
      'uw': {
        primary: 'mouthPucker',
        secondary: 'mouthFunnel',
        tertiary: 'mouthRollLower',
        primaryIntensity: 1.0,
        secondaryIntensity: 0.7,
        tertiaryIntensity: 0.3
      },

      // CONSONANTS (23) - Enhanced with detailed articulatory features
      'b': {
        primary: 'mouthClose',
        secondary: null,
        tertiary: 'mouthPress_L',
        primaryIntensity: 1.0,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.2
      },
      'ch': {
        primary: 'mouthClose',
        secondary: 'jawOpen',
        tertiary: 'mouthRollUpper',
        primaryIntensity: 0.8,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0.3
      },
      'd': {
        primary: 'jawOpen',
        secondary: 'mouthClose',
        tertiary: null,
        primaryIntensity: 0.3,
        secondaryIntensity: 0.2,
        tertiaryIntensity: 0
      },
      'f': {
        primary: 'mouthClose',
        secondary: 'mouthRollLower',
        tertiary: 'mouthPress_R',
        primaryIntensity: 0.7,
        secondaryIntensity: 0.6,
        tertiaryIntensity: 0.3
      },
      'g': {
        primary: 'jawOpen',
        secondary: null,
        tertiary: 'mouthFrown_L',
        primaryIntensity: 0.2,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.1
      },
      'hh': {
        primary: 'jawOpen',
        secondary: null,
        tertiary: 'mouthStretch_L',
        primaryIntensity: 0.1,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.2
      },
      'jh': {
        primary: 'mouthClose',
        secondary: 'jawOpen',
        tertiary: 'mouthSmile_L',
        primaryIntensity: 0.6,
        secondaryIntensity: 0.3,
        tertiaryIntensity: 0.2
      },
      'k': {
        primary: 'jawOpen',
        secondary: null,
        tertiary: 'mouthFrown_R',
        primaryIntensity: 0.15,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.1
      },
      'l': {
        primary: 'jawOpen',
        secondary: 'mouthSmile_R',
        tertiary: 'mouthRollUpper',
        primaryIntensity: 0.4,
        secondaryIntensity: 0.2,
        tertiaryIntensity: 0.1
      },
      'm': {
        primary: 'mouthClose',
        secondary: null,
        tertiary: 'mouthPress_L',
        primaryIntensity: 1.0,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.3
      },
      'n': {
        primary: 'jawOpen',
        secondary: 'mouthClose',
        tertiary: null,
        primaryIntensity: 0.3,
        secondaryIntensity: 0.2,
        tertiaryIntensity: 0
      },
      'ng': {
        primary: 'jawOpen',
        secondary: null,
        tertiary: 'mouthFrown_L',
        primaryIntensity: 0.1,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.2
      },
      'p': {
        primary: 'mouthClose',
        secondary: null,
        tertiary: 'mouthPress_R',
        primaryIntensity: 1.0,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.2
      },
      'r': {
        primary: 'mouthRollUpper',
        secondary: 'jawOpen',
        tertiary: 'mouthSmile_L',
        primaryIntensity: 0.7,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0.2
      },
      's': {
        primary: 'mouthClose',
        secondary: 'mouthSmile',
        tertiary: 'mouthRollLower',
        primaryIntensity: 0.6,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0.3
      },
      'sh': {
        primary: 'mouthClose',
        secondary: 'mouthRollUpper',
        tertiary: 'mouthFrown_R',
        primaryIntensity: 0.7,
        secondaryIntensity: 0.5,
        tertiaryIntensity: 0.2
      },
      't': {
        primary: 'jawOpen',
        secondary: null,
        tertiary: 'mouthClose',
        primaryIntensity: 0.2,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.1
      },
      'th': {
        primary: 'jawOpen',
        secondary: 'mouthClose',
        tertiary: 'mouthRollLower',
        primaryIntensity: 0.5,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0.2
      },
      'v': {
        primary: 'mouthClose',
        secondary: 'mouthRollLower',
        tertiary: 'mouthPress_L',
        primaryIntensity: 0.7,
        secondaryIntensity: 0.5,
        tertiaryIntensity: 0.3
      },
      'w': {
        primary: 'mouthPucker',
        secondary: 'mouthFunnel',
        tertiary: 'mouthRollUpper',
        primaryIntensity: 0.8,
        secondaryIntensity: 0.6,
        tertiaryIntensity: 0.3
      },
      'y': {
        primary: 'mouthSmile',
        secondary: 'jawOpen',
        tertiary: 'mouthUpperUp_L',
        primaryIntensity: 0.6,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0.2
      },
      'z': {
        primary: 'mouthClose',
        secondary: 'mouthSmile',
        tertiary: 'mouthRollLower',
        primaryIntensity: 0.5,
        secondaryIntensity: 0.3,
        tertiaryIntensity: 0.2
      },
      'zh': {
        primary: 'mouthClose',
        secondary: 'mouthRollUpper',
        tertiary: 'mouthFrown_L',
        primaryIntensity: 0.6,
        secondaryIntensity: 0.4,
        tertiaryIntensity: 0.2
      },

      // SPECIAL (2)
      'sil': {
        primary: null,
        secondary: null,
        tertiary: null,
        primaryIntensity: 0,
        secondaryIntensity: 0,
        tertiaryIntensity: 0
      },
      'pau': {
        primary: 'mouthSmile',
        secondary: null,
        tertiary: 'mouthUpperUp_R',
        primaryIntensity: 0.1,
        secondaryIntensity: 0,
        tertiaryIntensity: 0.05
      }
    };

    // ARKit blendshape indices (52 targets in face.glb)
    this.arKitMorphTargets = {
      jawOpen: 24, jawForward: 25, jawLeft: 26, jawRight: 27,
      mouthFunnel: 28, mouthPucker: 29, mouthLeft: 30, mouthRight: 31,
      mouthRollUpper: 32, mouthRollLower: 33, mouthShrugUpper: 34, mouthShrugLower: 35,
      mouthClose: 36, mouthSmile_L: 37, mouthSmile: 38, mouthSmile_R: 38,
      mouthFrown_L: 39, mouthFrown_R: 40, mouthDimple_L: 41, mouthDimple_R: 42,
      mouthUpperUp_L: 43, mouthUpperUp_R: 44, mouthLowerDown_L: 45, mouthLowerDown_R: 46,
      mouthPress_L: 47, mouthPress_R: 48, mouthStretch_L: 49, mouthStretch_R: 50,
      tongueOut: 51, browInnerUp: 0, browDown_L: 1, browDown_R: 2,
      browOuterUp_L: 3, browOuterUp_R: 4, eyeLookUp_L: 5, eyeLookUp_R: 6,
      eyeLookDown_L: 7, eyeLookDown_R: 8, eyeLookIn_L: 9, eyeLookIn_R: 10,
      eyeLookOut_L: 11, eyeLookOut_R: 12, eyeBlink_L: 13, eyeBlink_R: 14,
      eyeSquint_L: 15, eyeSquint_R: 16, eyeWide_L: 17, eyeWide_R: 18,
      cheekPuff: 19, cheekSquint_L: 20, cheekSquint_R: 21,
      noseSneer_L: 22, noseSneer_R: 23
    };

    // Current morphing state
    this.currentPhoneme = 'sil';
    this.targetPhoneme = 'sil';
    this.morphProgress = 0;
    this.lastUpdateTime = Date.now();

    this.logger.log('PhonemeMapper initialized (ARKit + Phase 2 + Phase 3)', {
      phonemesSupported: Object.keys(this.phonemeMap).length,
      morphTargets: Object.keys(this.arKitMorphTargets).length,
      smoothingFactor: this.config.smoothingFactor,
      phase2Enabled: !!(this.intensityMatrix && this.coarticulationEngine && this.morphTargetBlender),
      phase3Enabled: !!this.cacheManager,
    });
  }

  /**
   * Animate phoneme using ARKit blendshapes with Phase 2 dynamic intensity and Phase 3 caching
   * @param {string} phoneme - Phoneme code (e.g., 'aa', 'b', 'sil')
   * @param {number} duration - Duration in milliseconds
   * @param {object} audioContext - Audio context with amplitude, pitch, stress, etc.
   * @param {object} sequenceContext - Context within phoneme sequence
   */
  async animatePhoneme(phoneme, duration = 100, audioContext = {}, sequenceContext = {}) {
    if (!this.phonemeMap[phoneme]) {
      if (this.logger?.warn) this.logger.warn('Unknown phoneme', { phoneme });
      return;
    }

    const mapping = this.phonemeMap[phoneme];
    this.targetPhoneme = phoneme;

    // Update audio modifiers in intensity matrix
    if (audioContext) {
      this.intensityMatrix.updateAudioModifiers(audioContext);
    }

    // Build context for dynamic intensity calculation
    const context = {
      previousPhoneme: sequenceContext.previousPhoneme || this.currentPhoneme,
      nextPhoneme: sequenceContext.nextPhoneme,
      position: sequenceContext.position || 0,
      duration,
      ...sequenceContext,
    };

    // Calculate dynamic intensities using Phase 2 system with Phase 3 caching
    const primaryIntensity = mapping.primary ?
      await this.getCachedIntensity(phoneme, mapping.primary, context) : 0;

    const secondaryIntensity = mapping.secondary ?
      await this.getCachedIntensity(phoneme, mapping.secondary, context) : 0;

    const tertiaryIntensity = mapping.tertiary ?
      await this.getCachedIntensity(phoneme, mapping.tertiary, context) : 0;

    // Apply coarticulation smoothing with caching
    const coarticulationFactors = await this.getCachedCoarticulationFactors(phoneme, context);

    const finalPrimaryIntensity = primaryIntensity * (coarticulationFactors.primary || 1.0);
    const finalSecondaryIntensity = secondaryIntensity * (coarticulationFactors.secondary || 1.0);
    const finalTertiaryIntensity = tertiaryIntensity * (coarticulationFactors.tertiary || 1.0);

    // Use MorphTargetBlender for smooth transitions
    if (this.morphTargetBlender && mapping.primary) {
      const blendTargets = [];

      if (mapping.primary) {
        blendTargets.push({
          name: mapping.primary,
          index: this.arKitMorphTargets[mapping.primary],
          intensity: finalPrimaryIntensity,
          priority: 'primary',
        });
      }

      if (mapping.secondary) {
        blendTargets.push({
          name: mapping.secondary,
          index: this.arKitMorphTargets[mapping.secondary],
          intensity: finalSecondaryIntensity,
          priority: 'secondary',
        });
      }

      if (mapping.tertiary) {
        blendTargets.push({
          name: mapping.tertiary,
          index: this.arKitMorphTargets[mapping.tertiary],
          intensity: finalTertiaryIntensity,
          priority: 'tertiary',
        });
      }

      // Get current morph target values for blending
      const currentValues = {};
      blendTargets.forEach(target => {
        currentValues[target.name] = this.animationController?.getMorphTarget ?
          this.animationController.getMorphTarget(target.index) || 0 : 0;
      });

      // Create target values object
      const targetValues = {};
      blendTargets.forEach(target => {
        targetValues[target.name] = target.intensity;
      });

      // Blend and get result with performance monitoring
      const blendStart = performance.now();
      const blendedValues = this.morphTargetBlender.blendMorphTargets(
        currentValues,
        targetValues,
        duration,
        { blendMode: 'cubic' }
      );
      const blendTime = performance.now() - blendStart;

      // Record blend operation performance
      this.performanceMonitor?.recordBottleneck('blendOperations', blendTime, 5); // 5ms threshold

      // Apply blended values to animation controller
      Object.keys(blendedValues).forEach(targetName => {
        const target = blendTargets.find(t => t.name === targetName);
        if (target && this.animationController?.setMorphTarget) {
          this.animationController.setMorphTarget(
            target.index,
            blendedValues[targetName],
            this.config.transitionDuration
          );
        }
      });
    } else {
      // Fallback to direct animation controller calls (Phase 1 compatibility)
      // Apply primary morph target
      if (mapping.primary && this.animationController?.setMorphTarget) {
        const primaryIndex = this.arKitMorphTargets[mapping.primary];
        if (primaryIndex !== undefined) {
          this.animationController.setMorphTarget(
            primaryIndex,
            finalPrimaryIntensity,
            this.config.transitionDuration
          );
        }
      }

      // Apply secondary morph target for blending
      if (mapping.secondary && this.animationController?.setMorphTarget) {
        const secondaryIndex = this.arKitMorphTargets[mapping.secondary];
        if (secondaryIndex !== undefined) {
          this.animationController.setMorphTarget(
            secondaryIndex,
            finalSecondaryIntensity,
            this.config.transitionDuration
          );
        }
      }

      // Apply tertiary morph target for additional refinement
      if (mapping.tertiary && this.animationController?.setMorphTarget) {
        const tertiaryIndex = this.arKitMorphTargets[mapping.tertiary];
        if (tertiaryIndex !== undefined) {
          this.animationController.setMorphTarget(
            tertiaryIndex,
            finalTertiaryIntensity,
            this.config.transitionDuration
          );
        }
      }
    }

    // Reset all for silence
    if (phoneme === 'sil') {
      this.resetMorphTargets();
    }

    if (this.logger?.debug) {
      this.logger.log('DEBUG', 'Animated phoneme (Phase 2)', {
        phoneme,
        primary: mapping.primary,
        primaryIntensity: finalPrimaryIntensity.toFixed(3),
        secondary: mapping.secondary,
        secondaryIntensity: finalSecondaryIntensity.toFixed(3),
        tertiary: mapping.tertiary,
        tertiaryIntensity: finalTertiaryIntensity.toFixed(3),
        audioContext: audioContext.amplitude ? audioContext.amplitude.toFixed(2) : 'none',
        coarticulationApplied: Object.keys(coarticulationFactors).length > 0,
      });
    }
  }

  /**
   * Batch animate phoneme sequence with Phase 2 enhancements
   * @param {array} phonemeSequence - Array of {phoneme, duration, audioContext?}
   * @param {object} globalAudioContext - Global audio context for the sequence
   */
  async animateSequence(phonemeSequence, globalAudioContext = {}) {
    // Process sequence with coarticulation engine for look-ahead
    const processedSequence = this.coarticulationEngine ?
      this.coarticulationEngine.processPhonemeSequence(phonemeSequence) :
      phonemeSequence;

    for (let i = 0; i < processedSequence.length; i++) {
      const item = processedSequence[i];
      const phoneme = item.phoneme;
      const duration = item.duration || 100;

      // Merge global and per-phoneme audio context
      const audioContext = {
        ...globalAudioContext,
        ...item.audioContext,
      };

      // Build sequence context for coarticulation
      const sequenceContext = {
        previousPhoneme: i > 0 ? processedSequence[i - 1].phoneme : null,
        nextPhoneme: i < processedSequence.length - 1 ? processedSequence[i + 1].phoneme : null,
        position: i / processedSequence.length,
        sequenceLength: processedSequence.length,
        index: i,
      };

      await this.animatePhoneme(phoneme, duration, audioContext, sequenceContext);
      await new Promise(resolve => setTimeout(resolve, duration));
    }
  }

  /**
   * Update animation frame
   */
  update() {
    const now = Date.now();
    const deltaTime = now - this.lastUpdateTime;
    this.lastUpdateTime = now;

    // Smooth transition between phonemes
    if (this.currentPhoneme !== this.targetPhoneme) {
      this.morphProgress += deltaTime / this.config.transitionDuration;
      this.morphProgress = Math.min(this.morphProgress, 1.0);

      if (this.morphProgress >= 1.0) {
        this.currentPhoneme = this.targetPhoneme;
        this.morphProgress = 0;
      }
    }
  }

  /**
   * Reset morph targets to neutral (silence)
   */
  resetMorphTargets() {
    if (this.animationController?.resetMorphTargets) {
      this.animationController.resetMorphTargets();
    }
    this.currentPhoneme = 'sil';
    this.targetPhoneme = 'sil';
    this.morphProgress = 0;
  }

  /**
   * Get current animation state
   */
  getState() {
    return {
      currentPhoneme: this.currentPhoneme,
      targetPhoneme: this.targetPhoneme,
      morphProgress: this.morphProgress.toFixed(2),
      transitionActive: this.currentPhoneme !== this.targetPhoneme,
    };
  }

  /**
   * Parse speech data and extract phonemes
   * @param {object} speechData - {phonemes: [{time, duration, label}, ...]}
   * @returns {array} Formatted phoneme sequence
   */
  parseSpeechData(speechData) {
    if (!speechData || !speechData.phonemes) {
      this.logger.warn('Invalid speech data format');
      return [];
    }

    return speechData.phonemes.map(p => ({
      phoneme: this.normalizePhonemeName(p.label || p.phoneme),
      duration: p.duration || 100,
      time: p.time || 0,
    }));
  }

  /**
   * Normalize phoneme names
   */
  normalizePhonemeName(name) {
    if (!name) return 'sil';

    const normalized = name.toLowerCase().trim().replace(/[^a-z0-9]/g, '');

    const variations = {
      'ae': 'ae', 'aa': 'aa', 'ah': 'ah', 'ao': 'ao',
      'e': 'eh', 'ee': 'ee', 'eh': 'eh', 'er': 'er',
      'i': 'ih', 'ih': 'ih', 'iy': 'iy',
      'o': 'oh', 'oh': 'oh', 'ow': 'ow', 'oy': 'oy',
      'u': 'uh', 'uh': 'uh', 'uw': 'uw',
      'silence': 'sil', 'sil': 'sil', 'pau': 'pau', 'pause': 'pau',
    };

    return variations[normalized] || normalized;
  }

  /**
   * Get supported phonemes
   */
  getSupportedPhonemes() {
    return Object.keys(this.phonemeMap);
  }

  /**
   * Get morph target index for phoneme
   * @param {string} phoneme
   * @returns {number|null}
   */
  getMorphTargetIndex(phoneme) {
    const normalized = this.normalizePhonemeName(phoneme);
    const mapping = this.phonemeMap[normalized];
    if (mapping?.primary) {
      return this.arKitMorphTargets[mapping.primary] || null;
    }
    return null;
  }

  /**
   * Get all morph target indices (primary + secondary + tertiary)
   * @param {string} phoneme
   * @returns {number[]}
   */
  getMorphTargetIndices(phoneme) {
    const normalized = this.normalizePhonemeName(phoneme);
    const mapping = this.phonemeMap[normalized];
    const indices = [];

    if (mapping?.primary) {
      const idx = this.arKitMorphTargets[mapping.primary];
      if (idx !== undefined) indices.push(idx);
    }

    if (mapping?.secondary) {
      const idx = this.arKitMorphTargets[mapping.secondary];
      if (idx !== undefined) indices.push(idx);
    }

    if (mapping?.tertiary) {
      const idx = this.arKitMorphTargets[mapping.tertiary];
      if (idx !== undefined) indices.push(idx);
    }

    return indices;
  }

  /**
   * Get morph target name by index
   * @param {number} index
   * @returns {string|null}
   */
  getMorphTargetName(index) {
    for (const [name, idx] of Object.entries(this.arKitMorphTargets)) {
      if (idx === index) return name;
    }
    return null;
  }

  /**
   * Enable/disable phoneme animation
   */
  setEnabled(enabled) {
    if (!enabled) {
      this.resetMorphTargets();
    }
  }

  /**
   * Adjust smoothing factor
   * @param {number} factor - 0-1
   */
  setSmoothingFactor(factor) {
    this.config.smoothingFactor = Math.max(0, Math.min(1, factor));
    this.logger.log('Smoothing factor updated', { factor: this.config.smoothingFactor });
  }

  /**
   * Update audio modifiers for dynamic intensity calculation (Phase 2)
   * @param {object} audioData - Audio analysis data
   */
  updateAudioModifiers(audioData) {
    if (this.intensityMatrix) {
      this.intensityMatrix.updateAudioModifiers(audioData);
      this.logger.log('DEBUG', 'Audio modifiers updated', audioData);
    }
  }

  /**
   * Update emotion modifiers for dynamic intensity calculation (Phase 2)
   * @param {object} emotionData - Emotion analysis data
   */
  updateEmotionModifiers(emotionData) {
    if (this.intensityMatrix) {
      this.intensityMatrix.updateEmotionModifiers(emotionData);
      this.logger.log('DEBUG', 'Emotion modifiers updated', emotionData);
    }
  }

  /**
   * Learn from user feedback for adaptive intensity (Phase 2)
   * @param {string} phoneme - Phoneme that was animated
   * @param {string} morphTarget - Morph target name
   * @param {number} userRating - User rating (0-1)
   */
  learnFromFeedback(phoneme, morphTarget, userRating) {
    if (this.intensityMatrix) {
      this.intensityMatrix.learnFromFeedback(phoneme, morphTarget, userRating);
      this.logger.log('DEBUG', 'Learned from user feedback', { phoneme, morphTarget, userRating });
    }
  }

  /**
   * Get Phase 2 system status
   */
  getPhase2Status() {
    return {
      intensityMatrix: this.intensityMatrix ? {
        initialized: true,
        statistics: this.intensityMatrix.getStatistics(),
      } : { initialized: false },
      coarticulationEngine: this.coarticulationEngine ? {
        initialized: true,
        statistics: this.coarticulationEngine.getStatistics(),
      } : { initialized: false },
      morphTargetBlender: this.morphTargetBlender ? {
        initialized: true,
        blendState: this.morphTargetBlender.getBlendState(),
      } : { initialized: false },
    };
  }

  /**
   * Reset adaptive learning data (Phase 2)
   */
  resetAdaptiveLearning() {
    if (this.intensityMatrix) {
      this.intensityMatrix.resetLearning();
      this.logger.log('Adaptive learning data reset');
    }
  }

  /**
   * Export Phase 2 system data for debugging
   */
  exportPhase2Data() {
    return {
      intensityMatrix: this.intensityMatrix ? this.intensityMatrix.exportMatrix() : null,
      coarticulationEngine: this.coarticulationEngine ? this.coarticulationEngine.exportConfiguration() : null,
      morphTargetBlender: this.morphTargetBlender ? this.morphTargetBlender.exportState() : null,
    };
  }

  // ===== PHASE 3: CACHING METHODS =====

  /**
   * Get cached dynamic intensity calculation
   * @param {string} phoneme - Phoneme code
   * @param {string} morphTarget - Morph target name
   * @param {object} context - Calculation context
   * @returns {Promise<number>} Cached or calculated intensity
   */
  async getCachedIntensity(phoneme, morphTarget, context) {
    if (!this.cacheManager || !this.intensityMatrix) {
      return this.intensityMatrix.calculateDynamicIntensity(phoneme, morphTarget, context);
    }

    const startTime = performance.now();

    // Generate cache key
    const key = this.cacheManager.generateKey('intensity', {
      phoneme,
      morphTarget,
      context: this.hashContext(context),
    });

    // Try cache first
    const cached = await this.cacheManager.get(key);
    const endTime = performance.now();
    const responseTime = endTime - startTime;

    if (cached !== null) {
      // Cache hit
      this.performanceMonitor?.recordCacheAccess('intensityCache', true, responseTime);
      return cached;
    }

    // Cache miss - calculate and cache
    this.performanceMonitor?.recordCacheAccess('intensityCache', false, responseTime);

    const calculationStart = performance.now();
    const intensity = this.intensityMatrix.calculateDynamicIntensity(phoneme, morphTarget, context);
    const calculationTime = performance.now() - calculationStart;

    // Record bottleneck if calculation is slow
    this.performanceMonitor?.recordBottleneck('matrixCalculations', calculationTime, 10); // 10ms threshold

    await this.cacheManager.set(key, intensity);
    return intensity;
  }

  /**
   * Get cached coarticulation factors
   * @param {string} phoneme - Current phoneme
   * @param {object} context - Sequence context
   * @returns {Promise<object>} Cached or calculated coarticulation factors
   */
  async getCachedCoarticulationFactors(phoneme, context) {
    if (!this.cacheManager || !this.coarticulationEngine) {
      return this.coarticulationEngine ? this.coarticulationEngine.getCoarticulationFactors(phoneme, context) : {};
    }

    const startTime = performance.now();

    // Generate cache key
    const key = this.cacheManager.generateKey('coart', {
      phoneme,
      context: this.hashContext(context),
    });

    // Try cache first
    const cached = await this.cacheManager.get(key);
    const endTime = performance.now();
    const responseTime = endTime - startTime;

    if (cached !== null) {
      // Cache hit
      this.performanceMonitor?.recordCacheAccess('coarticulationCache', true, responseTime);
      return cached;
    }

    // Cache miss - calculate and cache
    this.performanceMonitor?.recordCacheAccess('coarticulationCache', false, responseTime);

    const calculationStart = performance.now();
    const factors = this.coarticulationEngine.getCoarticulationFactors(phoneme, context);
    const calculationTime = performance.now() - calculationStart;

    // Record bottleneck if calculation is slow
    this.performanceMonitor?.recordBottleneck('coarticulationProcessing', calculationTime, 15); // 15ms threshold

    await this.cacheManager.set(key, factors);
    return factors;
  }

  /**
   * Hash context object for cache key generation
   * @param {object} context - Context to hash
   * @returns {string} Hash string
   */
  hashContext(context) {
    // Simple hash for cache key - include only relevant, stable properties
    const relevantKeys = ['previousPhoneme', 'nextPhoneme', 'position', 'duration', 'sequenceLength'];
    const relevantContext = {};

    relevantKeys.forEach(key => {
      if (context[key] !== undefined) {
        relevantContext[key] = context[key];
      }
    });

    return JSON.stringify(relevantContext);
  }

  /**
   * Warm cache with common phoneme computations (Phase 3)
   */
  async warmCache() {
    if (this.cacheManager) {
      await this.cacheManager.warmCache(this);
    }
  }

  /**
   * Get cache statistics (Phase 3)
   */
  getCacheStats() {
    return this.cacheManager ? this.cacheManager.getStats() : null;
  }

  /**
   * Clear all caches (Phase 3)
   */
  async clearCache() {
    if (this.cacheManager) {
      await this.cacheManager.clear();
    }
  }

  /**
   * Get Phase 3 system status
   */
  getPhase3Status() {
    return {
      cacheManager: this.cacheManager ? {
        initialized: true,
        stats: this.cacheManager.getStats(),
      } : { initialized: false },
      performanceMonitor: this.performanceMonitor ? {
        initialized: true,
        report: this.performanceMonitor.getPerformanceReport(),
      } : { initialized: false },
    };
  }
}

export default PhonemeMapper;
