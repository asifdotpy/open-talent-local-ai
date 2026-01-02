#!/usr/bin/env node

/**
 * server.js - HTTP server for avatar rendering service
 * Provides REST API for lip-sync video generation
 */

import { spawn } from 'child_process'
import express from 'express'
import fs from 'fs'
import multer from 'multer'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
const PORT = process.env.PORT || 3001

// Configure multer for file uploads
const upload = multer({ dest: '/tmp/' })

// Middleware
app.use(express.json({ limit: '50mb' }))
app.use(express.urlencoded({ extended: true, limit: '50mb' }))

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'avatar-renderer',
    version: '1.0.0',
    capabilities: ['lip-sync', 'emotion-blending', 'three-js-rendering']
  })
})

// Lip-sync rendering endpoint
app.post('/render/lipsync', async (req, res) => {
  try {
    const { phonemes, audioUrl, model = 'face', duration } = req.body

    if (!phonemes || !Array.isArray(phonemes)) {
      return res.status(400).json({ error: 'Phonemes array is required' })
    }

    if (!audioUrl) {
      return res.status(400).json({ error: 'Audio URL is required' })
    }

    console.log(`Rendering avatar video: ${phonemes.length} phonemes, model: ${model}, duration: ${duration}`)

    // Prepare JSON input for render.js (matches expected stdin format)
    const renderInput = {
      phonemes: phonemes,
      duration: parseFloat(duration) || 5.0,
      model: model,
      text: '', // Not used in current render.js
      emotion: null,
      sentiment: null,
      context: null
    }

    // Spawn render.js process
    const renderProcess = spawn('node', ['render.js'], {
      cwd: __dirname,
      stdio: ['pipe', 'pipe', 'pipe']
    })

    let stdout = ''
    let stderr = ''

    renderProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    renderProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    // Send JSON input to stdin
    renderProcess.stdin.write(JSON.stringify(renderInput))
    renderProcess.stdin.end()

    // Wait for process to complete
    const exitCode = await new Promise((resolve) => {
      renderProcess.on('close', resolve)
    })

    if (exitCode !== 0) {
      console.error(`Render process failed: ${stderr}`)
      return res.status(500).json({
        error: 'Rendering failed',
        details: stderr,
        stdout: stdout
      })
    }

    // Parse JSON output from render.js
    let result
    try {
      // Find the last JSON line in stdout
      const lines = stdout.trim().split('\n')
      const jsonLine = lines[lines.length - 1]
      result = JSON.parse(jsonLine)
    } catch (parseError) {
      console.error(`Failed to parse render output: ${parseError.message}`)
      return res.status(500).json({
        error: 'Invalid render output',
        stdout: stdout,
        stderr: stderr
      })
    }

    if (!result.metadata || result.error) {
      console.error(`Render failed: ${result.error || 'Unknown error'}`)
      return res.status(500).json({
        error: 'Rendering failed',
        details: result
      })
    }

    // For now, since render.js saves to temp_video.webm, read that file
    // TODO: Modify render.js to output video data directly
    const videoPath = path.join(__dirname, 'temp_video.webm')

    if (!fs.existsSync(videoPath)) {
      console.error(`Video file not found: ${videoPath}`)
      return res.status(500).json({
        error: 'Video file not generated',
        result: result
      })
    }

    // Read video file
    const videoBuffer = fs.readFileSync(videoPath)

    // Set response headers
    res.setHeader('Content-Type', 'video/webm')
    res.setHeader('Content-Length', videoBuffer.length)
    res.setHeader('X-Processing-Time', result.metadata.total_time_ms || 'unknown')
    res.setHeader('X-Video-Duration', result.duration || duration)

    // Send video data
    res.send(videoBuffer)

    // Cleanup video file
    try {
      fs.unlinkSync(videoPath)
    } catch (cleanupError) {
      console.warn(`Failed to cleanup video file: ${cleanupError.message}`)
    }

  } catch (error) {
    console.error('Server error:', error)
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    })
  }
})

// Start server
app.listen(PORT, () => {
  console.log(`Avatar renderer server listening on port ${PORT}`)
  console.log(`Health check: http://localhost:${PORT}/health`)
  console.log(`Render endpoint: POST http://localhost:${PORT}/render/lipsync`)
})
