/**
 * Phase 3: MorphTargetAdapter - Adapts 3D models for morph target animation
 * Handles phoneme-to-morph target mapping and animation
 */

export class MorphTargetAdapter {
  constructor(model, config, phonemeMapper) {
    this.model = model
    this.config = config
    this.phonemeMapper = phonemeMapper
    this.morphTargetMesh = null
    this.currentPhoneme = null
    this.transitionProgress = 0
    this.transitionDuration = 0.1 // 100ms transition

    this.initialize()
  }

  initialize() {
    // Find the mesh with morph targets
    this.model.traverse((child) => {
      if (child.isMesh && child.morphTargetInfluences) {
        this.morphTargetMesh = child
        console.log(`MorphTargetAdapter: Found mesh with ${child.morphTargetInfluences.length} morph targets`)
        console.log('Available morph targets:', child.morphTargetDictionary)
      }
    })

    if (!this.morphTargetMesh) {
      console.warn('MorphTargetAdapter: No mesh with morph targets found in model')
    }
  }

  /**
   * Animate based on phoneme data
   * @param {Array} phonemes - Phoneme timing data
   * @param {number} currentTime - Current time in seconds
   */
  animate(phonemes, currentTime) {
    if (!this.morphTargetMesh || !phonemes) return

    // Find current phoneme
    const currentPhonemeData = phonemes.find(p =>
      currentTime >= p.start && currentTime <= p.end
    )

    const targetPhoneme = currentPhonemeData ? currentPhonemeData.phoneme : 'rest'

    // Handle phoneme transitions
    if (this.currentPhoneme !== targetPhoneme) {
      this.currentPhoneme = targetPhoneme
      this.transitionProgress = 0
    }

    // Smooth transition between phonemes
    this.transitionProgress = Math.min(1, this.transitionProgress + (1 / this.transitionDuration) * (1/30)) // Assuming 30fps

    // Get morph weights for current phoneme
    const weights = this.phonemeMapper.getMorphWeights(targetPhoneme)

    // Apply weights to morph targets
    this.applyMorphWeights(weights)
  }

  /**
   * Animate with emotion blending
   * @param {Array} phonemes - Phoneme timing data
   * @param {number} currentTime - Current time in seconds
   * @param {Array} emotionWeights - Emotion morph target weights
   */
  animateWithEmotion(phonemes, currentTime, emotionWeights) {
    // First apply phoneme animation
    this.animate(phonemes, currentTime)

    // Then blend with emotion weights if provided
    if (emotionWeights && emotionWeights.length > 0) {
      this.blendEmotionWeights(emotionWeights)
    }
  }

  /**
   * Apply morph target weights
   * @param {Object} weights - Morph target weight object
   */
  applyMorphWeights(weights) {
    if (!this.morphTargetMesh) return

    const influences = this.morphTargetMesh.morphTargetInfluences
    const dictionary = this.morphTargetMesh.morphTargetDictionary

    if (!influences || !dictionary) return

    // Reset all influences
    for (let i = 0; i < influences.length; i++) {
      influences[i] = 0
    }

    // Apply weights for each phoneme
    for (const [phoneme, weight] of Object.entries(weights)) {
      const index = dictionary[phoneme]
      if (index !== undefined) {
        influences[index] = weight * this.transitionProgress
      }
    }
  }

  /**
   * Blend emotion weights with current morph targets
   * @param {Array} emotionWeights - Emotion morph weights array
   */
  blendEmotionWeights(emotionWeights) {
    if (!this.morphTargetMesh || !emotionWeights) return

    const influences = this.morphTargetMesh.morphTargetInfluences

    // For now, we'll assume emotion weights correspond to additional morph targets
    // In a full implementation, this would be more sophisticated
    const emotionStartIndex = 5 // After phoneme morphs (A, E, I, O, U)

    for (let i = 0; i < emotionWeights.length; i++) {
      const index = emotionStartIndex + i
      if (index < influences.length) {
        // Blend emotion with existing phoneme weights
        influences[index] = (influences[index] || 0) + emotionWeights[i] * 0.3 // 30% emotion influence
      }
    }
  }

  /**
   * Get current morph target influences
   * @returns {Array} Current morph influences
   */
  getCurrentInfluences() {
    return this.morphTargetMesh ? [...this.morphTargetMesh.morphTargetInfluences] : []
  }

  /**
   * Set transition duration
   * @param {number} duration - Transition duration in seconds
   */
  setTransitionDuration(duration) {
    this.transitionDuration = Math.max(0.01, duration)
  }

  /**
   * Reset to neutral pose
   */
  reset() {
    this.currentPhoneme = null
    this.transitionProgress = 0

    if (this.morphTargetMesh && this.morphTargetMesh.morphTargetInfluences) {
      this.morphTargetMesh.morphTargetInfluences.fill(0)
    }
  }

  /**
   * Get morph target information
   * @returns {Object} Morph target metadata
   */
  getMorphInfo() {
    if (!this.morphTargetMesh) return null

    return {
      morphTargetCount: this.morphTargetMesh.morphTargetInfluences.length,
      morphTargetDictionary: this.morphTargetMesh.morphTargetDictionary,
      currentInfluences: this.getCurrentInfluences(),
      currentPhoneme: this.currentPhoneme
    }
  }
}