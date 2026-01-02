/**
 * Phase 3: PhonemeMapper - Maps phonemes to morph target weights
 * Converts phoneme data to facial morph target influences
 */

export class PhonemeMapper {
  constructor() {
    // Phoneme to morph target mapping
    this.phonemeMap = {
      'A': { A: 1.0, E: 0.0, I: 0.0, O: 0.0, U: 0.0 },
      'E': { A: 0.0, E: 1.0, I: 0.0, O: 0.0, U: 0.0 },
      'I': { A: 0.0, E: 0.0, I: 1.0, O: 0.0, U: 0.0 },
      'O': { A: 0.0, E: 0.0, I: 0.0, O: 1.0, U: 0.0 },
      'U': { A: 0.0, E: 0.0, I: 0.0, O: 0.0, U: 1.0 },
      'a': { A: 0.8, E: 0.0, I: 0.0, O: 0.0, U: 0.0 },
      'e': { A: 0.0, E: 0.8, I: 0.0, O: 0.0, U: 0.0 },
      'i': { A: 0.0, E: 0.0, I: 0.8, O: 0.0, U: 0.0 },
      'o': { A: 0.0, E: 0.0, I: 0.0, O: 0.8, U: 0.0 },
      'u': { A: 0.0, E: 0.0, I: 0.0, O: 0.0, U: 0.8 }
    }

    // Default neutral pose
    this.neutralPose = { A: 0.0, E: 0.0, I: 0.0, O: 0.0, U: 0.0 }
  }

  /**
   * Get morph target weights for a phoneme
   * @param {string} phoneme - Phoneme character (A, E, I, O, U, etc.)
   * @returns {Object} Morph target weight object
   */
  getMorphWeights(phoneme) {
    if (!phoneme || phoneme === 'rest' || phoneme === ' ') {
      return { ...this.neutralPose }
    }

    const weights = this.phonemeMap[phoneme]
    return weights ? { ...weights } : { ...this.neutralPose }
  }

  /**
   * Interpolate between two phoneme states
   * @param {string} fromPhoneme - Starting phoneme
   * @param {string} toPhoneme - Ending phoneme
   * @param {number} t - Interpolation factor (0-1)
   * @returns {Object} Interpolated morph weights
   */
  interpolatePhonemes(fromPhoneme, toPhoneme, t) {
    const fromWeights = this.getMorphWeights(fromPhoneme)
    const toWeights = this.getMorphWeights(toPhoneme)

    const result = {}
    for (const key of Object.keys(fromWeights)) {
      result[key] = fromWeights[key] * (1 - t) + toWeights[key] * t
    }

    return result
  }

  /**
   * Get morph target names array
   * @returns {Array<string>} Array of morph target names
   */
  getMorphTargetNames() {
    return ['A', 'E', 'I', 'O', 'U']
  }

  /**
   * Validate phoneme data
   * @param {Array} phonemes - Phoneme array with timing data
   * @returns {boolean} True if valid
   */
  validatePhonemes(phonemes) {
    if (!Array.isArray(phonemes)) return false

    for (const phoneme of phonemes) {
      if (!phoneme.phoneme || typeof phoneme.start !== 'number' || typeof phoneme.end !== 'number') {
        return false
      }
    }

    return true
  }
}
