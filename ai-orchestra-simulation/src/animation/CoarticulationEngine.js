/**
 * CoarticulationEngine - Advanced phoneme transition and blending system
 *
 * Implements sophisticated coarticulation effects for smooth phoneme transitions,
 * look-ahead processing, and context-aware intensity modulation.
 *
 * Features:
 * - Look-ahead phoneme processing (2-3 phonemes ahead)
 * - Transition smoothing with spline interpolation
 * - Context-dependent coarticulation rules
 * - Articulatory feature assimilation
 * - Phoneme cluster optimization
 */

import { Logger } from '../utils/Logger.js';

export class CoarticulationEngine {
  constructor(config = {}) {
    this.logger = this.initializeLogger();

    this.config = {
      lookAheadPhonemes: config.lookAheadPhonemes || 3,
      transitionDuration: config.transitionDuration || 150, // ms
      smoothingFactor: config.smoothingFactor || 0.7,
      assimilationStrength: config.assimilationStrength || 0.6,
      clusterOptimization: config.clusterOptimization !== false,
      ...config,
    };

    // Coarticulation rules database
    this.coarticulationRules = this.initializeCoarticulationRules();

    // Transition buffers
    this.transitionBuffer = new Map();
    this.lookAheadBuffer = [];

    // Articulatory assimilation patterns
    this.assimilationPatterns = this.initializeAssimilationPatterns();

    this.logger.log('INFO', 'CoarticulationEngine initialized', {
      lookAhead: this.config.lookAheadPhonemes,
      transitionDuration: this.config.transitionDuration,
      features: ['look-ahead', 'smoothing', 'assimilation', 'clustering'],
    });
  }

  /**
   * Initialize logger with fallback
   */
  initializeLogger() {
    try {
      return new Logger();
    } catch (error) {
      return {
        log: (category, message, data) => console.log(`[${category}] ${message}`, data || ''),
      };
    }
  }

  /**
   * Initialize coarticulation rules for phoneme transitions
   */
  initializeCoarticulationRules() {
    const rules = {};

    // Vowel-to-vowel transitions (diphthongs and smooth gliding)
    const vowels = ['aa', 'ae', 'ah', 'ao', 'ee', 'eh', 'er', 'ih', 'iy', 'oh', 'ow', 'oy', 'uh', 'uw'];

    vowels.forEach(fromVowel => {
      vowels.forEach(toVowel => {
        if (fromVowel !== toVowel) {
          rules[`${fromVowel}->${toVowel}`] = {
            type: 'vowel_glide',
            smoothingFactor: 0.8,
            transitionType: 'smooth',
            duration: 120,
          };
        }
      });
    });

    // Consonant-to-vowel transitions (release bursts)
    const consonants = ['b', 'ch', 'd', 'f', 'g', 'hh', 'jh', 'k', 'l', 'm', 'n', 'ng', 'p', 'r', 's', 'sh', 't', 'th', 'v', 'w', 'y', 'z', 'zh'];

    consonants.forEach(consonant => {
      vowels.forEach(vowel => {
        rules[`${consonant}->${vowel}`] = {
          type: 'cv_transition',
          smoothingFactor: 0.6,
          transitionType: 'burst_release',
          duration: 80,
        };
      });
    });

    // Vowel-to-consonant transitions (anticipatory coarticulation)
    vowels.forEach(vowel => {
      consonants.forEach(consonant => {
        rules[`${vowel}->${consonant}`] = {
          type: 'vc_transition',
          smoothingFactor: 0.5,
          transitionType: 'anticipatory',
          duration: 100,
        };
      });
    });

    // Consonant clusters (assimilation effects)
    const similarConsonants = {
      'labial': ['b', 'p', 'm'],
      'dental': ['d', 't', 'n', 'l'],
      'velar': ['g', 'k', 'ng'],
      'fricative': ['f', 'v', 's', 'z', 'sh', 'zh', 'th'],
    };

    Object.keys(similarConsonants).forEach(place => {
      const consonants = similarConsonants[place];
      consonants.forEach(fromCons => {
        consonants.forEach(toCons => {
          if (fromCons !== toCons) {
            rules[`${fromCons}->${toCons}`] = {
              type: 'consonant_assimilation',
              smoothingFactor: 0.9,
              transitionType: 'assimilatory',
              duration: 60,
              assimilationStrength: 0.8,
            };
          }
        });
      });
    });

    return rules;
  }

