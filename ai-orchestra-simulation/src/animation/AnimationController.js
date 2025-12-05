import * as THREE from 'three';
import { Logger } from '../utils/Logger.js';
import { PhonemeMapper } from './PhonemeMapper.js';

/**
 * Controls facial animation using vertex-based lip-sync and morph targets
 * Integrates PhonemeMapper for real-time phoneme-based animation
 */
export class AnimationController {
  constructor(mesh, config, speechData, audioObject, meshManager) {
    this.mesh = mesh;
    this.config = config;
    this.speechData = speechData;
    this.audio = audioObject;
    this.meshManager = meshManager;
    this.logger = Logger.getInstance();
    this.clock = new THREE.Clock(false);

    this.animationState = {
      isPlaying: false,
      currentWordIndex: -1,
      lastDisplacement: 0,
    };

    // Performance optimization
    this.frameCount = 0;

    // Mouth animation data
    this.mouthData = null;
    this.lastLoggedTime = 0;
    this.lastDebugLog = 0;
    this.lastUpdateLog = 0;

    // Phase 1: Phoneme mapper for morph target animation
    this.phonemeMapper = new PhonemeMapper(this, {
      smoothingFactor: config.animation?.phonemeSmoothing || 0.1,
      transitionDuration: config.animation?.phonemeTransitionDuration || 50,
    });
    
    this.morphTargetInfluences = this.mesh && this.mesh.morphTargetInfluences 
      ? new Array(this.mesh.morphTargetInfluences.length).fill(0)
      : [];

    this.logger.log('Initialized AnimationController with PhonemeMapper');
  }

  initialize() {
    this.logger.log('ANIMATION', 'Initializing AnimationController...');
    
    // Get mouth tracking data from mesh manager
    this.mouthData = this.meshManager.getMouthData();
    
    if (this.mouthData && this.mouthData.vertexIndices.length > 0) {
      this.logger.log('SUCCESS', `AnimationController initialized with ${this.mouthData.vertexIndices.length} mouth vertices`);
    } else {
      this.logger.log('WARNING', 'No mouth vertices found for animation');
    }
  }

  getDetectionDiagnostics() {
    if (!this.mouthData) {
      return {
        strategy: 'Vertex-based',
        vertexCount: 0,
        confidence: 0,
        issues: ['Mouth tracking not initialized'],
      };
    }
    return {
      strategy: 'Vertex-based',
      vertexCount: this.mouthData.vertexIndices.length,
      confidence: this.mouthData.vertexIndices.length > 0 ? 1 : 0,
      issues: this.mouthData.vertexIndices.length === 0 ? ['No mouth vertices detected'] : [],
    };
  }

  start() {
    if (this.audio) {
      if (!this.audio.isPlaying) {
        this.audio.play();
        this.logger.log('SUCCESS', 'Audio playback started');
      } else {
        this.logger.log('INFO', 'Audio already playing');
      }
      this.logger.log('DEBUG', `Audio state - isPlaying: ${this.audio.isPlaying}, duration: ${this.audio.buffer?.duration || 'unknown'}`);
    } else {
      this.logger.log('WARNING', 'No audio object available');
    }
    
    this.clock.start();
    this.animationState.isPlaying = true;
    this.lastLoggedTime = 0;
    this.logger.log('SUCCESS', 'Animation started');
    return true;
  }

  stop() {
    this.clock.stop();
    this.animationState.isPlaying = false;
    this.resetToOriginalState();
    this.logger.log('SUCCESS', 'Animation stopped');
  }

  update() {
    if (!this.animationState.isPlaying || !this.mesh || !this.mouthData) {
      return;
    }

    const elapsedTime = this.clock.getElapsedTime();
    
    // Throttle updates to reduce performance impact (update every 3 frames)
    if (this.frameCount++ % 3 !== 0) {
      return;
    }
    
    this.updateMouthAnimation(elapsedTime);

    // Phase 1: Update phoneme mapper
    if (this.config.features?.enablePhonemeAnimation) {
      this.phonemeMapper.update();
    }
  }

  updateMouthAnimation(elapsedTime) {
    if (!this.speechData || !this.mouthData.vertexIndices.length) return;

    // Find current word (with caching for performance)
    const currentWordIndex = this.speechData.words.findIndex(
      (w) => elapsedTime >= w.start && elapsedTime <= w.end
    );

    if (currentWordIndex === -1) {
      // No active word, close mouth gradually
      if (this.animationState.lastDisplacement > 0) {
        this.animationState.lastDisplacement *= 0.95; // Gradual close
        this.applyMouthDisplacement(this.animationState.lastDisplacement);
      }
      return;
    }

    // New word started
    if (currentWordIndex !== this.animationState.currentWordIndex) {
      this.animationState.currentWordIndex = currentWordIndex;
      // Removed excessive word logging
    }

    const currentWord = this.speechData.words[currentWordIndex];
    let activePhoneme = null;

    // Find current phoneme within the word
    if (currentWord.phonemes) {
      let phonemeStartTime = currentWord.start;
      for (const phoneme of currentWord.phonemes) {
        const phonemeEndTime = phonemeStartTime + phoneme.duration;
        if (elapsedTime >= phonemeStartTime && elapsedTime <= phonemeEndTime) {
          activePhoneme = phoneme.phoneme;
          break;
        }
        phonemeStartTime = phonemeEndTime;
      }
    }

    // Calculate mouth displacement based on phoneme
    const displacement = this.calculateMouthDisplacement(activePhoneme);
    this.animationState.lastDisplacement = displacement;
    this.applyMouthDisplacement(displacement);

    // Removed excessive phoneme logging
  }

