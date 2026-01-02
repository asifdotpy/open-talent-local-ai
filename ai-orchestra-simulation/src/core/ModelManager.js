/**
 * ModelManager.js - Abstraction layer for avatar models
 * Handles loading, validation, and switching between models
 * Integrated with FaceGLBLoader for 52 ARKit blendshape support
 */
import * as THREE from 'three'
import { FaceGLBLoader } from './FaceGLBLoader.js'

export class ModelManager {
  constructor(config, options = {}) {
    this.config = config
    this.mockMode = options.mockMode || false
    this.currentModel = null
    this.modelCache = new Map()
    this.modelMetadata = new Map()
    this.faceGLBLoader = new FaceGLBLoader() // Initialize FaceGLBLoader for production
  }

  /**
   * Load model with validation and caching
   * @param {string} modelKey - Model identifier (e.g., 'face', 'custom')
   * @returns {Promise<Object3D>}
   */
  async loadModel(modelKey) {
    // Check cache first
    if (this.modelCache.has(modelKey)) {
      return this.modelCache.get(modelKey)
    }

    const modelConfig = this.config[modelKey]
    if (!modelConfig) {
      throw new Error(`Model '${modelKey}' not found in configuration`)
    }

    // Load model (use FaceGLBLoader for production models)
    let model
    if (modelKey === 'face' && this.config.useFaceGLBLoader !== false) {
      try {
        console.log('📦 Loading production face.glb with FaceGLBLoader...')
        model = await this.faceGLBLoader.load(modelConfig.path)
      } catch (error) {
        console.warn('⚠️ FaceGLBLoader failed, falling back to simplified model:', error.message)
        model = await this.loadGLTF(modelConfig.path)
      }
    } else {
      model = await this.loadGLTF(modelConfig.path)
    }

    // Validate model meets requirements
    const validation = this.validateModel(model, modelConfig.constraints)
    if (!validation.valid) {
      console.error('Model validation failed:', validation.errors)
      // Try fallback model
      if (modelConfig.fallback && modelConfig.fallback !== modelKey) {
        console.warn(`Loading fallback model: ${modelConfig.fallback}`)
        return this.loadModel(modelConfig.fallback)
      }
      throw new Error('Model validation failed and no fallback available')
    }

    // Store metadata with enhanced logging
    const vertexCount = this.getVertexCount(model)
    const morphTargets = this.extractMorphTargets(model)

    this.modelMetadata.set(modelKey, {
      morphTargets,
      vertexCount,
      capabilities: modelConfig.capabilities
    })

    // Enhanced logging for debugging
    console.log(`✅ Model loaded successfully: ${modelKey}`)
    console.log(`   Vertices: ${vertexCount}`)
    console.log(`   Morph targets: ${morphTargets.size}`)

    if (morphTargets.size > 0) {
      console.log(`   Morph target mapping:`)
      let count = 0
      for (const [name, index] of morphTargets.entries()) {
        if (count < 10) { // Show first 10
          console.log(`     [${index}] ${name}`)
          count++
        }
      }
      if (morphTargets.size > 10) {
        console.log(`     ... and ${morphTargets.size - 10} more targets`)
      }
    }

    // Log mesh details
    let meshCount = 0
    model.traverse((child) => {
      if (child.isMesh) {
        meshCount++
        console.log(`   Mesh ${meshCount}: ${child.name || 'unnamed'}`)
        console.log(`     - Vertices: ${child.geometry.attributes.position?.count || 0}`)
        console.log(`     - Has morph targets: ${child.morphTargetInfluences?.length > 0}`)
        if (child.morphTargetInfluences) {
          console.log(`     - Morph target count: ${child.morphTargetInfluences.length}`)
        }
      }
    })

    // Cache model
    this.modelCache.set(modelKey, model)
    this.currentModel = model

    return model
  }

  /**
   * Validate model against requirements
   * @param {Object3D} model
   * @param {Object} constraints
   * @returns {Object} validation result
   */
  validateModel(model, constraints) {
    const errors = []
    const warnings = []

    // Check vertex count
    const vertexCount = this.getVertexCount(model)
    if (vertexCount > constraints.maxVertices) {
      errors.push(`Vertex count ${vertexCount} exceeds limit ${constraints.maxVertices}`)
    }

    // Check morph targets
    const morphTargets = this.extractMorphTargets(model)
    console.log(`🔍 Validating morph targets. Found: ${morphTargets.size} targets`)
    console.log(`   Required: ${constraints.requiredMorphTargets}`)
    console.log(`   Available: ${Array.from(morphTargets.keys()).join(', ')}`)

    const requiredTargets = constraints.requiredMorphTargets || []

    for (const required of requiredTargets) {
      if (!morphTargets.has(required)) {
        console.log(`❌ Missing required morph target: ${required}`)
        errors.push(`Missing required morph target: ${required}`)
      } else {
        console.log(`✅ Found required morph target: ${required}`)
      }
    }

    // Check morph target count
    if (morphTargets.size > constraints.maxMorphTargets) {
      warnings.push(`Morph target count ${morphTargets.size} exceeds recommended ${constraints.maxMorphTargets}`)
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      metadata: {
        vertexCount,
        morphTargetCount: morphTargets.size,
        morphTargets: Array.from(morphTargets.keys())
      }
    }
  }

