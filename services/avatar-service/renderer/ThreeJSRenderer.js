/**
 * Production Three.js renderer for server-side avatar video generation
 * Uses face.glb with modular model support
 */
import { PNG } from 'pngjs'
import * as THREE from 'three'
import { MorphTargetAdapter } from '../../../ai-orchestra-simulation/phase3-integration/src/adapters/MorphTargetAdapter.js'
import { PhonemeMapper } from '../../../ai-orchestra-simulation/phase3-integration/src/animation/PhonemeMapper.js'
import { ModelManager } from '../../../ai-orchestra-simulation/phase3-integration/src/core/ModelManager.js'

// Mock document and canvas for headless THREE.js
if (typeof document === 'undefined') {
  global.document = {
    createElementNS: (ns, tag) => {
      if (tag === 'canvas') {
        return {
          getContext: () => null,
          width: 1920,
          height: 1080,
          style: {}
        }
      }
      return {}
    },
    createElement: (tag) => {
      if (tag === 'canvas') {
        return {
          getContext: () => null,
          width: 1920,
          height: 1080,
          style: {}
        }
      }
      return {}
    }
  }
}

// Global caches for performance optimization
const globalModelCache = new Map()
const globalRendererCache = new Map()
const frameBufferPool = []
const MAX_FRAME_BUFFERS = 10

export class ThreeJSRenderer {
  constructor(config) {
    this.config = config
    this.cacheKey = JSON.stringify(config.models) // Cache key based on model config

    // Use global model cache to avoid recreating models
    if (!globalModelCache.has(this.cacheKey)) {
      this.modelManager = new ModelManager(config.models)
      globalModelCache.set(this.cacheKey, this.modelManager)
    } else {
      this.modelManager = globalModelCache.get(this.cacheKey)
    }

    this.phonemeMapper = new PhonemeMapper()
    this.scene = null
    this.camera = null
    this.renderer = null
    this.modelAdapter = null
  }

  /**
   * Initialize Three.js scene with specified model
   * @param {string} modelKey - Model to use (defaults to production model)
   */
  async initialize(modelKey = 'face') {
    // Load model
    const model = await this.modelManager.loadModel(modelKey)

    // Create adapter
    this.modelAdapter = new MorphTargetAdapter(
      model,
      this.config.models[modelKey],
      this.phonemeMapper
    )

    // Setup Three.js scene
    this.setupScene()
    this.setupCamera()
    await this.setupRenderer()
    this.setupLighting()

    // Add model to scene
    this.scene.add(model)

    console.log(`ThreeJSRenderer initialized with model: ${modelKey}`)
    console.log(`Model metadata:`, this.modelManager.modelMetadata.get(modelKey))
  }

  setupScene() {
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(0x1a233f)  // Professional background
    // Remove fog for clean avatar presentation
    // this.scene.fog = new THREE.Fog(0x1a233f, 100, 1000)
  }

  setupCamera() {
    this.camera = new THREE.PerspectiveCamera(
      35, // FIXED: Narrower FOV (was 45) for better face focus
      1920 / 1080, // Aspect ratio
      0.1, // Near
      1000 // Far
    )
    // FIXED: Better camera positioning for face focus
    this.camera.position.set(0, 1.4, 2.2)  // Higher and further back (was 0, 1.2, 1.8)
    this.camera.lookAt(0, 1.3, 0)  // FIXED: Center on face area (was 0, 1.0, 0)
  }

  async setupRenderer() {
    // Check global renderer cache first
    if (globalRendererCache.has('webgl_renderer')) {
      this.renderer = globalRendererCache.get('webgl_renderer')
      console.log('Using cached WebGL renderer')
      return
    }

    // For production - use headless canvas with WebGL
    try {
      console.log('Attempting to import canvas and gl packages...')
      const { createCanvas } = await import('canvas')
      const glModule = await import('gl')

      const width = 1920
      const height = 1080

      // Create headless canvas
      const canvas = createCanvas(width, height)
      console.log('Headless canvas created')

      // Create WebGL context
      const gl = glModule.default(width, height, { preserveDrawingBuffer: true })
      console.log('WebGL context created')

      // Create THREE.js renderer with canvas and context
      this.renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        context: gl,
        antialias: true,
        preserveDrawingBuffer: true
      })
      this.renderer.setSize(width, height)

