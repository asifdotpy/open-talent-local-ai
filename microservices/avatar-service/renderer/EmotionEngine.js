/**
 * EmotionEngine.js - Emotion state machine and blending system
 * Manages avatar emotional states and transitions for realistic expressions
 */

/**
 * Emotion states with morph target weights
 * Each emotion maps to a combination of facial expression morph targets
 */
export const EmotionStates = {
  NEUTRAL: {
    name: 'neutral',
    intensity: 0.0,
    morphWeights: {
      // Baseline state - all morph targets at rest
      eyebrowRaise: 0.0,
      eyebrowFrown: 0.0,
      eyeWiden: 0.0,
      eyeNarrow: 0.0,
      mouthSmile: 0.0,
      mouthFrown: 0.0,
      cheekRaise: 0.0
    },
    idleVariation: 0.05 // Small random variations for natural look
  },

  PROFESSIONAL: {
    name: 'professional',
    intensity: 0.3,
    morphWeights: {
      eyebrowRaise: 0.1,
      eyebrowFrown: 0.0,
      eyeWiden: 0.05,
      eyeNarrow: 0.0,
      mouthSmile: 0.15,
      mouthFrown: 0.0,
      cheekRaise: 0.1
    },
    idleVariation: 0.03
  },

  HAPPY: {
    name: 'happy',
    intensity: 0.7,
    morphWeights: {
      eyebrowRaise: 0.2,
      eyebrowFrown: 0.0,
      eyeWiden: 0.15,
      eyeNarrow: 0.0,
      mouthSmile: 0.6,
      mouthFrown: 0.0,
      cheekRaise: 0.5
    },
    idleVariation: 0.08
  },

  SURPRISED: {
    name: 'surprised',
    intensity: 0.8,
    morphWeights: {
      eyebrowRaise: 0.8,
      eyebrowFrown: 0.0,
      eyeWiden: 0.9,
      eyeNarrow: 0.0,
      mouthSmile: 0.0,
      mouthFrown: 0.0,
      cheekRaise: 0.0
    },
    idleVariation: 0.1
  },

  CONFUSED: {
    name: 'confused',
    intensity: 0.5,
    morphWeights: {
      eyebrowRaise: 0.3,
      eyebrowFrown: 0.4,
      eyeWiden: 0.0,
      eyeNarrow: 0.2,
      mouthSmile: 0.0,
      mouthFrown: 0.1,
      cheekRaise: 0.0
    },
    idleVariation: 0.06
  },

  SAD: {
    name: 'sad',
    intensity: 0.4,
    morphWeights: {
      eyebrowRaise: 0.0,
      eyebrowFrown: 0.5,
      eyeWiden: 0.0,
      eyeNarrow: 0.3,
      mouthSmile: 0.0,
      mouthFrown: 0.4,
      cheekRaise: 0.0
    },
    idleVariation: 0.02
  },

  THOUGHTFUL: {
    name: 'thoughtful',
    intensity: 0.4,
    morphWeights: {
      eyebrowRaise: 0.2,
      eyebrowFrown: 0.2,
      eyeWiden: 0.0,
      eyeNarrow: 0.1,
      mouthSmile: 0.05,
      mouthFrown: 0.0,
      cheekRaise: 0.0
    },
    idleVariation: 0.04
  }
}

/**
 * Easing functions for smooth emotion transitions
 */