  /**
   * Initialize articulatory assimilation patterns
   */
  initializeAssimilationPatterns() {
    return {
      // Place assimilation (bilabial to labiodental, etc.)
      place: {
        'b->f': { strength: 0.7, features: ['lipProtrusion'] },
        'p->f': { strength: 0.8, features: ['lipProtrusion'] },
        'd->th': { strength: 0.6, features: ['tongueHeight'] },
        't->th': { strength: 0.7, features: ['tongueHeight'] },
      },

      // Manner assimilation (stop to fricative, etc.)
      manner: {
        'b->v': { strength: 0.5, features: ['lipCompression'] },
        'd->z': { strength: 0.5, features: ['tongueHeight'] },
        'g->gh': { strength: 0.4, features: ['tongueBackness'] },
      },

      // Voicing assimilation (voiced to voiceless, etc.)
      voicing: {
        'b->p': { strength: 0.6, features: ['lipCompression'] },
        'd->t': { strength: 0.6, features: ['tongueHeight'] },
        'g->k': { strength: 0.6, features: ['tongueBackness'] },
        'v->f': { strength: 0.5, features: ['lipWidth'] },
        'z->s': { strength: 0.5, features: ['tongueHeight'] },
      },
    };
  }

  /**
   * Process phoneme sequence with coarticulation effects
   */
  processPhonemeSequence(phonemeSequence, timingData = {}) {
    if (!phonemeSequence || phonemeSequence.length === 0) {
      return [];
    }

    const processedSequence = [];
    const lookAheadBuffer = this.buildLookAheadBuffer(phonemeSequence);

    for (let i = 0; i < phonemeSequence.length; i++) {
      const currentPhoneme = phonemeSequence[i];
      const context = this.buildContext(i, phonemeSequence, lookAheadBuffer, timingData);

      const processedPhoneme = this.applyCoarticulation(currentPhoneme, context);
      processedSequence.push(processedPhoneme);
    }

    this.logger.log('INFO', 'Processed phoneme sequence with coarticulation', {
      inputLength: phonemeSequence.length,
      outputLength: processedSequence.length,
    });

    return processedSequence;
  }

  /**
   * Build look-ahead buffer for anticipatory coarticulation
   */
  buildLookAheadBuffer(phonemeSequence) {
    const buffer = [];

    for (let i = 0; i < phonemeSequence.length; i++) {
      const lookAhead = [];

      for (let j = 1; j <= this.config.lookAheadPhonemes; j++) {
        if (i + j < phonemeSequence.length) {
          lookAhead.push({
            phoneme: phonemeSequence[i + j],
            distance: j,
            weight: Math.max(0, 1 - (j * 0.3)), // Decreasing weight with distance
          });
        }
      }

      buffer.push(lookAhead);
    }

    return buffer;
  }

  /**
   * Build context for current phoneme
   */
  buildContext(index, phonemeSequence, lookAheadBuffer, timingData) {
    return {
      index,
      previousPhoneme: index > 0 ? phonemeSequence[index - 1] : null,
      nextPhoneme: index < phonemeSequence.length - 1 ? phonemeSequence[index + 1] : null,
      lookAhead: lookAheadBuffer[index] || [],
      timing: timingData[index] || {},
      sequenceLength: phonemeSequence.length,
      position: index / phonemeSequence.length, // 0 to 1
    };
  }

  /**
   * Apply coarticulation effects to phoneme
   */
  applyCoarticulation(phoneme, context) {
    let processedPhoneme = { ...phoneme };

    // Apply transition smoothing
    processedPhoneme = this.applyTransitionSmoothing(processedPhoneme, context);

    // Apply anticipatory coarticulation
    processedPhoneme = this.applyAnticipatoryCoarticulation(processedPhoneme, context);

    // Apply perseveratory coarticulation
    processedPhoneme = this.applyPerseveratoryCoarticulation(processedPhoneme, context);

    // Apply assimilation effects
    processedPhoneme = this.applyAssimilationEffects(processedPhoneme, context);

    // Apply cluster optimization
    if (this.config.clusterOptimization) {
      processedPhoneme = this.applyClusterOptimization(processedPhoneme, context);
    }

    return processedPhoneme;
  }

  /**
   * Apply transition smoothing between phonemes
   */
  applyTransitionSmoothing(phoneme, context) {
    const processed = { ...phoneme };

    if (!context.previousPhoneme || !context.nextPhoneme) {
      return processed;
    }

    const transitionKey = `${context.previousPhoneme}->${phoneme}`;
    const rule = this.coarticulationRules[transitionKey];

    if (rule) {
      // Apply smoothing factor to intensity values
      if (processed.intensities) {
        Object.keys(processed.intensities).forEach(target => {
          const originalIntensity = processed.intensities[target];
          processed.intensities[target] = this.smoothTransition(
            originalIntensity,
            rule.smoothingFactor,
            context.position
          );
        });
      }

      // Adjust timing based on transition type
      if (processed.timing) {
        processed.timing.duration = rule.duration;
        processed.timing.transitionType = rule.transitionType;
      }
    }

    return processed;
  }

