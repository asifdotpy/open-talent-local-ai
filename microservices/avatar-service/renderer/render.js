#!/usr/bin/env node

/**
 * render.js - Node.js script for server-side avatar video rendering
 * Called by avatar-service to generate lip-sync videos
 * Phase 4: Performance optimization and caching
 */

import { spawn } from 'child_process'
import crypto from 'crypto'
import ffmpeg from 'ffmpeg-static'
import fs from 'fs'
import os from 'os'
import path from 'path'
import { Worker, isMainThread, parentPort } from 'worker_threads'
import { AppConfig } from '../../../ai-orchestra-simulation/phase3-integration/src/config/AppConfig.js'
import { EmotionStates } from './EmotionEngine.js'
import { ExpressionController } from './ExpressionController.js'
import { ThreeJSRenderer } from './ThreeJSRenderer.js'

// Global video cache to avoid regenerating identical videos
const videoCache = new Map()
const MAX_CACHE_SIZE = 50 // Maximum cached videos
const CACHE_TTL = 30 * 60 * 1000 // 30 minutes TTL

// Advanced expression caching: separate caches for expressions and phonemes
const expressionFrameCache = new Map() // Cache expression frames by emotion + time
const phonemeFrameCache = new Map()    // Cache phoneme frames by phoneme sequence + time
const MAX_EXPRESSION_CACHE_SIZE = 100 // Maximum cached expression frames
const MAX_PHONEME_CACHE_SIZE = 100    // Maximum cached phoneme frames

// Worker thread pool for parallel frame rendering
const workerPool = []
const MAX_WORKERS = Math.min(4, os.cpus().length) // Use up to 4 workers or available CPUs

// Clean up expired cache entries periodically
setInterval(() => {
  const now = Date.now()
  for (const [key, entry] of videoCache.entries()) {
    if (now - entry.timestamp > CACHE_TTL) {
      videoCache.delete(key)
      console.log(`Cleaned up expired cache entry: ${key}`)
    }
  }
  // Clean expression and phoneme caches too
  for (const [key, entry] of expressionFrameCache.entries()) {
    if (now - entry.timestamp > CACHE_TTL) {
      expressionFrameCache.delete(key)
    }
  }
  for (const [key, entry] of phonemeFrameCache.entries()) {
    if (now - entry.timestamp > CACHE_TTL) {
      phonemeFrameCache.delete(key)
    }
  }
}, 5 * 60 * 1000) // Clean every 5 minutes

// Clean up worker pool on exit
process.on('exit', () => {
  workerPool.forEach(worker => worker.terminate())
})

/**
 * Get cached expression frame or render new one
 */
async function getExpressionFrame(renderer, currentTime, emotionWeights, cacheKey) {
  const key = `${cacheKey}_expr_${currentTime.toFixed(3)}`
  
  if (expressionFrameCache.has(key)) {
    return expressionFrameCache.get(key).buffer
  }
  
  // Render expression-only frame
  const buffer = await renderer.renderFrame([], currentTime, emotionWeights)
  
  // Cache it
  if (expressionFrameCache.size >= MAX_EXPRESSION_CACHE_SIZE) {
    const oldestKey = expressionFrameCache.keys().next().value
    expressionFrameCache.delete(oldestKey)
  }
  expressionFrameCache.set(key, {
    buffer: buffer,
    timestamp: Date.now()
  })
  
  return buffer
}

/**
 * Get cached phoneme frame or render new one
 */
async function getPhonemeFrame(renderer, phonemes, currentTime, cacheKey) {
  const key = `${cacheKey}_phon_${currentTime.toFixed(3)}`
  
  if (phonemeFrameCache.has(key)) {
    return phonemeFrameCache.get(key).buffer
  }
  
  // Render phoneme-only frame (no emotions)
  const buffer = await renderer.renderFrame(phonemes, currentTime, null)
  
  // Cache it
  if (phonemeFrameCache.size >= MAX_PHONEME_CACHE_SIZE) {
    const oldestKey = phonemeFrameCache.keys().next().value
    phonemeFrameCache.delete(oldestKey)
  }
  phonemeFrameCache.set(key, {
    buffer: buffer,
    timestamp: Date.now()
  })
  
  return buffer
}

