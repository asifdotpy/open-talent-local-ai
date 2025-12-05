import * as THREE from 'three';
import { Logger } from '../utils/Logger.js';

/**
 * Controls facial animation using morph target-based lip-sync
 * This approach uses blend shapes instead of vertex manipulation for better performance and compatibility
 */
export class MorphTargetAnimationController {
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

    // Morph target data
    this.morphTargets = null;
    this.mouthMorphTargets = {}; // Multiple mouth-related morph targets
    this.lastLoggedTime = 0;
  }

  initialize() {
    console.log('[CHECKPOINT 1] MorphTargetAnimationController.initialize() called');
    console.log('[CHECKPOINT 1] Mesh:', this.mesh);
    console.log('[CHECKPOINT 1] Has morphTargetInfluences:', !!this.mesh?.morphTargetInfluences);
    console.log('[CHECKPOINT 1] Has morphTargetDictionary:', !!this.mesh?.morphTargetDictionary);
    
    this.logger.log('ANIMATION', 'Initializing MorphTargetAnimationController...');

    // Check if mesh has morph targets
    if (!this.mesh || !this.mesh.morphTargetInfluences || !this.mesh.morphTargetDictionary) {
      this.logger.log('WARNING', 'Mesh does not support morph targets. This model cannot use morph-based lip-sync animation.');
      this.logger.log('INFO', 'To enable lip-sync, you need a 3D model with morph targets (blend shapes) for mouth movements.');
      this.logger.log('INFO', 'Common morph target names: mouth_open, jaw_open, mouthOpen, etc.');
      return false;
    }

    // Find all mouth-related morph targets
    this.morphTargets = this.mesh.morphTargetDictionary;
    this.findMouthMorphTargets();

    if (Object.keys(this.mouthMorphTargets).length === 0) {
      this.logger.log('WARNING', `No mouth morph targets found in model. Available: ${Object.keys(this.morphTargets).join(', ')}`);
      return false;
    }

    console.log('[CHECKPOINT 1] Mouth morph targets found:', this.mouthMorphTargets);
    console.log('[CHECKPOINT 1] Initialization result:', Object.keys(this.mouthMorphTargets).length > 0);
    
    this.logger.log('SUCCESS', `MorphTargetAnimationController initialized with ${Object.keys(this.mouthMorphTargets).length} mouth morph targets`);
    this.logger.log('INFO', `Mouth targets: ${Object.keys(this.mouthMorphTargets).join(', ')}`);
    return true;
  }

  findMouthMorphTargets() {
    // Comprehensive ARKit blendshape mapping for full facial animation support
    const arKitTargets = {
      // Essential mouth targets
      jawOpen: ['jawopen', 'jaw_open', 'mouth_open', 'mouthopen'],
      mouthFunnel: ['mouthfunnel', 'mouth_funnel', 'pucker'],
      mouthSmile: ['mouthsmile', 'mouth_smile', 'smile'],
      mouthClose: ['mouthclose', 'mouth_close', 'closed'],
      
      // Enhanced mouth shapes for better phoneme coverage
      mouthPucker: ['mouthpucker', 'mouth_pucker', 'pucker'],
      mouthRollUpper: ['mouthrollupper', 'mouth_roll_upper', 'roll_upper'],
      mouthRollLower: ['mouthrolllower', 'mouth_roll_lower', 'roll_lower'],
      mouthStretch_L: ['mouthstretch_l', 'mouth_stretch_l', 'stretch_left'],
      mouthStretch_R: ['mouthstretch_r', 'mouth_stretch_r', 'stretch_right'],
      mouthSmile_L: ['mouthsmile_l', 'mouth_smile_l', 'smile_left'],
      mouthSmile_R: ['mouthsmile_r', 'mouth_smile_r', 'smile_right'],
      mouthFrown_L: ['mouthfrown_l', 'mouth_frown_l', 'frown_left'],
      mouthFrown_R: ['mouthfrown_r', 'mouth_frown_r', 'frown_right'],
      
      // Jaw movements
      jawForward: ['jawforward', 'jaw_forward', 'jaw_fwd'],
      jawLeft: ['jawleft', 'jaw_left'],
      jawRight: ['jawright', 'jaw_right'],
      
      // Additional articulatory targets
      mouthUpperUp_L: ['mouthupperup_l', 'mouth_upper_up_l', 'upper_lift_left'],
      mouthUpperUp_R: ['mouthupperup_r', 'mouth_upper_up_r', 'upper_lift_right'],
      mouthLowerDown_L: ['mouthlowardown_l', 'mouth_lower_down_l', 'lower_drop_left'],
      mouthLowerDown_R: ['mouthlowardown_r', 'mouth_lower_down_r', 'lower_drop_right'],
      mouthPress_L: ['mouthpress_l', 'mouth_press_l', 'press_left'],
      mouthPress_R: ['mouthpress_r', 'mouth_press_r', 'press_right'],
      mouthDimple_L: ['mouthdimple_l', 'mouth_dimple_l', 'dimple_left'],
      mouthDimple_R: ['mouthdimple_r', 'mouth_dimple_r', 'dimple_right'],
      
      // Expression targets for emotional context
      browInnerUp: ['browinnerup', 'brow_inner_up', 'inner_brow'],
      browDown_L: ['browdown_l', 'brow_down_l', 'brow_left'],
      browDown_R: ['browdown_r', 'brow_down_r', 'brow_right'],
      browOuterUp_L: ['browouterup_l', 'brow_outer_up_l', 'outer_brow_left'],
      browOuterUp_R: ['browouterup_r', 'brow_outer_up_r', 'outer_brow_right'],
      
      // Eye targets for expressiveness
      eyeWide_L: ['eyewide_l', 'eye_wide_l', 'wide_eye_left'],
      eyeWide_R: ['eyewide_r', 'eye_wide_r', 'wide_eye_right'],
      eyeSquint_L: ['eyesquint_l', 'eye_squint_l', 'squint_left'],
      eyeSquint_R: ['eyesquint_r', 'eye_squint_r', 'squint_right'],
      
      // Cheek targets
      cheekPuff: ['cheekpuff', 'cheek_puff', 'puff'],
      cheekSquint_L: ['cheeksquint_l', 'cheek_squint_l', 'cheek_left'],
      cheekSquint_R: ['cheeksquint_r', 'cheek_squint_r', 'cheek_right'],
      
      // Nose and other facial targets
      noseSneer_L: ['nosesneer_l', 'nose_sneer_l', 'sneer_left'],
      noseSneer_R: ['nosesneer_r', 'nose_sneer_r', 'sneer_right'],
      tongueOut: ['tongueout', 'tongue_out', 'tongue']
    };

    // Find all available morph targets
    for (const [targetName, patterns] of Object.entries(arKitTargets)) {
      for (const [morphName, index] of Object.entries(this.morphTargets)) {
        const lowerMorphName = morphName.toLowerCase();
        
        // Check if this morph target matches any of the patterns
        if (patterns.some(pattern => lowerMorphName.includes(pattern))) {
          this.mouthMorphTargets[targetName] = index;
          this.logger.log('INFO', `Found ${targetName}: "${morphName}" at index ${index}`);
          break; // Found a match, move to next target
        }
      }
    }

    // If no specific targets found, try to find any jaw/mouth related targets as fallback
    if (Object.keys(this.mouthMorphTargets).length === 0) {
      for (const [name, index] of Object.entries(this.morphTargets)) {
        const lowerName = name.toLowerCase();
        if (lowerName.includes('jaw') || lowerName.includes('mouth')) {
          this.mouthMorphTargets['jawOpen'] = index;
          this.logger.log('INFO', `Using fallback mouth target: "${name}" at index ${index}`);
          break;
        }
      }
    }

    // Log comprehensive morph target discovery
    this.logger.log('INFO', `Morph target discovery complete. Found ${Object.keys(this.mouthMorphTargets).length} targets: ${Object.keys(this.mouthMorphTargets).join(', ')}`);
  }

  getDetectionDiagnostics() {
    if (!this.mesh || !this.mesh.morphTargetInfluences) {
      return {
        strategy: 'Morph Target-based',
        morphTargetCount: 0,
        mouthMorphTargets: {},
        confidence: 0,
        issues: ['Mesh does not support morph targets'],
      };
    }

    return {
      strategy: 'Morph Target-based',
      morphTargetCount: this.mesh.morphTargetInfluences.length,
      mouthMorphTargets: this.mouthMorphTargets,
      confidence: Object.keys(this.mouthMorphTargets).length > 0 ? 1 : 0,
      issues: Object.keys(this.mouthMorphTargets).length === 0 ? ['No suitable mouth morph targets found'] : [],
    };
  }

  start() {
    console.log('[CHECKPOINT 2] Animation start() called');
    console.log('[CHECKPOINT 2] HTML Audio element:', this.htmlAudioElement);
    console.log('[CHECKPOINT 2] THREE.Audio object:', this.audio);
    
    // Prefer HTML audio element for reliable playback and synchronization
    if (this.htmlAudioElement) {
      if (this.htmlAudioElement.paused) {
        this.htmlAudioElement.currentTime = 0;
        this.htmlAudioElement.play();
        console.log('[CHECKPOINT 2] HTML audio play() triggered');
        this.logger.log('SUCCESS', 'Audio playback started via HTML audio element');
      } else {
        console.log('[CHECKPOINT 2] HTML audio already playing');
        this.logger.log('INFO', 'Audio already playing');
      }
    } else if (this.audio) {
      // Fallback to THREE.Audio if HTML audio not available
      if (!this.audio.isPlaying) {
        this.audio.play();
        console.log('[CHECKPOINT 2] THREE.Audio play() triggered (fallback)');
        this.logger.log('SUCCESS', 'Audio playback started via THREE.Audio');
      } else {
        this.logger.log('INFO', 'Audio already playing');
      }
    } else {
      this.logger.log('WARNING', 'No audio object available');
    }

    this.clock.start();
    this.animationState.isPlaying = true;
    this.lastLoggedTime = 0;
    
    console.log('[CHECKPOINT 2] Animation state:', this.animationState);
    console.log('[CHECKPOINT 2] Clock started:', this.clock.running);
    
    this.logger.log('SUCCESS', 'Morph target animation started');
    return true;
  }

  stop() {
    this.clock.stop();
    this.animationState.isPlaying = false;
    this.resetToOriginalState();
    this.logger.log('SUCCESS', 'Morph target animation stopped');
  }

  update() {
    if (!this.animationState.isPlaying || !this.mesh || Object.keys(this.mouthMorphTargets).length === 0) {
      if (!this._loggedSkip) {
        console.log('[CHECKPOINT 3] Update() skipped - isPlaying:', this.animationState.isPlaying, 
                    'hasMesh:', !!this.mesh, 'morphTargets:', Object.keys(this.mouthMorphTargets || {}).length);
        this._loggedSkip = true;
      }
      return;
    }
    
    this._frameCount = (this._frameCount || 0) + 1;
    if (this._frameCount % 60 === 0) { // Log every 60 frames (~1 second)
      console.log('[CHECKPOINT 3] Update() running - frame:', this._frameCount, 
                  'elapsed:', this.clock.getElapsedTime().toFixed(2));
    }

    const elapsedTime = this.clock.getElapsedTime();
    this.updateMouthAnimation(elapsedTime);
  }

  updateMouthAnimation(elapsedTime) {
    if (!this.speechData || Object.keys(this.mouthMorphTargets).length === 0) return;
    
    // Use HTML audio element's currentTime for accurate synchronization
    if (this.htmlAudioElement && !this.htmlAudioElement.paused) {
      elapsedTime = this.htmlAudioElement.currentTime;
    }
    
    // CHECKPOINT 4: Audio-Animation Sync
    const audioTime = this.htmlAudioElement?.currentTime || this.audio?.context?.currentTime || 0;
    if (!this._lastSyncLog || Date.now() - this._lastSyncLog > 1000) {
      console.log('[CHECKPOINT 4] Time sync - Elapsed:', elapsedTime.toFixed(2), 
                  'Audio time:', audioTime.toFixed(2));
      this._lastSyncLog = Date.now();
    }

    // Find current word (with caching for performance)
    const currentWordIndex = this.speechData.words.findIndex(
      (w) => elapsedTime >= w.start && elapsedTime <= w.end
    );
    
    // CHECKPOINT 5: Word/Phoneme Detection
    if (currentWordIndex !== this._lastWordIndex && currentWordIndex !== -1) {
      const word = this.speechData.words[currentWordIndex];
      console.log('[CHECKPOINT 5] New word:', word?.word, 'at', elapsedTime.toFixed(2), 
                  'phonemes:', word?.phonemes?.map(p => p.phoneme).join('-'));
      this._lastWordIndex = currentWordIndex;
    }

    if (currentWordIndex === -1) {
      // No active word, close mouth gradually
      const isNumber = typeof this.animationState.lastDisplacement === 'number';
      if (isNumber && this.animationState.lastDisplacement > 0) {
        this.animationState.lastDisplacement *= 0.95; // Gradual close
        this.applyMouthDisplacement(this.animationState.lastDisplacement);
      } else if (!isNumber) {
        // Gradually reduce all morph targets
        const reduced = {};
        for (const key in this.animationState.lastDisplacement) {
          reduced[key] = this.animationState.lastDisplacement[key] * 0.95;
        }
        this.animationState.lastDisplacement = reduced;
        this.applyMouthDisplacement(reduced);
      }
      return;
    }

    // New word started
    if (currentWordIndex !== this.animationState.currentWordIndex) {
      this.animationState.currentWordIndex = currentWordIndex;
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

    // CHECKPOINT 5: Active Phoneme
    if (activePhoneme && activePhoneme !== this._lastPhoneme) {
      console.log('[CHECKPOINT 5] Active phoneme:', activePhoneme);
      this._lastPhoneme = activePhoneme;
    }
    
    // Calculate mouth displacement based on phoneme
    const displacement = this.calculateMouthDisplacement(activePhoneme);
    this.animationState.lastDisplacement = displacement;
    this.applyMouthDisplacement(displacement);
  }

  calculateMouthDisplacement(phoneme) {
    if (!phoneme) {
      return this.getNeutralMorphState();
    }

    // Enhanced phoneme to morph target mapping with comprehensive ARKit support
    const phonemeMap = {
      // Wide open vowels - primarily jaw open with additional shaping
      'AA': { jawOpen: 1.0, mouthFunnel: 0.2, mouthStretch_L: 0.3, mouthStretch_R: 0.3 },
      'AO': { jawOpen: 0.9, mouthFunnel: 0.6, mouthPucker: 0.3 },
      'A': { jawOpen: 0.8, mouthFunnel: 0.1 },
      
      // Medium vowels with smile components
      'AE': { jawOpen: 0.7, mouthSmile: 0.4, mouthStretch_R: 0.2 },
      'AH': { jawOpen: 0.8, mouthRollLower: 0.2 },
      'E': { jawOpen: 0.6, mouthSmile: 0.5, mouthUpperUp_L: 0.2 },
      'EH': { jawOpen: 0.7, mouthSmile_L: 0.3 },
      
      // Rounded vowels - funnel dominant
      'O': { jawOpen: 0.7, mouthFunnel: 1.0, mouthRollUpper: 0.3 },
      'OW': { jawOpen: 0.6, mouthFunnel: 0.8, mouthPucker: 0.4 },
      'U': { jawOpen: 0.5, mouthFunnel: 0.7, mouthPucker: 0.5 },
      'UW': { jawOpen: 0.4, mouthFunnel: 0.8, mouthPucker: 0.6, mouthRollLower: 0.3 },
      
      // Smile-dominant vowels
      'I': { jawOpen: 0.4, mouthSmile: 0.7, mouthUpperUp_R: 0.3 },
      'IY': { jawOpen: 0.3, mouthSmile: 0.8, mouthStretch_R: 0.2, mouthUpperUp_L: 0.2 },
      
      // Consonants - various articulations
      'M': { mouthClose: 1.0, mouthPress_L: 0.3 },
      'P': { mouthClose: 1.0, mouthPress_R: 0.3 },
      'B': { mouthClose: 0.8, mouthPress_L: 0.2 },
      
      // Dental and fricative consonants
      'TH': { jawOpen: 0.3, mouthClose: 0.4, mouthRollLower: 0.3 },
      'F': { mouthClose: 0.6, mouthRollLower: 0.5, mouthPress_R: 0.3 },
      'V': { mouthClose: 0.5, mouthRollLower: 0.4, mouthPress_L: 0.3 },
      
      // Sibilant consonants
      'S': { mouthClose: 0.5, mouthSmile: 0.4, mouthRollLower: 0.3 },
      'Z': { mouthClose: 0.4, mouthSmile: 0.3, mouthRollLower: 0.2 },
      'SH': { mouthClose: 0.6, mouthRollUpper: 0.5, mouthFrown_R: 0.2 },
      'CH': { mouthClose: 0.7, mouthRollUpper: 0.4 },
      
      // Liquid consonants
      'L': { jawOpen: 0.4, mouthSmile_R: 0.3, mouthRollUpper: 0.2 },
      'R': { mouthRollUpper: 0.6, jawOpen: 0.4, mouthSmile_L: 0.2 },
      
      // Nasal consonants
      'N': { jawOpen: 0.3, mouthClose: 0.3 },
      'NG': { jawOpen: 0.2, mouthFrown_L: 0.2 },
      
      // Plosive consonants
      'T': { jawOpen: 0.2, mouthClose: 0.2 },
      'K': { jawOpen: 0.2, mouthFrown_R: 0.1 },
      'G': { jawOpen: 0.2, mouthFrown_L: 0.1 },
      'D': { jawOpen: 0.3, mouthClose: 0.2 },
      
      // Approximant consonants
      'W': { mouthPucker: 0.7, mouthFunnel: 0.5, mouthRollUpper: 0.3 },
      'Y': { mouthSmile: 0.6, jawOpen: 0.4, mouthUpperUp_L: 0.3 },
      'HH': { jawOpen: 0.1, mouthStretch_L: 0.2 },
      
      // Silence and pause
      'SIL': this.getNeutralMorphState(),
      'PAU': { mouthSmile: 0.1, mouthUpperUp_R: 0.05 }
    };

    // Normalize phoneme name
    const normalizedPhoneme = phoneme.toUpperCase();
    const baseValues = phonemeMap[normalizedPhoneme] || this.getNeutralMorphState();
    
    // Scale by config displacement factor
    const scale = this.config.animation.mouthDisplacement;
    const result = {};
    
    for (const [targetName, value] of Object.entries(baseValues)) {
      result[targetName] = value * scale;
    }
    
    // CHECKPOINT 6: Displacement Calculation
    if (phoneme !== this._lastCalcPhoneme) {
      console.log('[CHECKPOINT 6] Displacement for phoneme "' + phoneme + '":', result, 'scale:', scale);
      this._lastCalcPhoneme = phoneme;
    }
    
    return result;
  }

  /**
   * Get neutral morph state (all targets at 0)
   * @returns {object} Neutral morph target values
   */
  getNeutralMorphState() {
    return {
      jawOpen: 0, mouthFunnel: 0, mouthSmile: 0, mouthClose: 0,
      mouthPucker: 0, mouthRollUpper: 0, mouthRollLower: 0,
      mouthStretch_L: 0, mouthStretch_R: 0, mouthSmile_L: 0, mouthSmile_R: 0,
      mouthFrown_L: 0, mouthFrown_R: 0, jawForward: 0, jawLeft: 0, jawRight: 0,
      mouthUpperUp_L: 0, mouthUpperUp_R: 0, mouthLowerDown_L: 0, mouthLowerDown_R: 0,
      mouthPress_L: 0, mouthPress_R: 0, mouthDimple_L: 0, mouthDimple_R: 0
    };
  }

  applyMouthDisplacement(displacements) {
    if (!this.mesh || !this.mesh.morphTargetInfluences) {
      console.error('[CHECKPOINT 7] Cannot apply - no mesh or influences');
      return;
    }
    
    const appliedValues = {};

    // Apply each morph target influence
    for (const [targetName, targetIndex] of Object.entries(this.mouthMorphTargets)) {
      const value = typeof displacements === 'number' ? displacements : (displacements[targetName] || 0);
      const clamped = Math.max(0, Math.min(1, value));
      this.mesh.morphTargetInfluences[targetIndex] = clamped;
      appliedValues[targetName] = clamped;
    }
    
    // CHECKPOINT 7: Morph Target Application
    if (!this._lastApplyLog || Date.now() - this._lastApplyLog > 500) {
      console.log('[CHECKPOINT 7] Applied morph values:', appliedValues);
      console.log('[CHECKPOINT 7] Actual influences (first 10):', 
                  Array.from(this.mesh.morphTargetInfluences).slice(0, 10).map(v => v.toFixed(2)));
      this._lastApplyLog = Date.now();
    }
  }

  resetToOriginalState() {
    if (!this.mesh || !this.mesh.morphTargetInfluences) return;

    // Reset all mouth morph target influences to 0
    for (const targetIndex of Object.values(this.mouthMorphTargets)) {
      this.mesh.morphTargetInfluences[targetIndex] = 0;
    }
  }

  getAnimationState() {
    return { ...this.animationState };
  }

  dispose() {
    this.stop();
  }

  /**
   * Set a specific morph target influence (used by PhonemeMapper)
   * @param {number} targetIndex - Index of the morph target
   * @param {number} intensity - Intensity value (0-1)
   * @param {number} duration - Transition duration in ms
   */
  setMorphTarget(targetIndex, intensity, duration = 100) {
    if (!this.mesh || !this.mesh.morphTargetInfluences) {
      this.logger?.warn('Cannot set morph target: no mesh or influences available');
      return;
    }

    if (targetIndex < 0 || targetIndex >= this.mesh.morphTargetInfluences.length) {
      this.logger?.warn(`Invalid morph target index: ${targetIndex}`);
      return;
    }

    // Smooth transition to new intensity
    const currentValue = this.mesh.morphTargetInfluences[targetIndex];
    const targetValue = Math.max(0, Math.min(1, intensity));
    
    // For now, set immediately (could be enhanced with smooth interpolation)
    this.mesh.morphTargetInfluences[targetIndex] = targetValue;
    
    this.logger?.debug(`Set morph target ${targetIndex} to ${targetValue}`);
  }

  /**
   * Reset all morph targets to neutral position
   */
  resetMorphTargets() {
    if (!this.mesh || !this.mesh.morphTargetInfluences) return;

    // Reset all morph target influences to 0
    for (let i = 0; i < this.mesh.morphTargetInfluences.length; i++) {
      this.mesh.morphTargetInfluences[i] = 0;
    }
    
    this.logger?.debug('Reset all morph targets to neutral');
  }
}