  /**
   * Apply anticipatory coarticulation (look-ahead effects)
   */
  applyAnticipatoryCoarticulation(phoneme, context) {
    const processed = { ...phoneme };

    if (context.lookAhead.length === 0) {
      return processed;
    }

    // Calculate anticipatory influence
    let totalInfluence = 0;
    const influenceFactors = {};

    context.lookAhead.forEach(lookAheadItem => {
      const influence = this.calculateAnticipatoryInfluence(phoneme, lookAheadItem);
      const weightedInfluence = influence * lookAheadItem.weight;

      Object.keys(weightedInfluence).forEach(feature => {
        influenceFactors[feature] = (influenceFactors[feature] || 0) + weightedInfluence[feature];
      });

      totalInfluence += Math.abs(weightedInfluence);
    });

    // Apply anticipatory adjustments
    if (processed.intensities && totalInfluence > 0) {
      Object.keys(processed.intensities).forEach(target => {
        const adjustment = this.calculateIntensityAdjustment(target, influenceFactors);
        processed.intensities[target] *= (1 + adjustment * 0.3); // Subtle anticipatory effect
      });
    }

    return processed;
  }

  /**
   * Apply perseveratory coarticulation (carry-over from previous phoneme)
   */
  applyPerseveratoryCoarticulation(phoneme, context) {
    const processed = { ...phoneme };

    if (!context.previousPhoneme) {
      return processed;
    }

    const transitionKey = `${context.previousPhoneme}->${phoneme}`;
    const rule = this.coarticulationRules[transitionKey];

    if (rule && rule.type === 'vc_transition') {
      // Vowel-to-consonant carry-over effects
      if (processed.intensities) {
        Object.keys(processed.intensities).forEach(target => {
          // Reduce intensity for perseveratory coarticulation
          processed.intensities[target] *= (1 - rule.smoothingFactor * 0.2);
        });
      }
    }

    return processed;
  }

  /**
   * Apply assimilation effects for similar phonemes
   */
  applyAssimilationEffects(phoneme, context) {
    const processed = { ...phoneme };

    if (!context.previousPhoneme) {
      return processed;
    }

    const transitionKey = `${context.previousPhoneme}->${phoneme}`;
    const assimilation = this.findAssimilationPattern(transitionKey);

    if (assimilation && processed.intensities) {
      Object.keys(processed.intensities).forEach(target => {
        const adjustment = this.calculateAssimilationAdjustment(target, assimilation);
        processed.intensities[target] *= (1 + adjustment * assimilation.strength);
      });
    }

    return processed;
  }

  /**
   * Apply cluster optimization for consonant clusters
   */
  applyClusterOptimization(phoneme, context) {
    const processed = { ...phoneme };

    // Check if this is part of a consonant cluster
    const isClusterStart = this.isConsonant(phoneme) &&
                          context.nextPhoneme &&
                          this.isConsonant(context.nextPhoneme);

    const isClusterMiddle = context.previousPhoneme &&
                           this.isConsonant(context.previousPhoneme) &&
                           context.nextPhoneme &&
                           this.isConsonant(context.nextPhoneme);

    if (isClusterStart || isClusterMiddle) {
      // Reduce overlap in consonant clusters
      if (processed.intensities) {
        Object.keys(processed.intensities).forEach(target => {
          processed.intensities[target] *= 0.85; // Reduce intensity in clusters
        });
      }

      // Adjust timing for cluster articulation
      if (processed.timing) {
        processed.timing.duration *= 0.9; // Faster articulation in clusters
      }
    }

    return processed;
  }

  /**
   * Calculate anticipatory influence from look-ahead phoneme
   */
  calculateAnticipatoryInfluence(currentPhoneme, lookAheadItem) {
    const influence = {};

    // Vowels anticipate lip rounding/protrusion
    if (this.isVowel(lookAheadItem.phoneme)) {
      if (lookAheadItem.phoneme.includes('w') || lookAheadItem.phoneme.includes('ow')) {
        influence.lipProtrusion = 0.3;
      }
      if (lookAheadItem.phoneme.includes('oy') || lookAheadItem.phoneme.includes('ee')) {
        influence.lipWidth = 0.2;
      }
    }

    // Consonants anticipate articulatory position
    if (this.isConsonant(lookAheadItem.phoneme)) {
      if (['b', 'p', 'm'].includes(lookAheadItem.phoneme)) {
        influence.lipCompression = 0.4;
      }
      if (['f', 'v'].includes(lookAheadItem.phoneme)) {
        influence.lipWidth = -0.2;
      }
    }

    return influence;
  }