  /**
   * Get morph target mapping
   * @returns {Map<string, number>}
   */
  getMorphTargetMapping() {
    if (!this.currentModel) {
      throw new Error('No model loaded')
    }
    return this.modelMetadata.get(this.getCurrentModelKey()).morphTargets
  }

  /**
   * Switch to different model at runtime
   * @param {string} modelKey
   */
  async switchModel(modelKey) {
    // Cleanup current model resources
    if (this.currentModel) {
      this.cleanup(this.currentModel)
    }

    // Load new model
    return this.loadModel(modelKey)
  }

  /**
   * Extract morph targets from model
   * @private
   */
  extractMorphTargets(model) {
    const targets = new Map()
    model.traverse((child) => {
      if (child.isMesh && child.morphTargetDictionary) {
        Object.entries(child.morphTargetDictionary).forEach(([name, index]) => {
          targets.set(name, index)
        })
      }
    })
    return targets
  }

  /**
   * Get total vertex count
   * @private
   */
  getVertexCount(model) {
    let count = 0
    model.traverse((child) => {
      if (child.isMesh && child.geometry) {
        count += child.geometry.attributes.position.count
      }
    })
    return count
  }

  /**
   * Cleanup model resources
   * @private
   */
  cleanup(model) {
    model.traverse((child) => {
      if (child.isMesh) {
        child.geometry.dispose()
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

  /**
   * Get current model key
   * @private
   */
  getCurrentModelKey() {
    for (const [key, model] of this.modelCache.entries()) {
      if (model === this.currentModel) {
        return key
      }
    }
    return null
  }

  /**
   * Load GLTF model from file - Simplified Node.js compatible version
   * @private
   */
  async loadGLTF(relativePath) {
    if (this.mockMode) {
      // Return mock model for testing
      return this.createMockModel()
    }

    console.log(`Loading GLTF file: ${relativePath}`)

    // For Phase 2, create a simplified model that works for lip-sync
    // This bypasses the complex GLTF parsing issues in Node.js
    return this.createSimplifiedAvatarModel()
  }

  /**
   * Create a simplified avatar model for lip-sync rendering
   * @private
   */
  async createSimplifiedAvatarModel() {
    // Import Three.js classes dynamically
    const THREE = await import('three')
    const { Group, Mesh, SphereGeometry, MeshBasicMaterial, BufferAttribute } = THREE

    const model = new Group()
    model.name = 'SimplifiedAvatar'

    // Create a basic head geometry (sphere)
    const geometry = new SphereGeometry(1, 32, 32)

    // Add morph targets for lip-sync (required mouth shapes) + facial expressions
    geometry.morphAttributes = { position: [] }
    geometry.morphTargetDictionary = {
      // Lip-sync morph targets (0-3)
      jawOpen: 0,
      mouthFunnel: 1,
      mouthClose: 2,
      mouthSmile: 3,
      // Facial expression morph targets (4-10)
      eyebrowRaise: 4,
      eyebrowFrown: 5,
      eyeWiden: 6,
      eyeNarrow: 7,
      mouthFrown: 8,
      cheekRaise: 9
    }

    // Get original positions
    const originalPositions = geometry.attributes.position.array
    const vertexCount = originalPositions.length / 3

    // Create morph targets by modifying vertex positions
    const morphTargets = [
      // === LIP-SYNC MORPH TARGETS ===

      // jawOpen - open mouth vertically
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (y > 0.3) return [x, y + 0.3, z] // Upper lip up
        if (y < -0.3) return [x, y - 0.3, z] // Lower lip down
        return [x, y, z]
      }),

      // mouthFunnel - rounded mouth
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (y > 0 && y < 0.5 && Math.abs(x) < 0.5) {
          return [x * 1.2, y, z * 1.2] // Expand upper mouth area
        }
        if (y < 0 && y > -0.5 && Math.abs(x) < 0.5) {
          return [x * 1.2, y, z * 1.2] // Expand lower mouth area
        }
        return [x, y, z]
      }),

      // mouthClose - close mouth
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (y > 0.2) return [x, y - 0.1, z] // Bring upper lip down
        if (y < -0.2) return [x, y + 0.1, z] // Bring lower lip up
        return [x, y, z]
      }),

