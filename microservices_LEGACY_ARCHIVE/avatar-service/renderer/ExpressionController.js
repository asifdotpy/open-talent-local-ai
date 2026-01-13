/**
 * ExpressionController.js - Controls facial expressions and blends with lip-sync
 * Combines emotion states with phoneme-based lip movements for realistic avatars
 */

import { EmotionEngine } from './EmotionEngine.js'

/**
 * ExpressionController - Manages the combination of emotions and lip-sync
 */
export class ExpressionController {
  constructor(config = {}) {
    this.emotionEngine = new EmotionEngine({
      transitionDuration: config.emotionTransitionDuration || 500,
      blinkInterval: config.blinkInterval || 3000,
      blinkDuration: config.blinkDuration || 150,
      easing: config.easing || 'smooth'
    })

    // Blending configuration
    this.lipSyncWeight = config.lipSyncWeight || 1.0 // 0-1, how much lip-sync affects mouth
    this.emotionWeight = config.emotionWeight || 0.7 // 0-1, how much emotion affects face
    this.idleAnimationEnabled = config.idleAnimationEnabled !== false

    // Morph target mapping
    this.lipSyncTargets = ['jawOpen', 'mouthFunnel', 'mouthClose', 'mouthSmile']
    this.expressionTargets = ['eyebrowRaise', 'eyebrowFrown', 'eyeWiden', 'eyeNarrow', 'mouthFrown', 'cheekRaise']

    // Performance tracking
    this.lastUpdateTime = Date.now()
  }

  /**
   * Set the current emotion
   * @param {Object} emotion - Emotion state from EmotionStates
   * @param {number} duration - Transition duration in ms (optional)
   */
  setEmotion(emotion, duration = null) {
    this.emotionEngine.setEmotion(emotion, duration)
  }

  /**
   * Set emotion from sentiment score
   * @param {number} sentiment - Sentiment score -1 to 1
   * @param {string} context - Context hint (interview, feedback, question)
   */
  setEmotionFromSentiment(sentiment, context = 'neutral') {
    const emotion = EmotionEngine.getEmotionFromSentiment(sentiment, context)
    this.setEmotion(emotion)
  }

  /**
   * Update expression state (call this each frame or regularly)
   * @param {number} deltaTime - Time elapsed since last update in ms (optional)
   */
  update(deltaTime = null) {
    if (deltaTime === null) {
      const currentTime = Date.now()
      deltaTime = currentTime - this.lastUpdateTime
      this.lastUpdateTime = currentTime
    }

    if (this.idleAnimationEnabled) {
      this.emotionEngine.update(deltaTime)
    }
  }

  /**
   * Get blended morph target weights for rendering
   * Combines lip-sync phoneme weights with emotional expression weights
   *
   * @param {Object} phonemeWeights - Weights from PhonemeMapper for lip-sync
   *   Example: { jawOpen: 0.5, mouthFunnel: 0.3, mouthClose: 0, mouthSmile: 0 }
   * @returns {Object} Complete morph target weights for all 10 targets
   */
  getBlendedMorphWeights(phonemeWeights = {}) {
    // Get emotion-based weights
    const emotionWeights = this.emotionEngine.getCurrentMorphWeights()

    // Initialize result with all targets
    const blendedWeights = {
      // Lip-sync targets (0-3)
      jawOpen: 0,
      mouthFunnel: 0,
      mouthClose: 0,
      mouthSmile: 0,
      // Expression targets (4-9)
      eyebrowRaise: 0,
      eyebrowFrown: 0,
      eyeWiden: 0,
      eyeNarrow: 0,
      mouthFrown: 0,
      cheekRaise: 0
    }

    // Blend lip-sync targets: phonemes take priority, emotion provides baseline
    this.lipSyncTargets.forEach(target => {
      const phonemeWeight = phonemeWeights[target] || 0
      const emotionWeight = emotionWeights[target] || 0

      // Lip-sync overrides emotion for mouth movements
      // Use max blend to ensure phonemes are visible
      blendedWeights[target] = Math.max(
        phonemeWeight * this.lipSyncWeight,
        emotionWeight * this.emotionWeight * (1 - phonemeWeight)
      )
    })

    // Expression targets: purely emotion-driven (not affected by lip-sync)
    this.expressionTargets.forEach(target => {
      blendedWeights[target] = (emotionWeights[target] || 0) * this.emotionWeight
    })

    // Special handling: mouthSmile from emotion can enhance lip-sync smile
    if (phonemeWeights.mouthSmile > 0 && emotionWeights.mouthSmile > 0) {
      blendedWeights.mouthSmile = Math.min(1.0,
        phonemeWeights.mouthSmile * this.lipSyncWeight +
        emotionWeights.mouthSmile * this.emotionWeight * 0.3
      )
    }

    // Clamp all weights to 0-1 range
    Object.keys(blendedWeights).forEach(key => {
      blendedWeights[key] = Math.max(0, Math.min(1, blendedWeights[key]))
    })

    return blendedWeights
  }