  calculateMouthDisplacement(phoneme) {
    if (!phoneme) return 0;

    // Phoneme to mouth opening mapping (simplified)
    const phonemeMap = {
      'AA': 1.0, 'AE': 0.9, 'AH': 0.7, 'AO': 1.0, 'AW': 0.8,
      'AY': 0.6, 'B': 0.1, 'CH': 0.2, 'D': 0.1, 'DH': 0.3,
      'EH': 0.8, 'ER': 0.6, 'EY': 0.7, 'F': 0.4, 'G': 0.1,
      'HH': 0.2, 'IH': 0.6, 'IY': 0.5, 'JH': 0.2, 'K': 0.1,
      'L': 0.3, 'M': 0.1, 'N': 0.1, 'NG': 0.1, 'OW': 0.9,
      'OY': 0.7, 'P': 0.1, 'R': 0.4, 'S': 0.2, 'SH': 0.3,
      'T': 0.1, 'TH': 0.3, 'UH': 0.7, 'UW': 0.6, 'V': 0.3,
      'W': 0.4, 'Y': 0.5, 'Z': 0.2, 'ZH': 0.3,
      // Additional mappings for speech data
      'A': 0.8, 'E': 0.7, 'I': 0.6, 'O': 0.9, 'U': 0.7
    };

    return (phonemeMap[phoneme] || 0) * this.config.animation.mouthDisplacement;
  }

  applyMouthDisplacement(displacement) {
    const geometry = this.mesh.geometry;
    const positions = geometry.attributes.position.array;

    // Apply displacement to mouth vertices
    let maxChange = 0;
    for (let i = 0; i < this.mouthData.vertexIndices.length; i++) {
      const vertexIndex = this.mouthData.vertexIndices[i];
      const originalPos = this.mouthData.originalPositions[i];
      
      const oldY = positions[vertexIndex * 3 + 1];
      // Move vertex downward (negative Y) for mouth opening
      positions[vertexIndex * 3 + 1] = originalPos.y - displacement;
      const newY = positions[vertexIndex * 3 + 1];
      maxChange = Math.max(maxChange, Math.abs(newY - oldY));
    }

    geometry.attributes.position.needsUpdate = true;

    // Removed excessive vertex displacement logging
  }

  resetToOriginalState() {
    if (!this.mesh || !this.mouthData) return;
    
    const geometry = this.mesh.geometry;
    const positions = geometry.attributes.position.array;

    // Reset mouth vertices to original positions
    for (let i = 0; i < this.mouthData.vertexIndices.length; i++) {
      const vertexIndex = this.mouthData.vertexIndices[i];
      const originalPos = this.mouthData.originalPositions[i];
      
      positions[vertexIndex * 3] = originalPos.x;
      positions[vertexIndex * 3 + 1] = originalPos.y;
      positions[vertexIndex * 3 + 2] = originalPos.z;
    }

    geometry.attributes.position.needsUpdate = true;
    // Removed excessive reset logging
  }

  /**
   * Phase 1: Set morph target weight for phoneme animation
   * @param {number} morphIndex - Morph target index
   * @param {number} value - Target weight (0-1)
   * @param {number} duration - Transition duration in ms
   */
  setMorphTarget(morphIndex, value, duration = 50) {
    if (!this.mesh || !this.mesh.morphTargetInfluences || morphIndex >= this.morphTargetInfluences.length) {
      return;
    }

    const clampedValue = Math.max(0, Math.min(1, value));
    
    // Apply directly for now; could add easing in Phase 2
    this.morphTargetInfluences[morphIndex] = clampedValue;
    this.mesh.morphTargetInfluences[morphIndex] = clampedValue;

    this.logger.debug('Morph target updated', {
      index: morphIndex,
      value: clampedValue.toFixed(2),
      duration,
    });
  }

  /**
   * Phase 1: Reset all morph targets to neutral (0)
   */
  resetMorphTargets() {
    if (!this.mesh || !this.mesh.morphTargetInfluences) {
      return;
    }

    for (let i = 0; i < this.morphTargetInfluences.length; i++) {
      this.morphTargetInfluences[i] = 0;
      this.mesh.morphTargetInfluences[i] = 0;
    }

    this.logger.debug('All morph targets reset to neutral');
  }

  /**
   * Get current morph target weights
   */
  getMorphTargetWeights() {
    return [...this.morphTargetInfluences];
  }

  /**
   * Get phoneme mapper instance
   */
  getPhonemeMapper() {
    return this.phonemeMapper;
  }

  getAnimationState() {
    return { ...this.animationState };
  }

  dispose() {
    this.stop();
  }
}