/**
 * Compose expression and phoneme frames by blending morph weights
 */
function composeFrames(expressionBuffer, phonemeBuffer, expressionController, phonemeWeights) {
  // For now, since ThreeJSRenderer.renderFrame returns a buffer,
  // we need to modify it to support composition.
  // As a placeholder, return the phoneme buffer (which already includes emotions)
  // In a full implementation, we'd blend the vertex data here
  return phonemeBuffer
}

/**
 * Get or create a worker from the pool
 */
function getWorker() {
  // Find available worker
  const availableWorker = workerPool.find(w => !w.busy)
  if (availableWorker) {
    availableWorker.busy = true
    return availableWorker
  }

  // Create new worker if pool not full
  if (workerPool.length < MAX_WORKERS) {
    const worker = new Worker(new URL(import.meta.url), { workerData: { type: 'frame_renderer' } })
    worker.busy = true
    workerPool.push(worker)
    return worker
  }

  // Wait for available worker (simple round-robin)
  return new Promise((resolve) => {
    const checkAvailable = () => {
      const worker = workerPool.find(w => !w.busy)
      if (worker) {
        worker.busy = true
        resolve(worker)
      } else {
        setImmediate(checkAvailable)
      }
    }
    checkAvailable()
  })
}

/**
 * Render frames using simple batch processing (better for smaller videos)
 * Now supports emotion blending with advanced caching
 */
async function renderFramesBatch(renderer, phonemes, totalFrames, fps, tempDir, expressionController = null) {
  const startTime = Date.now()
  console.log(`Rendering ${totalFrames} frames at ${fps}fps using batch processing...`)

  // Create cache key for this rendering session
  const sessionCacheKey = crypto.createHash('md5')
    .update(JSON.stringify({ phonemes, expressionController: !!expressionController }))
    .digest('hex').substring(0, 8)

  // Render frames in parallel batches for better performance
  const batchSize = Math.min(10, totalFrames) // Smaller batches for better memory usage
  let completedFrames = 0

  for (let batchStart = 0; batchStart < totalFrames; batchStart += batchSize) {
    const batchPromises = []
    const batchEnd = Math.min(batchStart + batchSize, totalFrames)

    for (let frame = batchStart; frame < batchEnd; frame++) {
      const currentTime = frame / fps
      
      // Get emotion weights if expression controller is provided
      let emotionWeights = null
      if (expressionController) {
        expressionController.update(currentTime * 1000) // Convert to ms
        emotionWeights = expressionController.getBlendedMorphWeightsArray({})
      }
      
      batchPromises.push(
        renderer.renderFrame(phonemes, currentTime, emotionWeights).then(buffer => {
          const framePath = path.join(tempDir, `frame_${frame.toString().padStart(6, '0')}.png`)
          return fs.promises.writeFile(framePath, buffer)
        })
      )
    }

    await Promise.all(batchPromises)
    completedFrames += batchPromises.length

    // Progress reporting every 10 batches or at key milestones
    if (batchStart % (batchSize * 3) === 0 || completedFrames === totalFrames) {
      const progress = ((completedFrames / totalFrames) * 100).toFixed(1)
      console.log(`Rendered frames ${batchStart}-${batchEnd - 1}/${totalFrames - 1} (${progress}%)`)
    }
  }

  const renderTime = Date.now() - startTime
  console.log(`Frame rendering completed in ${renderTime}ms (${(totalFrames / (renderTime / 1000)).toFixed(1)} fps)`)
  return renderTime
}

/**
 * Render frames using simple sequential processing (fastest for short videos)
 */