      // Cache the renderer for reuse
      globalRendererCache.set('webgl_renderer', this.renderer)
      console.log('Using headless WebGL renderer with canvas (cached)')
    } catch (error) {
      // Fallback for development - create renderer without context
      // This won't actually render but allows testing the API
      console.warn('Headless WebGL not available, using mock renderer for development:', error.message)
      this.renderer = {
        render: () => {},
        getContext: () => ({
          readPixels: () => new Uint8Array(1920 * 1080 * 4)
        }),
        dispose: () => {}
      }
    }
  }  setupLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    this.scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(5, 10, 7.5)
    this.scene.add(directionalLight)
  }

  /**
   * Render frame with phoneme animation and optional emotion weights
   * @param {Array} phonemes - Phoneme timing data
   * @param {number} currentTime - Current time in seconds
   * @param {Object} emotionWeights - Optional emotion morph target weights
   * @returns {Promise<Buffer>} - Image buffer
   */
  async renderFrame(phonemes, currentTime, emotionWeights = null) {
    // For mock renderer, generate a simple colored image
    if (!this.renderer || !this.renderer.getContext) {
      // Animate the model first to update morph targets
      if (this.modelAdapter) {
        if (emotionWeights) {
          this.modelAdapter.animateWithEmotion(phonemes, currentTime, emotionWeights)
        } else {
          this.modelAdapter.animate(phonemes, currentTime)
        }
      }
      return this._generateMockFrame(phonemes, currentTime, emotionWeights)
    }

    // Try real rendering first
    try {
      // Animate model with optional emotion blending
      if (this.modelAdapter) {
        if (emotionWeights) {
          this.modelAdapter.animateWithEmotion(phonemes, currentTime, emotionWeights)
        } else {
          this.modelAdapter.animate(phonemes, currentTime)
        }
      }

      // Render scene
      this.renderer.render(this.scene, this.camera)

      // Get pixels
      const width = 1920
      const height = 1080
      const pixels = new Uint8Array(width * height * 4)
      const gl_context = this.renderer.getContext()
      gl_context.readPixels(0, 0, width, height, gl_context.RGBA, gl_context.UNSIGNED_BYTE, pixels)

      // Convert to PNG buffer
      return this._pixelsToPNG(pixels, width, height)
    } catch (error) {
      console.warn('Real rendering failed, using mock frame:', error.message)
      return this._generateMockFrame(phonemes, currentTime, emotionWeights)
    }
  }

  /**
   * Generate mock frame for testing - now with avatar shape and morph targets + emotions
   * @private
   */
  _generateMockFrame(phonemes, currentTime, emotionWeights = null) {
    const width = 1920
    const height = 1080

    // Get frame buffer from pool or create new one
    let pixels = this._getFrameBuffer(width, height)

    // Fast background fill using typed array operations
    const bgColor = new Uint32Array([0xFF3F1A1A]) // BGRA format for faster copying
    const bgView = new Uint32Array(pixels.buffer)
    bgView.fill(bgColor[0])

    // Find current phoneme
    const currentPhoneme = phonemes.find(p => currentTime >= p.start && currentTime <= p.end)
    const phoneme = currentPhoneme ? currentPhoneme.phoneme : 'rest'

    // Get morph target influences from the model adapter
    let jawOpen = 0, mouthFunnel = 0, mouthClose = 0, mouthSmile = 0
    let eyebrowRaise = 0, eyebrowFrown = 0, eyeWiden = 0, eyeNarrow = 0, mouthFrown = 0, cheekRaise = 0

    if (this.modelAdapter && this.modelAdapter.morphTargetMesh && this.modelAdapter.morphTargetMesh.morphTargetInfluences) {
      const influences = this.modelAdapter.morphTargetMesh.morphTargetInfluences
      jawOpen = influences[0] || 0        // jawOpen
      mouthFunnel = influences[1] || 0     // mouthFunnel
      mouthClose = influences[2] || 0      // mouthClose
      mouthSmile = influences[3] || 0      // mouthSmile
      eyebrowRaise = influences[4] || 0    // eyebrowRaise
      eyebrowFrown = influences[5] || 0    // eyebrowFrown
      eyeWiden = influences[6] || 0        // eyeWiden
      eyeNarrow = influences[7] || 0       // eyeNarrow
      mouthFrown = influences[8] || 0      // mouthFrown
      cheekRaise = influences[9] || 0      // cheekRaise
    }

    // Pre-calculate avatar dimensions
    const centerX = width / 2
    const centerY = height / 2
    const faceRadius = 150
    const faceRadiusSq = faceRadius * faceRadius

    // Draw face circle using optimized algorithm
    this._drawCircleFast(pixels, width, height, centerX, centerY, faceRadius, 0xFFFFE0FF) // Skin color BGRA

    // Draw eyes
    const eyeY = centerY - 30
    const eyeRadius = 15
    this._drawCircleFast(pixels, width, height, centerX - 40, eyeY, eyeRadius, 0xFFFFFFFF) // White BGRA
    this._drawCircleFast(pixels, width, height, centerX + 40, eyeY, eyeRadius, 0xFFFFFFFF)

    // Draw mouth based on morph targets
    const mouthY = centerY + 40
    const mouthWidth = 80 + (jawOpen * 40)
    const mouthHeight = 20 + (jawOpen * 30)

    let mouthShape = 'neutral'
    if (mouthSmile > 0.5) mouthShape = 'smile'
    else if (mouthFunnel > 0.5) mouthShape = 'funnel'
    else if (mouthClose > 0.5) mouthShape = 'close'

    this._drawMouth(pixels, width, height, centerX, mouthY, mouthWidth, mouthHeight, mouthShape)

    // Add text overlays
    this._drawTextFast(pixels, width, height, `Phoneme: ${phoneme}`, 50, 50, 0xFFFFFFFF)
    this._drawTextFast(pixels, width, height, `Time: ${currentTime.toFixed(2)}s`, 50, 80, 0xFFFFFFFF)
    this._drawTextFast(pixels, width, height, `Jaw: ${(jawOpen * 100).toFixed(0)}%`, 50, 110, 0xFFFFFF00)

    // Add emotion information if available
    if (emotionWeights) {
      this._drawTextFast(pixels, width, height, `Emotion: ${emotionWeights.length > 0 ? 'Active' : 'None'}`, 50, 140, 0xFF00FF00)
      this._drawTextFast(pixels, width, height, `Eyebrow: ${(eyebrowRaise * 100).toFixed(0)}%`, 50, 170, 0xFF00FFFF)
      this._drawTextFast(pixels, width, height, `Eyes: ${(eyeWiden * 100).toFixed(0)}%`, 50, 200, 0xFF00FFFF)
    }

    return this._pixelsToPNG(pixels, width, height).finally(() => {
      // Return buffer to pool
      this._returnFrameBuffer(pixels)
    })
  }

  /**
   * Get frame buffer from pool or create new one
   * @private
   */
  _getFrameBuffer(width, height) {
    const size = width * height * 4
    for (let i = 0; i < frameBufferPool.length; i++) {
      if (frameBufferPool[i].length === size) {
        return frameBufferPool.splice(i, 1)[0]
      }
    }
    return new Uint8Array(size)
  }

  /**
   * Return frame buffer to pool for reuse
   * @private
   */
  _returnFrameBuffer(buffer) {
    if (frameBufferPool.length < MAX_FRAME_BUFFERS) {
      frameBufferPool.push(buffer)
    }
  }

  /**
   * Fast circle drawing using optimized algorithm
   * @private
   */
  _drawCircleFast(pixels, width, height, cx, cy, radius, color) {
    const radiusSq = radius * radius
    const minY = Math.max(0, Math.floor(cy - radius))
    const maxY = Math.min(height - 1, Math.floor(cy + radius))
    const minX = Math.max(0, Math.floor(cx - radius))
    const maxX = Math.min(width - 1, Math.floor(cx + radius))

    for (let y = minY; y <= maxY; y++) {
      const dy = y - cy
      const dySq = dy * dy
      const dx = Math.sqrt(radiusSq - dySq)
      const x1 = Math.max(minX, Math.floor(cx - dx))
      const x2 = Math.min(maxX, Math.floor(cx + dx))

      // Fill horizontal line
      const startIdx = (y * width + x1) * 4
      const endIdx = (y * width + x2) * 4
      for (let i = startIdx; i <= endIdx; i += 4) {
        pixels[i] = color & 0xFF         // B
        pixels[i + 1] = (color >> 8) & 0xFF  // G
        pixels[i + 2] = (color >> 16) & 0xFF // R
        pixels[i + 3] = (color >> 24) & 0xFF // A
      }
    }
  }

  /**
   * Draw mouth shape based on morph targets
   * @private
   */
  _drawMouth(pixels, width, height, cx, cy, width_mouth, height_mouth, shape) {
    const mouthColor = 0xFFFF32C8 // Red BGRA

    if (shape === 'close') {
      // Thin horizontal line
      const y = cy
      const x1 = Math.floor(cx - width_mouth)
      const x2 = Math.floor(cx + width_mouth)
      for (let x = x1; x <= x2; x++) {
        if (x >= 0 && x < width && y >= 0 && y < height) {
          const idx = (y * width + x) * 4
          pixels[idx] = mouthColor & 0xFF
          pixels[idx + 1] = (mouthColor >> 8) & 0xFF
          pixels[idx + 2] = (mouthColor >> 16) & 0xFF
          pixels[idx + 3] = (mouthColor >> 24) & 0xFF
        }
      }
    } else {
      // Filled ellipse
      const a = width_mouth
      const b = height_mouth
      const aSq = a * a
      const bSq = b * b

      for (let y = cy - b; y <= cy + b; y++) {
        if (y < 0 || y >= height) continue
        const dy = y - cy
        const dySq = dy * dy
        const dx = Math.sqrt((aSq * bSq - aSq * dySq) / bSq)
        const x1 = Math.floor(cx - dx)
        const x2 = Math.floor(cx + dx)

        for (let x = x1; x <= x2; x++) {
          if (x >= 0 && x < width) {
            const idx = (y * width + x) * 4
            pixels[idx] = mouthColor & 0xFF
            pixels[idx + 1] = (mouthColor >> 8) & 0xFF
            pixels[idx + 2] = (mouthColor >> 16) & 0xFF
            pixels[idx + 3] = (mouthColor >> 24) & 0xFF
          }
        }
      }
    }
  }

  /**
   * Fast text drawing using pre-calculated character patterns
   * @private
   */
  _drawTextFast(pixels, width, height, text, x, y, color) {
    const charWidth = 6
    const charHeight = 8

    for (let i = 0; i < text.length; i++) {
      const char = text[i]
      const charX = x + (i * charWidth)
      const charY = y

      // Simple character patterns (could be expanded)
      const pattern = this._getCharPattern(char)

      for (let dy = 0; dy < charHeight; dy++) {
        for (let dx = 0; dx < charWidth; dx++) {
          if (pattern[dy] & (1 << (charWidth - 1 - dx))) {
            const px = charX + dx
            const py = charY + dy
            if (px >= 0 && px < width && py >= 0 && py < height) {
              const idx = (py * width + px) * 4
              pixels[idx] = color & 0xFF
              pixels[idx + 1] = (color >> 8) & 0xFF
              pixels[idx + 2] = (color >> 16) & 0xFF
              pixels[idx + 3] = (color >> 24) & 0xFF
            }
          }
        }
      }
    }
  }

  /**
   * Get simple character pattern (bitmap)
   * @private
   */
  _getCharPattern(char) {
    // Simple 6x8 character patterns
    const patterns = {
      'A': [0x1C, 0x22, 0x22, 0x3E, 0x22, 0x22, 0x22, 0x00],
      'B': [0x3C, 0x22, 0x3C, 0x22, 0x22, 0x3C, 0x00, 0x00],
      'C': [0x1C, 0x22, 0x20, 0x20, 0x22, 0x1C, 0x00, 0x00],
      'D': [0x3C, 0x22, 0x22, 0x22, 0x22, 0x3C, 0x00, 0x00],
      'E': [0x3E, 0x20, 0x3C, 0x20, 0x20, 0x3E, 0x00, 0x00],
      'F': [0x3E, 0x20, 0x3C, 0x20, 0x20, 0x20, 0x00, 0x00],
      'G': [0x1C, 0x22, 0x20, 0x2E, 0x22, 0x1C, 0x00, 0x00],
      'H': [0x22, 0x22, 0x3E, 0x22, 0x22, 0x22, 0x00, 0x00],
      'I': [0x1C, 0x08, 0x08, 0x08, 0x08, 0x1C, 0x00, 0x00],
      'J': [0x0E, 0x04, 0x04, 0x04, 0x24, 0x18, 0x00, 0x00],
      'K': [0x22, 0x24, 0x38, 0x24, 0x22, 0x00, 0x00, 0x00],
      'L': [0x20, 0x20, 0x20, 0x20, 0x20, 0x3E, 0x00, 0x00],
      'M': [0x22, 0x36, 0x2A, 0x22, 0x22, 0x00, 0x00, 0x00],
      'N': [0x22, 0x32, 0x2A, 0x26, 0x22, 0x00, 0x00, 0x00],
      'O': [0x1C, 0x22, 0x22, 0x22, 0x22, 0x1C, 0x00, 0x00],
      'P': [0x3C, 0x22, 0x3C, 0x20, 0x20, 0x20, 0x00, 0x00],
      'Q': [0x1C, 0x22, 0x22, 0x2A, 0x24, 0x1A, 0x00, 0x00],
      'R': [0x3C, 0x22, 0x3C, 0x24, 0x22, 0x00, 0x00, 0x00],
      'S': [0x1E, 0x20, 0x1C, 0x02, 0x22, 0x1C, 0x00, 0x00],
      'T': [0x3E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00],
      'U': [0x22, 0x22, 0x22, 0x22, 0x22, 0x1C, 0x00, 0x00],
      'V': [0x22, 0x22, 0x22, 0x22, 0x14, 0x08, 0x00, 0x00],
      'W': [0x22, 0x22, 0x22, 0x2A, 0x36, 0x22, 0x00, 0x00],
      'X': [0x22, 0x14, 0x08, 0x08, 0x14, 0x22, 0x00, 0x00],
      'Y': [0x22, 0x14, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00],
      'Z': [0x3E, 0x02, 0x04, 0x08, 0x10, 0x3E, 0x00, 0x00],
      '0': [0x1C, 0x22, 0x26, 0x2A, 0x32, 0x22, 0x1C, 0x00],
      '1': [0x08, 0x18, 0x08, 0x08, 0x08, 0x1C, 0x00, 0x00],
      '2': [0x1C, 0x22, 0x02, 0x1C, 0x20, 0x3E, 0x00, 0x00],
      '3': [0x1C, 0x22, 0x0C, 0x02, 0x22, 0x1C, 0x00, 0x00],
      '4': [0x04, 0x0C, 0x14, 0x24, 0x3E, 0x04, 0x00, 0x00],
      '5': [0x3E, 0x20, 0x3C, 0x02, 0x22, 0x1C, 0x00, 0x00],
      '6': [0x1C, 0x20, 0x3C, 0x22, 0x22, 0x1C, 0x00, 0x00],
      '7': [0x3E, 0x02, 0x04, 0x08, 0x10, 0x10, 0x00, 0x00],
      '8': [0x1C, 0x22, 0x1C, 0x22, 0x22, 0x1C, 0x00, 0x00],
      '9': [0x1C, 0x22, 0x22, 0x1E, 0x02, 0x1C, 0x00, 0x00],
      '.': [0x00, 0x00, 0x00, 0x00, 0x08, 0x08, 0x00, 0x00],
      ':': [0x00, 0x08, 0x08, 0x00, 0x08, 0x08, 0x00, 0x00],
      ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
      '%': [0x22, 0x14, 0x08, 0x14, 0x22, 0x00, 0x00, 0x00],
      's': [0x00, 0x1E, 0x20, 0x1C, 0x02, 0x3C, 0x00, 0x00]
    }

    return patterns[char] || patterns[' ']
  }

  /**
   * Convert RGBA pixels to PNG buffer
   * @private
   */
  _pixelsToPNG(pixels, width, height) {
    return new Promise((resolve, reject) => {
      const png = new PNG({
        width: width,
        height: height,
        colorType: 6, // RGBA
        bgColor: { red: 0, green: 0, blue: 0 }
      })

      // Copy pixels to PNG data
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          const idx = (y * width + x) * 4
          const pngIdx = (y * width + x) * 4

          png.data[pngIdx] = pixels[idx]     // R
          png.data[pngIdx + 1] = pixels[idx + 1] // G
          png.data[pngIdx + 2] = pixels[idx + 2] // B
          png.data[pngIdx + 3] = pixels[idx + 3] // A
        }
      }

      const chunks = []
      png.on('data', chunk => chunks.push(chunk))
      png.on('end', () => resolve(Buffer.concat(chunks)))
      png.on('error', reject)

      png.pack()
    })
  }

  /**
   * Switch to different model at runtime
   * @param {string} modelKey
   */
  async switchModel(modelKey) {
    // Remove current model from scene
    if (this.modelAdapter && this.modelAdapter.model) {
      this.scene.remove(this.modelAdapter.model)
    }

    // Load new model
    const model = await this.modelManager.switchModel(modelKey)

    // Create new adapter
    this.modelAdapter = new MorphTargetAdapter(
      model,
      this.config.models[modelKey],
      this.phonemeMapper
    )

    // Add to scene
    this.scene.add(model)

    console.log(`Switched to model: ${modelKey}`)
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    if (this.renderer) {
      this.renderer.dispose()
    }
    if (this.modelManager) {
      this.modelManager.cleanup(this.modelAdapter.model)
    }
  }
}