  /**
   * Check if phoneme is a vowel
   */
  isVowel(phoneme) {
    const vowels = ['aa', 'ae', 'ah', 'ao', 'ee', 'eh', 'er', 'ih', 'iy', 'oh', 'ow', 'oy', 'uh', 'uw'];
    return vowels.includes(phoneme);
  }

  /**
   * Check if phoneme is a consonant
   */
  isConsonant(phoneme) {
    return !this.isVowel(phoneme) && phoneme !== 'sil' && phoneme !== 'pau';
  }

  /**
   * Calculate intensity adjustment based on articulatory features
   */
  calculateIntensityAdjustment(target, influenceFactors) {
    // Map morph targets to affected features
    const targetFeatureMap = {
      mouthPucker: ['lipProtrusion'],
      mouthFunnel: ['lipProtrusion'],
      mouthClose: ['lipCompression'],
      mouthSmile: ['lipWidth'],
      mouthStretch_L: ['lipWidth'],
      mouthStretch_R: ['lipWidth'],
    };

    const relevantFeatures = targetFeatureMap[target] || [];
    let totalAdjustment = 0;

    relevantFeatures.forEach(feature => {
      if (influenceFactors[feature]) {
        totalAdjustment += influenceFactors[feature];
      }
    });

    return totalAdjustment;
  }

  /**
   * Find assimilation pattern for transition
   */
  findAssimilationPattern(transitionKey) {
    // Check all assimilation categories
    for (const category of Object.keys(this.assimilationPatterns)) {
      if (this.assimilationPatterns[category][transitionKey]) {
        return this.assimilationPatterns[category][transitionKey];
      }
    }
    return null;
  }

  /**
   * Calculate assimilation adjustment for morph target
   */
  calculateAssimilationAdjustment(target, assimilation) {
    // Simplified: apply assimilation strength to relevant targets
    const assimilatoryTargets = [
      'mouthClose', 'mouthFunnel', 'mouthPucker',
      'mouthSmile', 'mouthStretch_L', 'mouthStretch_R'
    ];

    return assimilatoryTargets.includes(target) ? assimilation.strength * 0.5 : 0;
  }

  /**
   * Smooth transition using spline interpolation
   */
  smoothTransition(intensity, smoothingFactor, position) {
    // Simple easing function for smooth transitions
    const easedPosition = this.easeInOutQuad(position);
    return intensity * (1 - smoothingFactor) + (intensity * smoothingFactor) * easedPosition;
  }

  /**
   * Easing function for smooth transitions
   */
  easeInOutQuad(t) {
    return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
  }

  /**
   * Get coarticulation factors for morph targets
   */
  getCoarticulationFactors(phoneme, context) {
    const factors = {
      primary: 1.0,
      secondary: 1.0,
      tertiary: 1.0,
    };

    if (!context.previousPhoneme || !context.nextPhoneme) {
      return factors;
    }

    const transitionKey = `${context.previousPhoneme}->${phoneme}`;
    const rule = this.coarticulationRules[transitionKey];

    if (rule) {
      // Apply smoothing factor
      const smoothingMultiplier = 1 - rule.smoothingFactor * 0.3;
      factors.primary *= smoothingMultiplier;
      factors.secondary *= smoothingMultiplier;
      factors.tertiary *= smoothingMultiplier;
    }

    // Apply assimilation effects
    const assimilation = this.findAssimilationPattern(transitionKey);
    if (assimilation) {
      const assimilationMultiplier = 1 + assimilation.strength * 0.2;
      factors.primary *= assimilationMultiplier;
      factors.secondary *= assimilationMultiplier;
      factors.tertiary *= assimilationMultiplier;
    }

    return factors;
  }

  /**
   * Get coarticulation statistics
   */
  getStatistics() {
    return {
      rulesCount: Object.keys(this.coarticulationRules).length,
      assimilationPatterns: Object.keys(this.assimilationPatterns).length,
      lookAheadBuffer: this.lookAheadBuffer.length,
      transitionBuffer: this.transitionBuffer.size,
      config: this.config,
    };
  }

  /**
   * Reset engine state
   */
  reset() {
    this.transitionBuffer.clear();
    this.lookAheadBuffer = [];
    this.logger.log('INFO', 'CoarticulationEngine reset');
  }

  /**
   * Export engine configuration and rules
   */
  exportConfiguration() {
    return {
      config: this.config,
      coarticulationRules: this.coarticulationRules,
      assimilationPatterns: this.assimilationPatterns,
      statistics: this.getStatistics(),
    };
  }
}

export default CoarticulationEngine;