  /**
   * Get morph target weights as array (for Three.js morphTargetInfluences)
   * @param {Object} phonemeWeights - Weights from PhonemeMapper
   * @returns {Array<number>} Array of 10 weights in dictionary order
   */
  getBlendedMorphWeightsArray(phonemeWeights = {}) {
    const weights = this.getBlendedMorphWeights(phonemeWeights)

    // Return in the order defined by morphTargetDictionary
    return [
      weights.jawOpen,
      weights.mouthFunnel,
      weights.mouthClose,
      weights.mouthSmile,
      weights.eyebrowRaise,
      weights.eyebrowFrown,
      weights.eyeWiden,
      weights.eyeNarrow,
      weights.mouthFrown,
      weights.cheekRaise
    ]
  }

  /**
   * Apply blended weights to a Three.js mesh
   * @param {THREE.Mesh} mesh - Mesh with morph targets
   * @param {Object} phonemeWeights - Weights from PhonemeMapper
   */
  applyToMesh(mesh, phonemeWeights = {}) {
    if (!mesh.morphTargetInfluences) {
      console.warn('Mesh does not have morphTargetInfluences')
      return
    }

    const weightsArray = this.getBlendedMorphWeightsArray(phonemeWeights)

    // Apply weights to mesh
    for (let i = 0; i < weightsArray.length && i < mesh.morphTargetInfluences.length; i++) {
      mesh.morphTargetInfluences[i] = weightsArray[i]
    }
  }

  /**
   * Reset to neutral state
   */
  reset() {
    this.emotionEngine.reset()
    this.lastUpdateTime = Date.now()
  }

  /**
   * Get current emotion name
   * @returns {string} Current emotion name
   */
  getCurrentEmotion() {
    return this.emotionEngine.targetEmotion.name
  }

  /**
   * Get emotion analytics
   * @returns {Object} Emotion statistics
   */
  getAnalytics() {
    return {
      ...this.emotionEngine.getAnalytics(),
      blendingConfig: {
        lipSyncWeight: this.lipSyncWeight,
        emotionWeight: this.emotionWeight,
        idleAnimationEnabled: this.idleAnimationEnabled
      }
    }
  }

  /**
   * Configure blending weights
   * @param {Object} config - Configuration object
   */
  configure(config) {
    if (config.lipSyncWeight !== undefined) {
      this.lipSyncWeight = Math.max(0, Math.min(1, config.lipSyncWeight))
    }
    if (config.emotionWeight !== undefined) {
      this.emotionWeight = Math.max(0, Math.min(1, config.emotionWeight))
    }
    if (config.idleAnimationEnabled !== undefined) {
      this.idleAnimationEnabled = config.idleAnimationEnabled
    }
  }

  /**
   * Get emotion state for a conversation phase
   * @param {string} phase - Conversation phase (intro, main, conclusion)
   * @param {number} sentiment - Sentiment score
   * @returns {Object} Appropriate emotion with adjusted intensity
   */
  static getEmotionForPhase(phase, sentiment = 0) {
    const baseEmotion = EmotionEngine.getEmotionFromSentiment(sentiment, 'interview')
    const intensityMultiplier = EmotionEngine.getIntensityMultiplier(phase)

    // Create adjusted emotion with phase-appropriate intensity
    const adjustedEmotion = {
      ...baseEmotion,
      intensity: baseEmotion.intensity * intensityMultiplier,
      morphWeights: {}
    }

    // Scale morph weights by intensity multiplier
    Object.keys(baseEmotion.morphWeights).forEach(key => {
      adjustedEmotion.morphWeights[key] = baseEmotion.morphWeights[key] * intensityMultiplier
    })

    return adjustedEmotion
  }
}

export default ExpressionController
