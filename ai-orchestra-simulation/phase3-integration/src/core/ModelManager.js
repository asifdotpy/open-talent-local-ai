/**
 * Phase 3: ModelManager - Manages 3D model loading and caching
 * Handles GLTF/GLB model loading with Draco decompression
 */

import * as THREE from 'three'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

export class ModelManager {
  constructor() {
    this.models = new Map()
    this.modelMetadata = new Map()
    this.loader = null
    this.initializeLoader()
  }

  initializeLoader() {
    this.loader = new GLTFLoader()

    // Setup Draco loader for compressed models
    const dracoLoader = new DRACOLoader()
    dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/')
    this.loader.setDRACOLoader(dracoLoader)

    console.log('ModelManager: GLTF loader initialized with Draco support')
  }

  /**
   * Load a 3D model by key
   * @param {string} modelKey - Model identifier
   * @returns {Promise<THREE.Group>} Loaded model
   */
  async loadModel(modelKey) {
    if (this.models.has(modelKey)) {
      console.log(`ModelManager: Returning cached model: ${modelKey}`)
      return this.models.get(modelKey).clone()
    }

    // For now, we'll create a simple placeholder model
    // In production, this would load the actual face.glb
    console.log(`ModelManager: Creating placeholder model for: ${modelKey}`)

    const model = this.createPlaceholderModel()
    this.models.set(modelKey, model)

    // Store metadata
    this.modelMetadata.set(modelKey, {
      morphTargets: 5, // A, E, I, O, U
      triangles: 1000,
      hasDraco: false,
      loadTime: Date.now()
    })

    return model.clone()
  }

  /**
   * Create a placeholder 3D model with morph targets
   * This simulates the face.glb model structure
   * @returns {THREE.Group} Placeholder model
   */
  createPlaceholderModel() {
    const group = new THREE.Group()

    // Create a simple face-like geometry
    const geometry = new THREE.SphereGeometry(1, 32, 32)

    // Add morph targets for phonemes
    const morphTargets = []
    const phonemeNames = ['A', 'E', 'I', 'O', 'U']

    phonemeNames.forEach((phoneme, index) => {
      const morphGeometry = geometry.clone()

      // Simple morphing based on phoneme
      const positions = morphGeometry.attributes.position.array
      for (let i = 0; i < positions.length; i += 3) {
        const x = positions[i]
        const y = positions[i + 1]
        const z = positions[i + 2]

        // Apply different deformations based on phoneme
        switch (phoneme) {
          case 'A':
            positions[i + 1] = y * 1.2 // Widen vertically
            break
          case 'E':
            positions[i] = x * 1.1 // Widen horizontally
            break
          case 'I':
            positions[i + 1] = y * 0.9 // Narrow vertically
            break
          case 'O':
            positions[i + 2] = z * 1.1 // Push forward
            break
          case 'U':
            positions[i] = x * 0.9 // Narrow horizontally
            break
        }
      }

      morphTargets.push(morphGeometry)
    })

    // Set up morph targets on the base geometry
    geometry.morphTargets = phonemeNames.map(name => ({ name }))
    geometry.morphAttributes.position = morphTargets

    // Create material
    const material = new THREE.MeshLambertMaterial({
      color: 0xffdbac, // Skin tone
      transparent: false
    })

    // Create mesh
    const mesh = new THREE.Mesh(geometry, material)
    mesh.name = 'FaceMesh'

    // Add morph target dictionary for easy access
    mesh.morphTargetDictionary = {
      A: 0,
      E: 1,
      I: 2,
      O: 3,
      U: 4
    }

    // Initialize morph target influences
    mesh.morphTargetInfluences = [0, 0, 0, 0, 0]

    group.add(mesh)

    console.log('ModelManager: Created placeholder model with morph targets')
    return group
  }

  /**
   * Switch to a different model
   * @param {string} modelKey - New model key
   * @returns {Promise<THREE.Group>} New model
   */
  async switchModel(modelKey) {
    return this.loadModel(modelKey)
  }

  /**
   * Cleanup resources
   * @param {THREE.Group} model - Model to cleanup
   */
  cleanup(model) {
    if (model) {
      model.traverse((child) => {
        if (child.isMesh) {
          if (child.geometry) child.geometry.dispose()
          if (child.material) {
            if (Array.isArray(child.material)) {
              child.material.forEach(mat => mat.dispose())
            } else {
              child.material.dispose()
            }
          }
        }
      })
    }
  }

  /**
   * Get all loaded models
   * @returns {Map} Model cache
   */
  getLoadedModels() {
    return this.models
  }

  /**
   * Clear model cache
   */
  clearCache() {
    for (const [key, model] of this.models.entries()) {
      this.cleanup(model)
    }
    this.models.clear()
    this.modelMetadata.clear()
    console.log('ModelManager: Cache cleared')
  }
}