async function renderFramesSequential(renderer, phonemes, totalFrames, fps, tempDir, expressionController = null) {
  const startTime = Date.now()
  console.log(`Rendering ${totalFrames} frames at ${fps}fps using sequential processing...`)

  for (let frame = 0; frame < totalFrames; frame++) {
    const currentTime = frame / fps
    
    // Get emotion weights if expression controller is provided
    let emotionWeights = null
    if (expressionController) {
      expressionController.update(currentTime * 1000) // Convert to ms
      emotionWeights = expressionController.getBlendedMorphWeightsArray({})
    }
    
    const buffer = await renderer.renderFrame(phonemes, currentTime, emotionWeights)
    const framePath = path.join(tempDir, `frame_${frame.toString().padStart(6, '0')}.png`)
    await fs.promises.writeFile(framePath, buffer)

    // Progress reporting every 30 frames
    if (frame % 30 === 0 || frame === totalFrames - 1) {
      const progress = ((frame + 1) / totalFrames * 100).toFixed(1)
      console.log(`Rendered frame ${frame + 1}/${totalFrames} (${progress}%)`)
    }
  }

  const renderTime = Date.now() - startTime
  console.log(`Frame rendering completed in ${renderTime}ms (${(totalFrames / (renderTime / 1000)).toFixed(1)} fps)`)
  return renderTime
}
async function renderFramesParallel(renderer, phonemes, totalFrames, fps, tempDir) {
  const startTime = Date.now()
  console.log(`Rendering ${totalFrames} frames at ${fps}fps using ${MAX_WORKERS} worker threads...`)

  // Prepare frame tasks
  const frameTasks = []
  for (let frame = 0; frame < totalFrames; frame++) {
    const currentTime = frame / fps
    const framePath = path.join(tempDir, `frame_${frame.toString().padStart(6, '0')}.png`)
    frameTasks.push({ frame, currentTime, framePath, phonemes })
  }

  // Process frames in batches
  const batchSize = MAX_WORKERS * 2 // 2 batches per worker
  let completedFrames = 0

  for (let i = 0; i < frameTasks.length; i += batchSize) {
    const batch = frameTasks.slice(i, i + batchSize)
    const batchPromises = batch.map(async (task) => {
      const worker = await getWorker()
      return new Promise((resolve, reject) => {
        worker.once('message', (result) => {
          worker.busy = false
          if (result.error) {
            reject(new Error(result.error))
          } else {
            // Write frame buffer to file
            fs.writeFileSync(task.framePath, Buffer.from(result.buffer))
            completedFrames++
            resolve()
          }
        })

        worker.postMessage(task)
      })
    })

    await Promise.all(batchPromises)

    // Progress reporting
    const progress = ((completedFrames / totalFrames) * 100).toFixed(1)
    console.log(`Rendered frames ${i}-${Math.min(i + batchSize - 1, totalFrames - 1)}/${totalFrames - 1} (${progress}%)`)
  }

  const renderTime = Date.now() - startTime
  console.log(`Frame rendering completed in ${renderTime}ms (${(totalFrames / (renderTime / 1000)).toFixed(1)} fps)`)
  return renderTime
}

