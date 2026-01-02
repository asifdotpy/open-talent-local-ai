#!/usr/bin/env node

/**
 * test-gltf-loading.js - Test script to verify GLTF model loading works
 */

// Polyfill ProgressEvent for Node.js
if (typeof global.ProgressEvent === 'undefined') {
  global.ProgressEvent = class ProgressEvent {
    constructor(type, options = {}) {
      this.type = type
      this.lengthComputable = options.lengthComputable || false
      this.loaded = options.loaded || 0
      this.total = options.total || 0
    }
  }
}

import { AppConfig } from './src/config/AppConfig.js'
import { ModelManager } from './src/core/ModelManager.js'

async function testGLTFLoading() {
  try {
    console.log('Testing GLTF model loading...')

    // Get configuration
    const config = AppConfig.get()
    console.log('Config loaded:', config.models.production.key)

    // Create model manager
    const modelManager = new ModelManager(config.models)
    // Disable mock mode to test real loading
    modelManager.mockMode = false

    console.log('Loading production model...')
    const model = await modelManager.loadModel('production')

    console.log('Model loaded successfully!')
    console.log('Model type:', model.type)
    console.log('Model children:', model.children.length)

    // Check for morph targets
    let morphTargetCount = 0
    model.traverse((child) => {
      if (child.isMesh && child.morphTargetDictionary) {
        morphTargetCount++
        console.log(`Mesh with morph targets: ${child.name || 'unnamed'}`)
        console.log(`Morph targets: ${Object.keys(child.morphTargetDictionary).join(', ')}`)
      }
    })

    console.log(`Total meshes with morph targets: ${morphTargetCount}`)

    // Validate model
    const validation = modelManager.validateModel(model, config.models.production.constraints)
    console.log('Model validation:', validation.valid ? 'PASSED' : 'FAILED')
    if (!validation.valid) {
      console.error('Validation errors:', validation.errors)
    }
    if (validation.warnings.length > 0) {
      console.warn('Validation warnings:', validation.warnings)
    }

    console.log('GLTF loading test completed successfully!')

  } catch (error) {
    console.error('GLTF loading test failed:', error.message)
    console.error(error.stack)
    process.exit(1)
  }
}

testGLTFLoading()
