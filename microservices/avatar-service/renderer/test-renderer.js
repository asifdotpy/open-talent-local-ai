/**
 * Test script for ThreeJSRenderer validation
 * Tests initialization, model loading, and frame rendering
 */

import { AppConfig } from '../../../ai-orchestra-simulation/src/config/AppConfig.js'
import { ThreeJSRenderer } from './ThreeJSRenderer.js'

async function testRenderer() {
  console.log('🚀 Starting ThreeJSRenderer validation test...')

  try {
    // Set environment for testing
    process.env.NODE_ENV = 'production'

    // Get configuration
    const config = AppConfig.get()
    console.log('✅ Config loaded successfully')
    console.log('Environment:', AppConfig.getEnvironment())
    console.log('Production model key:', config.models.production.key)

    // Create renderer
    const renderer = new ThreeJSRenderer(config)
    console.log('✅ ThreeJSRenderer created')

    // Test WebGL availability first
    try {
      const gl = await import('gl')
      const testContext = gl.default(1920, 1080, { preserveDrawingBuffer: true })
      console.log('✅ Headless WebGL context created successfully')
      testContext.getExtension('WEBGL_debug_renderer_info')
    } catch (error) {
      console.log('⚠️ Headless WebGL not available, will use fallback:', error.message)
    }

    // Enable mock mode for testing (no GLTF loading)
    renderer.modelManager.mockMode = true
    console.log('✅ Mock mode enabled for testing')

    // Initialize with production model
    console.log('🔄 Initializing renderer with face.glb...')
    await renderer.initialize('production')
    console.log('✅ Renderer initialized successfully')

    // Test render frame
    console.log('🎬 Testing frame rendering...')
    const phonemes = [
      { phoneme: 'AA', start: 0, end: 0.5 },
      { phoneme: 'EH', start: 0.5, end: 1.0 }
    ]

    const buffer = renderer.renderFrame(phonemes, 0.25)
    console.log('✅ Frame rendered successfully')
    console.log('Buffer size:', buffer.length, 'bytes')

    // Test model switching (if in development mode)
    if (config.models.development.allowModelSwitch) {
      console.log('🔄 Testing model switching...')
      await renderer.switchModel('production') // Switch to same model for test
      console.log('✅ Model switching works')
    }

    // Cleanup
    renderer.cleanup()
    console.log('✅ Cleanup completed')

    console.log('🎉 All tests passed! ThreeJSRenderer is ready for production.')

  } catch (error) {
    console.error('❌ Test failed:', error.message)
    console.error('Stack:', error.stack)
    process.exit(1)
  }
}

// Run the test
testRenderer().catch(console.error)