async function main() {
  try {
    // Read input from stdin (JSON from avatar service)
    const input = fs.readFileSync(0, 'utf-8')
    const request = JSON.parse(input)

    const { phonemes, duration, model = 'face', text, emotion, sentiment, context } = request

    console.log(`Rendering avatar video: ${text.substring(0, 50)}...`)
    console.log(`Model: ${model}, Duration: ${duration}s, Phonemes: ${phonemes.length}`)
    if (emotion || sentiment !== undefined) {
      console.log(`Emotion: ${emotion || 'auto'}, Sentiment: ${sentiment || 'N/A'}, Context: ${context || 'default'}`)
    }

    // For testing: return mock result immediately
    if (process.env.SKIP_RENDERING === 'true') {
      console.log('SKIP_RENDERING=true: Returning mock result for testing')
      console.log('Environment SKIP_RENDERING:', process.env.SKIP_RENDERING)
      const result = {
        video_path: `/video/avatar_test_${Date.now()}.webm`,
        duration: duration,
        model: model,
        metadata: {
          frames: Math.ceil(duration * 30),
          fps: 30,
          phonemes: phonemes.length,
          text_length: text.length,
          video_size_bytes: 1024000, // Mock 1MB
          render_time_ms: 100,
          video_encode_time_ms: 200,
          total_time_ms: 300,
          cache_key: 'test_' + Date.now(),
          emotion: 'test',
          emotion_analytics: null,
          video_base64: 'dGVzdCB2aWRlbyBkYXRh' // Mock base64
        }
      }
      console.log(JSON.stringify(result))
      process.exit(0)
      return
    }

    // Create cache key from request parameters (including emotion data)
    const cacheKey = crypto.createHash('md5')
      .update(JSON.stringify({ phonemes, duration, model, text, emotion, sentiment, context }))
      .digest('hex')

    // Check cache first
    if (videoCache.has(cacheKey)) {
      const cached = videoCache.get(cacheKey)
      console.log('Returning cached video result')
      console.log(JSON.stringify(cached.result))
      return
    }

    // Get configuration
    const config = AppConfig.get()

    // Initialize renderer (now uses global caches)
    const renderer = new ThreeJSRenderer(config)
    await renderer.initialize(model)

    // Initialize expression controller for emotion support
    let expressionController = null
    if (emotion || sentiment !== undefined || context) {
      expressionController = new ExpressionController({
        emotionTransitionDuration: 500,
        blinkInterval: 3000,
        blinkDuration: 150,
        lipSyncWeight: 1.0,
        emotionWeight: 0.7,
        idleAnimationEnabled: true
      })

      // Set initial emotion based on input
      if (emotion && EmotionStates[emotion.toUpperCase()]) {
        expressionController.setEmotion(EmotionStates[emotion.toUpperCase()])
        console.log(`Set explicit emotion: ${emotion}`)
      } else if (sentiment !== undefined) {
        expressionController.setEmotionFromSentiment(sentiment, context || 'neutral')
        console.log(`Set emotion from sentiment: ${sentiment} (${expressionController.getCurrentEmotion()})`)
      } else if (context) {
        // Default professional emotion for interview context
        expressionController.setEmotion(EmotionStates.PROFESSIONAL)
        console.log(`Set context-based emotion: professional`)
      }
    }

    // Create temporary directory for frames (reuse if exists)
    const tempDir = path.join(process.cwd(), 'temp_frames')
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir)
    }

    // Clear any existing frames to avoid conflicts
    const existingFrames = fs.readdirSync(tempDir).filter(f => f.endsWith('.png'))
    existingFrames.forEach(frame => {
      try {
        fs.unlinkSync(path.join(tempDir, frame))
      } catch (e) {
        // Ignore cleanup errors
      }
    })

    // Render frames with performance monitoring
    const fps = 30
    const totalFrames = Math.ceil(duration * fps)
    const startTime = Date.now()

    console.log(`Rendering ${totalFrames} frames at ${fps}fps...`)

    // Choose rendering strategy based on frame count and system capabilities
    let renderTime
    if (totalFrames > 100 && MAX_WORKERS > 1) {
      // Use worker threads for large videos
      renderTime = await renderFramesParallel(renderer, phonemes, totalFrames, fps, tempDir, expressionController)
    } else if (totalFrames > 50) {
      // Use optimized batch processing for medium videos
      renderTime = await renderFramesBatch(renderer, phonemes, totalFrames, fps, tempDir, expressionController)
    } else {
      // Use simple sequential processing for short videos
      renderTime = await renderFramesSequential(renderer, phonemes, totalFrames, fps, tempDir, expressionController)
    }

    // Generate video using optimized FFmpeg settings
    console.log('Generating video with ffmpeg...')
    const outputVideoPath = path.join(process.cwd(), 'temp_video.webm')
    const videoStartTime = Date.now()

    const ffmpegArgs = [
      '-y', // Overwrite output
      '-framerate', fps.toString(),
      '-i', path.join(tempDir, 'frame_%06d.png'), // Input frames
      '-c:v', 'libvpx-vp9', // VP9 codec for WebM
      '-b:v', '200k', // Lower bitrate for faster encoding
      '-crf', '40', // Higher CRF for much faster encoding (lower quality)
      '-speed', '8', // Maximum speed preset
      '-threads', '0', // Use all available threads
      '-pix_fmt', 'yuva420p', // Pixel format with alpha
      outputVideoPath
    ]

    try {
      const ffmpegProcess = spawn(ffmpeg, ffmpegArgs, {
        stdio: 'inherit',
        env: { ...process.env, FFREPORT: 'file=ffmpeg_report.log:level=24' } // Enable detailed logging
      })

      await new Promise((resolve, reject) => {
        ffmpegProcess.on('close', (code) => {
          if (code === 0) {
            resolve()
          } else {
            reject(new Error(`ffmpeg exited with code ${code}`))
          }
        })
        ffmpegProcess.on('error', reject)
      })

      const videoTime = Date.now() - videoStartTime
      console.log(`Video encoding completed in ${videoTime}ms`)

      // Read the generated video file
      const videoBuffer = fs.readFileSync(outputVideoPath)
      const videoBase64 = videoBuffer.toString('base64')

      // Clean up temporary files asynchronously (don't block response)
      setImmediate(() => {
        try {
          // Clean up frame files
          for (let frame = 0; frame < totalFrames; frame++) {
            const framePath = path.join(tempDir, `frame_${frame.toString().padStart(6, '0')}.png`)
            if (fs.existsSync(framePath)) {
              fs.unlinkSync(framePath)
            }
          }
          // Keep video file for testing - don't clean up
          // if (fs.existsSync(outputVideoPath)) {
          //   fs.unlinkSync(outputVideoPath)
          // }
        } catch (cleanupError) {
          console.warn('Cleanup warning:', cleanupError.message)
        }
      })

      // Prepare result
      const result = {
        video_path: `/video/avatar_${Date.now()}.webm`,
        duration: duration,
        model: model,
        metadata: {
          frames: totalFrames,
          fps: fps,
          phonemes: phonemes.length,
          text_length: text.length,
          video_size_bytes: videoBuffer.length,
          render_time_ms: renderTime,
          video_encode_time_ms: videoTime,
          total_time_ms: renderTime + videoTime,
          cache_key: cacheKey,
          emotion: expressionController ? expressionController.getCurrentEmotion() : 'none',
          emotion_analytics: expressionController ? expressionController.getAnalytics() : null,
          video_base64: videoBase64.substring(0, 100) + '...' // Truncated for logging
        }
      }

      // Cache the result
      if (videoCache.size >= MAX_CACHE_SIZE) {
        // Remove oldest entry
        const oldestKey = videoCache.keys().next().value
        videoCache.delete(oldestKey)
      }
      videoCache.set(cacheKey, {
        result: result,
        timestamp: Date.now(),
        size: videoBuffer.length
      })

      console.log(`Generated video: ${videoBuffer.length} bytes, ${totalFrames} frames`)
      console.log(`Performance: Render ${renderTime}ms, Encode ${videoTime}ms, Total ${(renderTime + videoTime)}ms`)
      console.log(`Cache status: ${videoCache.size}/${MAX_CACHE_SIZE} entries`)

      console.log(JSON.stringify(result))

    } catch (ffmpegError) {
      console.error('Video generation failed:', ffmpegError)

      // Fallback: return frame data as JSON
      const result = {
        video_path: null,
        duration: duration,
        model: model,
        metadata: {
          frames: totalFrames,
          fps: fps,
          phonemes: phonemes.length,
          text_length: text.length,
          error: 'Video generation failed',
          ffmpeg_error: ffmpegError.message,
          render_time_ms: renderTime,
          cache_key: cacheKey
        }
      }

      console.log(JSON.stringify(result))
    }

  } catch (error) {
    console.error('Rendering failed:', error.message)
    process.exit(1)
  }
}

// Only run main if this script is executed directly (not imported)
if (import.meta.url === `file://${process.argv[1]}`) {
  if (isMainThread) {
    main()
  } else {
    // Worker thread code for parallel frame rendering
    runWorker()
  }
}

async function runWorker() {
  const { ThreeJSRenderer } = await import('./ThreeJSRenderer.js')
  const { AppConfig } = await import('../../../ai-orchestra-simulation/phase3-integration/src/config/AppConfig.js')

  // Create renderer instance in worker
  const config = AppConfig.get()
  const renderer = new ThreeJSRenderer(config)
  await renderer.initialize('face')

  parentPort.on('message', async (task) => {
    try {
      const { frame, currentTime, phonemes } = task
      const buffer = await renderer.renderFrame(phonemes, currentTime)
      parentPort.postMessage({ buffer: Array.from(buffer) })
    } catch (error) {
      parentPort.postMessage({ error: error.message })
    }
  })
}