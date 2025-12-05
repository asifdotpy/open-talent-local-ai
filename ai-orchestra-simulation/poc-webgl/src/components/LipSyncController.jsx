/**
 * LipSyncController Component
 * Manages phoneme-to-viseme mapping and morph target animation with interpolation
 */

import { useFrame } from '@react-three/fiber';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useInterviewStore } from '../stores/interviewStore';

// ============================================================================
// DEBUGGING & VISUALIZATION
// ============================================================================

/**
 * Debug overlay for lip-sync development
 */
function LipSyncDebugOverlay({ faceMesh, currentPhoneme, targetWeights, currentWeights, emotion, speakingRate, isSilent }) {
  const [showDebug, setShowDebug] = useState(false);

  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'd' && e.ctrlKey) {
        setShowDebug(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  if (!showDebug) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 10,
      right: 10,
      background: 'rgba(0,0,0,0.8)',
      color: 'white',
      padding: '10px',
      borderRadius: '8px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 10000,
      maxWidth: '300px'
    }}>
      <div style={{ marginBottom: '8px', fontWeight: 'bold' }}>
        Lip-Sync Debug (Ctrl+D to toggle)
      </div>
      <div>Current Phoneme: {currentPhoneme?.phoneme || 'none'}</div>
      <div>Face Mesh: {faceMesh?.name || 'none'}</div>
      <div>Oculus Visemes Available: {faceMesh?.morphTargetDictionary?.viseme_sil !== undefined ? 'yes' : 'no'}</div>
      <div>ARKit Shapes Available: {faceMesh?.morphTargetDictionary?.jawOpen !== undefined ? 'yes' : 'no'}</div>
      <div>Total Morph Targets: {faceMesh?.morphTargetDictionary ? Object.keys(faceMesh.morphTargetDictionary).length : 0}</div>

      <div style={{ marginTop: '8px', fontSize: '10px' }}>
        <div>All Morph Targets:</div>
        {faceMesh?.morphTargetDictionary ? (
          <div style={{ maxHeight: '100px', overflowY: 'auto' }}>
            {Object.keys(faceMesh.morphTargetDictionary).map(key => (
              <div key={key} style={{ marginLeft: '8px' }}>
                {key}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ marginLeft: '8px' }}>None</div>
        )}
      </div>
      <div>Emotion: {emotion || 'neutral'}</div>
      <div>Speaking Rate: {speakingRate?.toFixed(1) || '0.0'} phon/sec</div>
      <div>Silence: {isSilent ? 'Yes' : 'No'}</div>

      <div style={{ marginTop: '8px', fontSize: '10px' }}>
        <div>Target Weights:</div>
        {Object.entries(targetWeights).map(([key, value]) => (
          <div key={key} style={{ marginLeft: '8px' }}>
            {key}: {value?.toFixed(2)}
          </div>
        ))}
      </div>

      <div style={{ marginTop: '8px', fontSize: '10px' }}>
        <div>Current Weights:</div>
        {Object.entries(currentWeights).map(([key, value]) => (
          <div key={key} style={{ marginLeft: '8px' }}>
            {key}: {value?.toFixed(2)}
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// EASING FUNCTIONS FOR SMOOTH INTERPOLATION
// ============================================================================

/**
 * Smooth easing function for morph target transitions
 */
function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

/**
 * Linear interpolation with easing
 */
function lerp(start, end, factor, easing = true) {
  const t = easing ? easeInOutCubic(factor) : factor;
  return start + (end - start) * t;
}

// ============================================================================
// OBJECT POOLING FOR PERFORMANCE
// ============================================================================

class MorphTargetPool {
  constructor() {
    this.pool = new Map();
    this.maxPoolSize = 50;
  }

  get(key) {
    return this.pool.get(key) || {};
  }

  set(key, value) {
    if (this.pool.size >= this.maxPoolSize) {
      // Remove oldest entry
      const firstKey = this.pool.keys().next().value;
      this.pool.delete(firstKey);
    }
    this.pool.set(key, value);
  }

  clear() {
    this.pool.clear();
  }
}

// ============================================================================
// SILENCE & TRANSITION HANDLING
// ============================================================================

/**
 * Handle silence periods and transitions between phonemes
 */
class SilenceHandler {
  constructor() {
    this.lastPhonemeEndTime = 0;
    this.silenceThreshold = 0.1; // 100ms silence threshold
    this.isInSilence = false;
  }

  /**
   * Check if we're in a silence period and handle transitions
   */
  handleSilence(audioTime, phonemes) {
    if (!phonemes || phonemes.length === 0) {
      this.isInSilence = true;
      return { isSilent: true, silenceDuration: 0, mouthOpen: 0.02 }; // Very subtle breathing motion
    }

    // Find if there's any phoneme active at current time
    const activePhoneme = phonemes.find(p => audioTime >= p.start && audioTime < p.end);

    if (!activePhoneme) {
      // We're in a silence period
      if (!this.isInSilence) {
        this.isInSilence = true;
        this.lastPhonemeEndTime = audioTime;
      }

      const silenceDuration = audioTime - this.lastPhonemeEndTime;
      // Very subtle mouth movement during silence (breathing)
      const breathingMotion = Math.sin(audioTime * 2) * 0.01 + 0.02;

      return {
        isSilent: true,
        silenceDuration: silenceDuration,
        mouthOpen: Math.max(0, breathingMotion),
        shouldNeutralize: silenceDuration > this.silenceThreshold
      };
    } else {
      // We're speaking again
      if (this.isInSilence) {
        this.isInSilence = false;
      }
      return { isSilent: false, silenceDuration: 0, mouthOpen: 0 };
    }
  }
}

/**
 * Adjust viseme weights based on speaking style and emotion
 */
class LipSyncStyler {
  constructor() {
    this.emotionMultipliers = {
      neutral: { intensity: 1.0, speed: 1.0 },
      excited: { intensity: 1.3, speed: 1.2 },
      calm: { intensity: 0.8, speed: 0.9 },
      angry: { intensity: 1.4, speed: 1.1 },
      sad: { intensity: 0.7, speed: 0.8 }
    };

    this.currentEmotion = 'neutral';
  }

  /**
   * Apply emotion-based adjustments to viseme weights
   */
  applyEmotionAdjustment(weights, emotion = 'neutral') {
    const multiplier = this.emotionMultipliers[emotion] || this.emotionMultipliers.neutral;
    const adjusted = {};

    Object.entries(weights).forEach(([morphName, weight]) => {
      let adjustedWeight = weight * multiplier.intensity;

      // Emotion-specific morph adjustments for Oculus visemes
      switch (emotion) {
        case 'excited':
          if (morphName.startsWith('viseme_')) {
            adjustedWeight *= 1.3; // More exaggerated viseme movements
          }
          break;
        case 'calm':
          if (morphName.startsWith('viseme_')) {
            adjustedWeight *= 0.8; // Subtle viseme movements
          }
          break;
        case 'angry':
          if (morphName === 'viseme_CH' || morphName === 'viseme_kk') {
            adjustedWeight *= 1.4; // Emphasize harsh consonants
          }
          break;
        case 'sad':
          if (morphName === 'viseme_O' || morphName === 'viseme_U') {
            adjustedWeight *= 1.2; // Emphasize rounded vowel shapes
          }
          break;
      }

      adjusted[morphName] = Math.max(0, Math.min(1, adjustedWeight));
    });

    return adjusted;
  }

  /**
   * Set current emotion for lip-sync adjustments
   */
  setEmotion(emotion) {
    this.currentEmotion = emotion;
  }
}

/**
 * Enhanced phoneme timing with coarticulation support
 */
class PhonemeScheduler {
  constructor() {
    this.currentPhoneme = null;
    this.nextPhoneme = null;
    this.transitionProgress = 0;
    this.transitionDuration = 0.1; // 100ms transition
    this.visemeAnticipation = 0.05; // 50ms anticipation
  }

  /**
   * Get current phoneme with coarticulation blending and anticipation
   */
  getCurrentViseme(audioTime, phonemes) {
    if (!phonemes || phonemes.length === 0) {
      return { phoneme: null, weights: {}, blendFactor: 0, anticipationFactor: 0 };
    }

    // Find current and adjacent phonemes
    const currentIndex = phonemes.findIndex(p => audioTime >= p.start && audioTime < p.end);
    const prevIndex = currentIndex - 1;
    const nextIndex = currentIndex + 1;

    const current = currentIndex >= 0 ? phonemes[currentIndex] : null;
    const prev = prevIndex >= 0 ? phonemes[prevIndex] : null;
    const next = nextIndex < phonemes.length ? phonemes[nextIndex] : null;

    if (!current) {
      return { phoneme: null, weights: {}, blendFactor: 0, anticipationFactor: 0 };
    }

    // Calculate timing within current phoneme
    const phonemeDuration = current.end - current.start;
    const timeInPhoneme = audioTime - current.start;
    const progressInPhoneme = phonemeDuration > 0 ? timeInPhoneme / phonemeDuration : 0;

    // Anticipation: start preparing for next phoneme early
    let anticipationFactor = 0;
    let baseWeights = { ...getVisemeWeights(current.phoneme) };

    if (next && progressInPhoneme > (1 - this.visemeAnticipation / phonemeDuration)) {
      const nextWeights = getVisemeWeights(next.phoneme);
      anticipationFactor = Math.min(1, (progressInPhoneme - (1 - this.visemeAnticipation / phonemeDuration)) / (this.visemeAnticipation / phonemeDuration));

      // Blend with anticipation of next phoneme
      Object.keys({ ...baseWeights, ...nextWeights }).forEach(key => {
        const currentWeight = baseWeights[key] || 0;
        const nextWeight = nextWeights[key] || 0;
        baseWeights[key] = currentWeight * (1 - anticipationFactor * 0.3) + nextWeight * (anticipationFactor * 0.3);
      });
    }

    // Coarticulation: blend with previous phoneme at start
    let blendFactor = 0;
    if (prev && progressInPhoneme < 0.2) {
      const prevWeights = getVisemeWeights(prev.phoneme);
      blendFactor = Math.max(0, 1 - progressInPhoneme / 0.2);

      Object.keys({ ...baseWeights, ...prevWeights }).forEach(key => {
        const currentWeight = baseWeights[key] || 0;
        const prevWeight = prevWeights[key] || 0;
        baseWeights[key] = currentWeight * (1 - blendFactor * 0.4) + prevWeight * (blendFactor * 0.4);
      });
    }

    return {
      phoneme: current,
      weights: baseWeights,
      blendFactor: blendFactor,
      anticipationFactor: anticipationFactor
    };
  }
}

/**
 * Maps CMU phonemes to Oculus LipSync visemes (15 visemes)
 * Ready Player Me avatars support Oculus LipSync for lip-sync animation
 */
const PHONEME_TO_OCULUS_VISEME = {
  // Silence
  'sil': { viseme_sil: 1.0 },

  // Vowels - map to closest Oculus visemes
  'AA': { viseme_aa: 1.0 },              // "father" -> aa
  'AE': { viseme_aa: 0.8 },              // "cat" -> aa
  'AH': { viseme_aa: 0.6 },              // "but" -> aa
  'AO': { viseme_O: 0.8 },               // "caught" -> O
  'AW': { viseme_O: 0.7 },               // "cow" -> O
  'AY': { viseme_I: 0.6 },               // "hide" -> I
  'EH': { viseme_E: 0.8 },               // "red" -> E
  'ER': { viseme_E: 0.7 },               // "her" -> E
  'EY': { viseme_E: 0.9 },               // "ate" -> E
  'IH': { viseme_I: 0.7 },               // "it" -> I
  'IY': { viseme_I: 1.0 },               // "feet" -> I
  'OW': { viseme_O: 1.0 },               // "go" -> O
  'OY': { viseme_O: 0.8 },               // "boy" -> O
  'UH': { viseme_U: 0.6 },               // "book" -> U
  'UW': { viseme_U: 1.0 },               // "boot" -> U

  // Consonants - Bilabials (lips together) -> PP
  'B': { viseme_PP: 0.8 },               // "bat" -> PP
  'P': { viseme_PP: 1.0 },               // "pat" -> PP
  'M': { viseme_PP: 0.6 },               // "mat" -> PP

  // Consonants - Labiodentals -> FF
  'F': { viseme_FF: 1.0 },               // "fat" -> FF
  'V': { viseme_FF: 0.8 },               // "vat" -> FF

  // Consonants - Dental -> TH
  'TH': { viseme_TH: 1.0 },              // "thin" -> TH
  'DH': { viseme_TH: 0.8 },              // "this" -> TH

  // Consonants - Alveolar -> DD, SS, nn
  'T': { viseme_DD: 0.8 },               // "top" -> DD
  'D': { viseme_DD: 1.0 },               // "dog" -> DD
  'N': { viseme_nn: 0.8 },               // "no" -> nn
  'L': { viseme_DD: 0.6 },               // "let" -> DD
  'S': { viseme_SS: 1.0 },               // "sit" -> SS
  'Z': { viseme_SS: 0.8 },               // "zoo" -> SS

  // Consonants - Postalveolar -> CH, SS
  'SH': { viseme_SS: 0.9 },              // "she" -> SS
  'ZH': { viseme_SS: 0.7 },              // "measure" -> SS
  'CH': { viseme_CH: 1.0 },              // "church" -> CH
  'JH': { viseme_CH: 0.8 },              // "judge" -> CH

  // Consonants - Velar -> kk
  'K': { viseme_kk: 1.0 },               // "cat" -> kk
  'G': { viseme_kk: 0.8 },               // "go" -> kk
  'NG': { viseme_nn: 0.7 },              // "sing" -> nn

  // Consonants - Other -> RR, kk
  'HH': { viseme_kk: 0.6 },              // "hat" -> kk
  'R': { viseme_RR: 1.0 },               // "red" -> RR
  'W': { viseme_U: 0.5 },                // "wet" -> U
  'Y': { viseme_I: 0.5 },                // "yes" -> I
};

/**
 * Get Oculus LipSync viseme weights for a phoneme
 */
function getVisemeWeights(phoneme) {
  if (!phoneme) return {};
  return PHONEME_TO_OCULUS_VISEME[phoneme.toUpperCase()] || {};
}

/**
 * Check if Oculus LipSync visemes are available
 */
function hasOculusVisemesAvailable(morphTargets) {
  const oculusVisemes = ['viseme_sil', 'viseme_PP', 'viseme_FF', 'viseme_TH', 'viseme_DD', 'viseme_kk', 'viseme_CH', 'viseme_SS', 'viseme_nn', 'viseme_RR', 'viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U'];
  return oculusVisemes.some(viseme => morphTargets[viseme] !== undefined);
}

/**
 * Check if ARKit blend shapes are available
 */
function hasArkitShapesAvailable(morphTargets) {
  const arkitShapes = ['jawOpen', 'mouthOpen', 'mouthClose', 'mouthFunnel', 'mouthPucker'];
  return arkitShapes.some(shape => morphTargets[shape] !== undefined);
}

/**
 * Check if any morph targets are available (last resort fallback)
 */
function hasAnyMorphTargetsAvailable(morphTargets) {
  return Object.keys(morphTargets).length > 0;
}

/**
 * Process phonemes array to get current Oculus viseme weights
 */
function processPhonemesToOculusVisemes(phonemes) {
  if (!phonemes || phonemes.length === 0) return {};

  // Find current phoneme based on audio time (assuming audioTime is available)
  // For now, just use the first phoneme as a simple implementation
  const currentPhoneme = phonemes[0];
  if (!currentPhoneme || !currentPhoneme.phoneme) return {};

  return getVisemeWeights(currentPhoneme.phoneme);
}

/**
 * Convert Oculus viseme weights to ARKit blend shapes for fallback
 */
function convertToArkitShapes(oculusWeights) {
  const arkitWeights = {};

  Object.entries(oculusWeights).forEach(([viseme, weight]) => {
    switch (viseme) {
      case 'viseme_sil':
        // Silence - slight mouth closure
        arkitWeights.mouthClose = weight * 0.5;
        break;
      case 'viseme_PP':
      case 'viseme_FF':
        // Bilabial/labiodental - lips together or to teeth
        arkitWeights.mouthClose = weight;
        break;
      case 'viseme_TH':
      case 'viseme_DD':
        // Dental/alveolar - tongue to teeth/ridge
        arkitWeights.mouthOpen = weight * 0.3;
        break;
      case 'viseme_kk':
      case 'viseme_CH':
      case 'viseme_SS':
        // Velar/postalveolar - back of tongue
        arkitWeights.mouthFunnel = weight * 0.7;
        arkitWeights.mouthPucker = weight * 0.3;
        break;
      case 'viseme_nn':
      case 'viseme_RR':
        // Alveolar/retroflex - tongue position
        arkitWeights.mouthOpen = weight * 0.4;
        break;
      case 'viseme_aa':
      case 'viseme_E':
      case 'viseme_I':
      case 'viseme_O':
      case 'viseme_U':
        // Vowels - mouth open with different shapes
        arkitWeights.jawOpen = weight * 0.8;
        arkitWeights.mouthOpen = weight * 0.6;
        if (viseme === 'viseme_O' || viseme === 'viseme_U') {
          arkitWeights.mouthFunnel = weight * 0.5;
        }
        break;
    }
  });

  return arkitWeights;
}

/**
 * Map viseme weights to any available morph targets as last resort
 */
function mapToAvailableMorphTargets(oculusWeights, availableTargets) {
  const weights = {};

  // Calculate overall mouth openness from visemes
  let mouthOpenness = 0;
  Object.entries(oculusWeights).forEach(([viseme, weight]) => {
    if (viseme === 'viseme_sil') {
      mouthOpenness += weight * 0.1; // Silence = slight movement
    } else if (['viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U'].includes(viseme)) {
      mouthOpenness += weight * 0.8; // Vowels = more open
    } else if (['viseme_PP', 'viseme_FF'].includes(viseme)) {
      mouthOpenness += weight * 0.2; // Closed consonants = less open
    } else {
      mouthOpenness += weight * 0.4; // Other consonants = medium open
    }
  });

  // Try to map to common morph target names
  availableTargets.forEach(target => {
    const lowerTarget = target.toLowerCase();

    if (lowerTarget.includes('mouth') && lowerTarget.includes('open')) {
      weights[target] = Math.min(1, mouthOpenness);
    } else if (lowerTarget.includes('jaw') && lowerTarget.includes('open')) {
      weights[target] = Math.min(1, mouthOpenness * 0.8);
    } else if (lowerTarget.includes('mouth') && lowerTarget.includes('close')) {
      weights[target] = Math.min(1, (1 - mouthOpenness) * 0.5);
    } else if (lowerTarget.includes('viseme') || lowerTarget.includes('phoneme')) {
      // If it has viseme in the name, use direct mapping
      weights[target] = mouthOpenness;
    }
    // For other morph targets, we'll leave them at 0 (neutral)
  });

  console.log('🔄 Mapped viseme weights to available morph targets:', weights);
  return weights;
}

export function LipSyncController({ faceMesh }) {
  const audioTime = useInterviewStore(state => state.audioTime);
  const phonemes = useInterviewStore(state => state.phonemes);
  const isAvatarSpeaking = useInterviewStore(state => state.isAvatarSpeaking);

  // Enhanced components
  const phonemeScheduler = useMemo(() => new PhonemeScheduler(), []);
  const lipSyncStyler = useMemo(() => new LipSyncStyler(), []);
  const silenceHandler = useMemo(() => new SilenceHandler(), []);

  // Object pooling for morph targets
  const morphPool = useMemo(() => new MorphTargetPool(), []);

  // Interpolation state
  const currentWeights = useRef({});
  const targetWeights = useRef({});
  const interpolationProgress = useRef(0);
  const lastUpdateTime = useRef(0);

  // Debug state
  const [debugInfo, setDebugInfo] = useState({
    currentPhoneme: null,
    targetWeights: {},
    currentWeights: {},
    emotion: 'neutral',
    speakingRate: 0,
    isSilent: false
  });

  // Speaking analysis state
  const speakingStats = useRef({
    phonemeCount: 0,
    avgPhonemeDuration: 0,
    speakingRate: 0, // phonemes per second
    lastAnalysisTime: 0
  });

  // Analyze speaking patterns for adaptive lip-sync
  const analyzeSpeakingPatterns = (phonemes, currentTime) => {
    if (!phonemes || phonemes.length === 0) return;

    // Update speaking statistics every 500ms
    if (currentTime - speakingStats.current.lastAnalysisTime > 0.5) {
      const recentPhonemes = phonemes.filter(p => p.end > currentTime - 2); // Last 2 seconds
      if (recentPhonemes.length > 0) {
        const totalDuration = recentPhonemes.reduce((sum, p) => sum + (p.end - p.start), 0);
        speakingStats.current.avgPhonemeDuration = totalDuration / recentPhonemes.length;
        speakingStats.current.speakingRate = recentPhonemes.length / 2; // phonemes per second
        speakingStats.current.phonemeCount = recentPhonemes.length;
      }
      speakingStats.current.lastAnalysisTime = currentTime;
    }

    // Adjust emotion based on speaking rate
    if (speakingStats.current.speakingRate > 8) {
      lipSyncStyler.setEmotion('excited');
    } else if (speakingStats.current.speakingRate < 4) {
      lipSyncStyler.setEmotion('calm');
    } else {
      lipSyncStyler.setEmotion('neutral');
    }
  };

  // Update lip-sync on every frame with interpolation
  useFrame((state, delta) => {
    if (!faceMesh) return;

    const influences = faceMesh.morphTargetInfluences;
    if (!influences) return;

    const currentTime = state.clock.elapsedTime;

    // Analyze speaking patterns
    analyzeSpeakingPatterns(phonemes, currentTime);

    // Handle silence periods
    const silenceInfo = silenceHandler.handleSilence(audioTime, phonemes);
    const isFallbackAvatar = faceMesh.name === 'FallbackAvatar';
    const hasOculusVisemes = faceMesh.morphTargetDictionary && faceMesh.morphTargetDictionary['viseme_sil'];
    const hasArkitBlendshapes = faceMesh.morphTargetDictionary && faceMesh.morphTargetDictionary['jawOpen'];

    // Check for any available morph targets as last resort
    const availableMorphTargets = faceMesh.morphTargetDictionary ? Object.keys(faceMesh.morphTargetDictionary) : [];
    const hasAnyMorphTargets = availableMorphTargets.length > 0;

    // Calculate target weights based on phonemes or silence
    if (silenceInfo.isSilent) {
      // Silence - use appropriate morph targets
      if (isFallbackAvatar) {
        targetWeights.current = { mouthOpen: silenceInfo.mouthOpen };
      } else if (hasOculusVisemes) {
        targetWeights.current = { viseme_sil: 1.0 };
      } else if (hasArkitBlendshapes) {
        targetWeights.current = { mouthClose: 0.1 };
      } else {
        targetWeights.current = {};
      }
    } else if (phonemes.length > 0) {
      // Use enhanced phoneme scheduling with coarticulation
      const visemeData = phonemeScheduler.getCurrentViseme(audioTime, phonemes);

      if (visemeData.phoneme) {
        console.log('🎭 Processing phoneme:', visemeData.phoneme.phoneme, 'at time:', audioTime.toFixed(2), 'weights:', visemeData.weights);
        if (isFallbackAvatar) {
          // Simple mapping for fallback avatar
          const phoneme = visemeData.phoneme.phoneme.toUpperCase();
          const isVowel = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'].includes(phoneme);
          targetWeights.current = { mouthOpen: isVowel ? 0.6 : 0.2 };
        } else if (hasOculusVisemes) {
          // Use Oculus LipSync visemes for proper phoneme mapping
          const emotionAdjustedWeights = lipSyncStyler.applyEmotionAdjustment(visemeData.weights);
          targetWeights.current = emotionAdjustedWeights;
        } else if (hasArkitBlendshapes) {
          // Convert phoneme weights to ARKit shapes
          const oculusWeights = visemeData.weights;
          targetWeights.current = convertToArkitShapes(oculusWeights);
        } else if (hasAnyMorphTargets) {
          // Last resort: try to use any available morph targets
          console.log('🔄 Using available morph targets for lip sync:', availableMorphTargets);
          targetWeights.current = mapToAvailableMorphTargets(visemeData.weights, availableMorphTargets);
        } else {
          console.warn('⚠️ No suitable morph targets found for lip sync');
          targetWeights.current = {};
        }

        // Update debug info
        setDebugInfo({
          currentPhoneme: visemeData.phoneme,
          targetWeights: { ...targetWeights.current },
          currentWeights: { ...currentWeights.current },
          emotion: lipSyncStyler.currentEmotion,
          speakingRate: speakingStats.current.speakingRate,
          isSilent: silenceInfo.isSilent
        });
      }
    } else if (isAvatarSpeaking) {
      // Fallback for when avatar is speaking but no phonemes available
      if (isFallbackAvatar) {
        targetWeights.current = { mouthOpen: 0.3 };
      } else if (hasOculusVisemes) {
        targetWeights.current = { viseme_aa: 0.6 };
      } else if (hasArkitBlendshapes) {
        targetWeights.current = { jawOpen: 0.4, mouthOpen: 0.3 };
      }
    } else {
      // Not speaking - return to neutral
      targetWeights.current = {};
      setDebugInfo(prev => ({ ...prev, isSilent: true }));
    }

    // Add subtle variation for natural animation
    const variation = Math.sin(currentTime * 8) * 0.05;
    if (isFallbackAvatar && targetWeights.current.mouthOpen !== undefined) {
      targetWeights.current.mouthOpen = Math.max(0, Math.min(1, targetWeights.current.mouthOpen + variation));
    } else if (hasOculusVisemes) {
      // Apply variation to the primary active viseme
      const primaryViseme = Object.keys(targetWeights.current).find(key => key !== 'viseme_sil' && targetWeights.current[key] > 0);
      if (primaryViseme) {
        targetWeights.current[primaryViseme] = Math.max(0, Math.min(1, targetWeights.current[primaryViseme] + variation));
      }
    } else if (hasArkitBlendshapes && targetWeights.current.mouthOpen !== undefined) {
      targetWeights.current.mouthOpen = Math.max(0, Math.min(1, targetWeights.current.mouthOpen + variation));
    }

    // Adaptive interpolation based on speaking rate
    const speakingRateMultiplier = Math.max(0.5, Math.min(2.0, speakingStats.current.speakingRate / 6));
    const targetChangeDetected = JSON.stringify(targetWeights.current) !== JSON.stringify(currentWeights.current);
    const baseInterpolationSpeed = targetChangeDetected ? 12 : 8;
    const interpolationSpeed = baseInterpolationSpeed * delta * speakingRateMultiplier;
    interpolationProgress.current = Math.min(1, interpolationProgress.current + interpolationSpeed);

    // Apply interpolated weights to morph targets
    Object.entries(targetWeights.current).forEach(([morphName, targetWeight]) => {
      let index;

      if (isFallbackAvatar) {
        index = faceMesh.morphTargetDictionary[morphName];
      } else {
        index = faceMesh.morphTargetDictionary[morphName];
      }

      if (index !== undefined && influences[index] !== undefined) {
        const currentWeight = currentWeights.current[morphName] || 0;
        const interpolatedWeight = lerp(currentWeight, targetWeight, interpolationProgress.current);

        influences[index] = Math.max(0, Math.min(1, interpolatedWeight));
        currentWeights.current[morphName] = interpolatedWeight;
      }
    });

    // Reset interpolation progress when targets change significantly
    if (interpolationProgress.current >= 1 || targetChangeDetected) {
      interpolationProgress.current = 0;
      Object.assign(currentWeights.current, targetWeights.current);
    }

    // Cache morph target state for performance
    const cacheKey = `${isAvatarSpeaking}-${audioTime.toFixed(2)}-${lipSyncStyler.currentEmotion}`;
    morphPool.set(cacheKey, { ...currentWeights.current });
  });

  // Reset when component unmounts
  useEffect(() => {
    return () => {
      morphPool.clear();
    };
  }, [morphPool]);

  return (
    <>
      <LipSyncDebugOverlay
        faceMesh={faceMesh}
        currentPhoneme={debugInfo.currentPhoneme}
        targetWeights={debugInfo.targetWeights}
        currentWeights={debugInfo.currentWeights}
        emotion={debugInfo.emotion}
        speakingRate={debugInfo.speakingRate}
        isSilent={debugInfo.isSilent}
      />
    </>
  );
}