export const EasingFunctions = {
  linear: (t) => t,
  easeInOut: (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  easeOut: (t) => t * (2 - t),
  easeIn: (t) => t * t,
  smooth: (t) => t * t * (3 - 2 * t) // Smoothstep
}

/**
 * EmotionEngine class - Manages emotional state and transitions
 */
export class EmotionEngine {
  constructor(config = {}) {
    this.currentEmotion = EmotionStates.NEUTRAL
    this.targetEmotion = EmotionStates.NEUTRAL
    this.transitionProgress = 1.0 // 0.0 to 1.0
    this.transitionDuration = config.transitionDuration || 500 // milliseconds
    this.transitionStartTime = 0
    this.easingFunction = EasingFunctions[config.easing || 'smooth']

    // Idle animation state
    this.idleTime = 0
    this.blinkTimer = 0
    this.blinkInterval = config.blinkInterval || 3000 // ms between blinks
    this.blinkDuration = config.blinkDuration || 150 // ms
    this.isBlinking = false

    // Emotion history for context-aware behavior
    this.emotionHistory = []
    this.maxHistoryLength = 10
  }

  /**
   * Set target emotion and begin transition
   * @param {Object} emotion - Target emotion state from EmotionStates
   * @param {number} duration - Transition duration in ms (optional)
   */
  setEmotion(emotion, duration = null) {
    if (this.targetEmotion.name === emotion.name && this.transitionProgress >= 1.0) {
      return // Already at this emotion
    }

    // Record emotion change in history
    this.emotionHistory.push({
      emotion: emotion.name,
      timestamp: Date.now(),
      intensity: emotion.intensity
    })

    if (this.emotionHistory.length > this.maxHistoryLength) {
      this.emotionHistory.shift()
    }

    this.currentEmotion = this.getCurrentBlendedState()
    this.targetEmotion = emotion
    this.transitionProgress = 0.0
    this.transitionStartTime = Date.now()
    if (duration !== null) {
      this.transitionDuration = duration
    }
  }

  /**
   * Update emotion state based on elapsed time
   * @param {number} deltaTime - Time elapsed since last update in ms
   */
  update(deltaTime) {
    // Update transition
    if (this.transitionProgress < 1.0) {
      const elapsed = Date.now() - this.transitionStartTime
      this.transitionProgress = Math.min(1.0, elapsed / this.transitionDuration)
    }

    // Update idle animations
    this.idleTime += deltaTime
    this.updateBlink(deltaTime)
  }

  /**
   * Update blink animation
   * @param {number} deltaTime - Time elapsed since last update in ms
   */
  updateBlink(deltaTime) {
    this.blinkTimer += deltaTime

    if (!this.isBlinking && this.blinkTimer >= this.blinkInterval) {
      // Start blink
      this.isBlinking = true
      this.blinkTimer = 0
    } else if (this.isBlinking && this.blinkTimer >= this.blinkDuration) {
      // End blink
      this.isBlinking = false
      this.blinkTimer = 0
    }
  }

  /**
   * Get current blended morph target weights
   * Combines emotion transition + idle animations
   * @returns {Object} Morph target weights
   */
  getCurrentMorphWeights() {
    const blendedState = this.getCurrentBlendedState()
    const weights = { ...blendedState.morphWeights }

    // Apply idle variations (subtle random movements)
    const idleNoise = Math.sin(this.idleTime * 0.001) * blendedState.idleVariation
    Object.keys(weights).forEach(key => {
      weights[key] += idleNoise * (Math.random() - 0.5)
      weights[key] = Math.max(0, Math.min(1, weights[key])) // Clamp 0-1
    })

    // Apply blink animation (overrides eye targets during blink)
    if (this.isBlinking) {
      const blinkProgress = this.blinkTimer / this.blinkDuration
      const blinkWeight = blinkProgress < 0.5
        ? blinkProgress * 2 // Close eyes
        : (1 - blinkProgress) * 2 // Open eyes

      weights.eyeWiden = Math.max(0, weights.eyeWiden - blinkWeight)
      weights.eyeNarrow = Math.max(0, weights.eyeNarrow + blinkWeight * 0.3)
    }

    return weights
  }

  /**
   * Get current blended emotion state
   * @returns {Object} Blended emotion state
   */
  getCurrentBlendedState() {
    if (this.transitionProgress >= 1.0) {
      return this.targetEmotion
    }

    // Blend between current and target emotions
    const t = this.easingFunction(this.transitionProgress)
    const blended = {
      name: `${this.currentEmotion.name}_to_${this.targetEmotion.name}`,
      intensity: this.lerp(this.currentEmotion.intensity, this.targetEmotion.intensity, t),
      morphWeights: {},
      idleVariation: this.lerp(this.currentEmotion.idleVariation, this.targetEmotion.idleVariation, t)
    }

    // Blend each morph target weight
    const morphKeys = Object.keys(this.currentEmotion.morphWeights)
    morphKeys.forEach(key => {
      blended.morphWeights[key] = this.lerp(
        this.currentEmotion.morphWeights[key],
        this.targetEmotion.morphWeights[key],
        t
      )
    })

    return blended
  }

  /**
   * Linear interpolation helper
   */
  lerp(a, b, t) {
    return a + (b - a) * t
  }

  /**
   * Get emotion from sentiment score
   * @param {number} sentiment - Sentiment score from -1 (negative) to 1 (positive)
   * @param {string} context - Context hint (interview, feedback, question)
   * @returns {Object} Appropriate emotion state
   */
  static getEmotionFromSentiment(sentiment, context = 'neutral') {
    // For professional interview context, moderate emotional responses
    if (context === 'interview' || context === 'professional') {
      if (sentiment > 0.5) return EmotionStates.PROFESSIONAL
      if (sentiment > 0.2) return EmotionStates.NEUTRAL
      if (sentiment < -0.3) return EmotionStates.THOUGHTFUL
      return EmotionStates.NEUTRAL
    }

    // More expressive for feedback context
    if (context === 'feedback') {
      if (sentiment > 0.6) return EmotionStates.HAPPY
      if (sentiment > 0.2) return EmotionStates.PROFESSIONAL
      if (sentiment < -0.4) return EmotionStates.SAD
      if (sentiment < -0.1) return EmotionStates.THOUGHTFUL
      return EmotionStates.NEUTRAL
    }

    // For questions, show attentiveness
    if (context === 'question') {
      if (sentiment < -0.5) return EmotionStates.CONFUSED
      if (sentiment > 0.3) return EmotionStates.SURPRISED
      return EmotionStates.THOUGHTFUL
    }

    // Default mapping
    if (sentiment > 0.6) return EmotionStates.HAPPY
    if (sentiment > 0.2) return EmotionStates.PROFESSIONAL
    if (sentiment < -0.5) return EmotionStates.SAD
    if (sentiment < -0.2) return EmotionStates.THOUGHTFUL
    if (Math.abs(sentiment) < 0.1 && Math.random() > 0.8) return EmotionStates.SURPRISED

    return EmotionStates.NEUTRAL
  }

  /**
   * Get emotion intensity multiplier based on conversation phase
   * @param {string} phase - Conversation phase (intro, main, conclusion)
   * @returns {number} Intensity multiplier
   */
  static getIntensityMultiplier(phase) {
    switch (phase) {
      case 'intro': return 0.7 // More reserved at start
      case 'main': return 1.0 // Full expression during conversation
      case 'conclusion': return 0.8 // Moderate at end
      default: return 1.0
    }
  }

  /**
   * Reset to neutral state
   */
  reset() {
    this.currentEmotion = EmotionStates.NEUTRAL
    this.targetEmotion = EmotionStates.NEUTRAL
    this.transitionProgress = 1.0
    this.emotionHistory = []
    this.idleTime = 0
    this.blinkTimer = 0
    this.isBlinking = false
  }

  /**
   * Get emotion analytics
   * @returns {Object} Emotion statistics
   */
  getAnalytics() {
    const emotionCounts = {}
    this.emotionHistory.forEach(entry => {
      emotionCounts[entry.emotion] = (emotionCounts[entry.emotion] || 0) + 1
    })

    return {
      currentEmotion: this.targetEmotion.name,
      transitionProgress: this.transitionProgress,
      emotionHistory: this.emotionHistory,
      emotionDistribution: emotionCounts,
      averageIntensity: this.emotionHistory.reduce((sum, e) => sum + e.intensity, 0) / (this.emotionHistory.length || 1)
    }
  }
}

export default EmotionEngine
