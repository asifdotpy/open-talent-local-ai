/**
 * Base adapter for avatar models
 * Allows different model types to work with same renderer
 */
export class ModelAdapter {
  constructor(model, config) {
    this.model = model
    this.config = config
  }

  /**
   * Get morph target index by phoneme
   * @param {string} phoneme
   * @returns {number|null}
   */
  getMorphTargetForPhoneme(phoneme) {
    throw new Error('Must implement getMorphTargetForPhoneme()')
  }

  /**
   * Animate model based on phoneme data
   * @param {Array} phonemes
   * @param {number} currentTime
   */
  animate(phonemes, currentTime) {
    throw new Error('Must implement animate()')
  }

  /**
   * Animate model with emotion blending
   * @param {Array} phonemes
   * @param {number} currentTime
   * @param {Object} emotionWeights - Emotion morph target weights
   */
  animateWithEmotion(phonemes, currentTime, emotionWeights) {
    throw new Error('Must implement animateWithEmotion()')
  }

  /**
   * Reset animation state
   */
  reset() {
    throw new Error('Must implement reset()')
  }
}

/**
 * Adapter for morph-target based models (face.glb, future realistic models)
 */
export class MorphTargetAdapter extends ModelAdapter {
  constructor(model, config, phonemeMapper) {
    super(model, config)
    this.phonemeMapper = phonemeMapper
    this.morphTargetMesh = this.findMorphTargetMesh()

    // Enhanced logging
    if (this.morphTargetMesh) {
      console.log(`✅ MorphTargetAdapter initialized`)
      console.log(`   Mesh: ${this.morphTargetMesh.name || 'unnamed'}`)
      console.log(`   Morph targets: ${this.morphTargetMesh.morphTargetInfluences?.length || 0}`)
      console.log(`   Vertices: ${this.morphTargetMesh.geometry.attributes.position?.count || 0}`)

      if (this.morphTargetMesh.morphTargetDictionary) {
        console.log(`   Available morph targets:`)
        for (const [name, index] of Object.entries(this.morphTargetMesh.morphTargetDictionary)) {
          console.log(`     [${index}] ${name}`)
        }
      }
    } else {
      console.warn(`⚠️  No mesh with morph targets found in model!`)
      console.log(`   Model structure:`)
      this.model.traverse((child) => {
        if (child.isMesh) {
          console.log(`     - Mesh: ${child.name || 'unnamed'}, vertices: ${child.geometry.attributes.position?.count || 0}`)
        }
      })
    }
  }

  findMorphTargetMesh() {
    let mesh = null
    let meshCount = 0

    this.model.traverse((child) => {
      if (child.isMesh) {
        meshCount++
        console.log(`   Checking mesh ${meshCount}: ${child.name || 'unnamed'}`)
        console.log(`     - Has morphTargetInfluences: ${!!child.morphTargetInfluences}`)
        console.log(`     - Influence count: ${child.morphTargetInfluences?.length || 0}`)

        if (child.morphTargetInfluences && child.morphTargetInfluences.length > 0) {
          console.log(`     ✅ Found morph target mesh!`)
          mesh = child
        }
      }
    })

    if (!mesh) {
      console.warn(`   ⚠️  No mesh with morph targets found in ${meshCount} mesh(es)`)
    }

    return mesh
  }

  getMorphTargetForPhoneme(phoneme) {
    return this.phonemeMapper.getMorphTargetIndex(phoneme)
  }

  animate(phonemes, currentTime) {
    if (!this.morphTargetMesh) return

    // Find current phoneme
    const currentPhoneme = phonemes.find(p =>
      currentTime >= p.start && currentTime <= p.end
    )

    if (currentPhoneme) {
      const targetIndex = this.getMorphTargetForPhoneme(currentPhoneme.phoneme)
      if (targetIndex !== null) {
        this.morphTargetMesh.morphTargetInfluences[targetIndex] = 1.0
      }
    } else {
      // Reset to neutral
      this.reset()
    }
  }

  animateWithEmotion(phonemes, currentTime, emotionWeights) {
    if (!this.morphTargetMesh) return

    // Reset all morph targets first
    this.morphTargetMesh.morphTargetInfluences.fill(0)

    // Apply emotion weights (indices 4-9 for expressions)
    if (emotionWeights && Array.isArray(emotionWeights)) {
      for (let i = 0; i < emotionWeights.length && i < 6; i++) {
        const emotionIndex = i + 4 // Expression targets start at index 4
        if (emotionIndex < this.morphTargetMesh.morphTargetInfluences.length) {
          this.morphTargetMesh.morphTargetInfluences[emotionIndex] = emotionWeights[i] || 0
        }
      }
    }

    // Apply phoneme weights (indices 0-3 for lip-sync)
    const currentPhoneme = phonemes.find(p =>
      currentTime >= p.start && currentTime <= p.end
    )

    if (currentPhoneme) {
      const targetIndex = this.getMorphTargetForPhoneme(currentPhoneme.phoneme)
      if (targetIndex !== null && targetIndex < 4) { // Only apply to lip-sync targets
        this.morphTargetMesh.morphTargetInfluences[targetIndex] = 1.0
      }
    }
  }

  reset() {
    if (!this.morphTargetMesh) return
    this.morphTargetMesh.morphTargetInfluences.fill(0)
  }
}

/**
 * Future adapter for bone-rigged models
 */
export class SkeletalAdapter extends ModelAdapter {
  // Placeholder for future realistic models with bone rigs
  // Will implement bone-based lip-sync when ready

  animateWithEmotion(phonemes, currentTime, emotionWeights) {
    // Placeholder - implement when skeletal models are added
    console.warn('animateWithEmotion not implemented for SkeletalAdapter')
  }
}