      // mouthSmile - smiling mouth (also used by HAPPY emotion)
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (Math.abs(y) < 0.3 && Math.abs(x) < 0.7) {
          return [x * 1.1, y + (x > 0 ? 0.1 : -0.1), z] // Curve mouth corners up
        }
        return [x, y, z]
      }),

      // === FACIAL EXPRESSION MORPH TARGETS ===

      // eyebrowRaise - raise eyebrows (surprised, questioning)
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (y > 0.5 && y < 0.8 && Math.abs(x) < 0.6 && z > 0.3) {
          return [x, y + 0.15, z] // Raise eyebrow area
        }
        return [x, y, z]
      }),

      // eyebrowFrown - furrow eyebrows (concerned, thoughtful)
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (y > 0.5 && y < 0.8 && Math.abs(x) < 0.6 && z > 0.3) {
          return [x * 0.95, y - 0.1, z] // Bring eyebrows down and closer
        }
        return [x, y, z]
      }),

      // eyeWiden - widen eyes (surprised, alert)
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (y > 0.2 && y < 0.5 && Math.abs(x) < 0.5 && z > 0.5) {
          return [x * 1.1, y * 1.15, z * 1.05] // Expand eye area
        }
        return [x, y, z]
      }),

      // eyeNarrow - narrow eyes (skeptical, focused)
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (y > 0.2 && y < 0.5 && Math.abs(x) < 0.5 && z > 0.5) {
          return [x, y * 0.85, z] // Compress eye area vertically
        }
        return [x, y, z]
      }),

      // mouthFrown - frown (sad, disappointed)
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (Math.abs(y) < 0.3 && Math.abs(x) < 0.7 && z > 0.2) {
          return [x, y - Math.abs(x) * 0.15, z] // Curve mouth corners down
        }
        return [x, y, z]
      }),

      // cheekRaise - raise cheeks (genuine smile)
      this.createMorphTarget(originalPositions, (x, y, z, index) => {
        if (y > -0.1 && y < 0.3 && Math.abs(x) > 0.3 && Math.abs(x) < 0.7 && z > 0.3) {
          return [x, y + 0.1, z * 1.05] // Raise and expand cheek area
        }
        return [x, y, z]
      })
    ]

    // Add morph targets to geometry
    morphTargets.forEach(morphTarget => {
      geometry.morphAttributes.position.push(new BufferAttribute(morphTarget, 3))
    })

    // Initialize morph target influences (now 10 targets instead of 4)
    geometry.morphTargetInfluences = new Array(10).fill(0)

    // Create material
    const material = new MeshBasicMaterial({
      color: 0xffdbac, // Skin tone
      transparent: false
    })

    // Create mesh
    const mesh = new Mesh(geometry, material)
    mesh.name = 'AvatarHead'
    mesh.morphTargetDictionary = geometry.morphTargetDictionary
    mesh.morphTargetInfluences = geometry.morphTargetInfluences

    model.add(mesh)

    console.log('Created simplified avatar model with morph targets:', Object.keys(geometry.morphTargetDictionary))

    return model
  }

  /**
   * Create a morph target by applying a transformation function
   * @private
   */
  createMorphTarget(originalPositions, transformFunc) {
    const morphPositions = new Float32Array(originalPositions.length)

    for (let i = 0; i < originalPositions.length; i += 3) {
      const x = originalPositions[i]
      const y = originalPositions[i + 1]
      const z = originalPositions[i + 2]

      const [newX, newY, newZ] = transformFunc(x, y, z, i / 3)
      morphPositions[i] = newX
      morphPositions[i + 1] = newY
      morphPositions[i + 2] = newZ
    }

    return morphPositions
  }

  /**
   * Create mock model for testing
   * @private
   */
  createMockModel() {
    const mockModel = new THREE.Group()

    // Create a simple mesh with morph targets
    const geometry = new THREE.SphereGeometry(1, 32, 32)
    geometry.morphAttributes.position = []

    // Add some morph targets
    const positions = geometry.attributes.position.array
    for (let i = 0; i < 4; i++) {
      const morphPositions = new Float32Array(positions.length)
      morphPositions.set(positions)
      // Modify some vertices for morphing
      for (let j = 0; j < morphPositions.length; j += 3) {
        morphPositions[j] += (Math.random() - 0.5) * 0.1
        morphPositions[j + 1] += (Math.random() - 0.5) * 0.1
        morphPositions[j + 2] += (Math.random() - 0.5) * 0.1
      }
      geometry.morphAttributes.position.push(new THREE.BufferAttribute(morphPositions, 3))
    }

    const material = new THREE.MeshBasicMaterial({ color: 0xff0000 })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.morphTargetDictionary = {
      jawOpen: 0,
      mouthFunnel: 1,
      mouthClose: 2,
      mouthSmile: 3
    }
    mesh.morphTargetInfluences = new Array(4).fill(0)

    mockModel.add(mesh)
    return mockModel
  }
}
