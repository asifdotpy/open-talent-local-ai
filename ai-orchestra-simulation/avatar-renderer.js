/**
 * Avatar Rendering Server - Phase 2 MVP
 *
 * Simple server-side avatar video generation with phoneme-based lip-sync
 * Uses Canvas API for basic animation - full 3D integration in Phase 3
 */

import { createCanvas } from 'canvas';
import { spawn } from 'child_process';
import cors from 'cors';
import crypto from 'crypto';
import express from 'express';
import ffmpeg from 'ffmpeg-static';
import fs from 'fs';
import http from 'http';
import path from 'path';
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { fileURLToPath } from 'url';
import { WebSocketServer } from 'ws';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Main application class for backward compatibility
 * Wraps the new modular AvatarServer
 */
class AvatarRendererServer {
  constructor(port = 3001) {
    // Load configuration
    const configManager = getConfig();
    const config = configManager.getAll();

    // Override port if specified
    if (port !== 3001) {
      config.server.port = port;
    }

    // Initialize logger
    this.logger = new StructuredLogger(config.logging);

    // Initialize server with configuration
    this.server = new AvatarServer({
      ...config.server,
      ...config.renderer,
      ...config.session,
      logger: this.logger,
      rendererType: config.renderer.type,
      maxSessions: config.session.maxSessions
    });

    this.port = config.server.port;
    this.logger.info('AvatarRendererServer initialized', {
      port: this.port,
      renderer: config.renderer.type,
      environment: configManager.getEnvironment()
    });
  }

  /**
   * Start the server
   */
  async start() {
    try {
      await this.server.start();
      this.logger.info('Server started successfully', {
        port: this.port,
        endpoints: {
          health: `http://localhost:${this.port}/health`,
          docs: `http://localhost:${this.port}/docs`,
          websocket: `ws://localhost:${this.port}`
        }
      });
    } catch (error) {
      this.logger.error('Failed to start server', error);
      throw error;
    }
  }

  /**
   * Stop the server gracefully
   */
  async stop() {
    try {
      await this.server.stop();
      this.logger.info('Server stopped successfully');
    } catch (error) {
      this.logger.error('Error stopping server', error);
      throw error;
    }
  }
}

// Legacy OpenAPI specification (kept for reference, now in AvatarServer)
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'AI Orchestra Simulation - Avatar Renderer API',
      version: '1.0.0',
      description: `
      Real-time avatar rendering and lip-sync animation service for TalentAI Platform.

      **Capabilities:**
      - Real-time lip-sync animation with phoneme-based mouth movement
      - WebSocket streaming for live avatar interactions
      - Canvas-based 1920x1080@30fps video generation
      - FFmpeg-powered video encoding and processing

      **API Documentation:**
      - Interactive Swagger UI: \`/docs\`
      - Alternative docs URL: \`/doc\`
      - ReDoc documentation: \`/redoc\`
      - OpenAPI schema: \`/openapi.json\`
      - API endpoints summary: \`/api-docs\`

      **WebSocket Streaming:**
      - Real-time avatar animation: \`ws://localhost:3001\`
      - Phoneme data streaming for lip-sync
      - Frame-by-frame rendering updates
      `,
      contact: {
        name: 'AI Orchestra Team'
      }
    },
    servers: [
      {
        url: 'http://localhost:3001',
        description: 'Local development server'
      }
    ],
    components: {
      schemas: {
        Phoneme: {
          type: 'object',
          properties: {
            phoneme: {
              type: 'string',
              description: 'Phoneme symbol (e.g., "AA", "EH", "M")',
              example: 'AA'
            },
            start: {
              type: 'number',
              description: 'Start time in seconds',
              example: 0.0
            },
            end: {
              type: 'number',
              description: 'End time in seconds',
              example: 0.2
            }
          },
          required: ['phoneme', 'start', 'end']
        },
        LipSyncRequest: {
          type: 'object',
          properties: {
            phonemes: {
              type: 'array',
              items: { $ref: '#/components/schemas/Phoneme' },
              description: 'Array of phoneme timing data'
            },
            audioUrl: {
              type: 'string',
              description: 'URL to audio file for synchronization',
              example: 'file:///tmp/audio.wav'
            },
            model: {
              type: 'string',
              description: 'Avatar model preset',
              enum: ['face', 'metahuman', 'conductor'],
              default: 'face'
            },
            duration: {
              type: 'number',
              description: 'Expected duration in seconds',
              example: 3.5
            }
          },
          required: ['phonemes']
        },
        HealthResponse: {
          type: 'object',
          properties: {
            status: {
              type: 'string',
              example: 'ok'
            },
            timestamp: {
              type: 'string',
              format: 'date-time',
              example: '2025-11-12T17:35:49.211Z'
            }
          }
        },
        VideoResponse: {
          type: 'object',
          properties: {
            video_path: {
              type: 'string',
              description: 'Path to generated video file'
            },
            duration: {
              type: 'number',
              description: 'Video duration in seconds'
            },
            model_used: {
              type: 'string',
              description: 'Avatar model used for rendering'
            },
            metadata: {
              type: 'object',
              description: 'Additional rendering metadata'
            }
          }
        },
        ApiDocsResponse: {
          type: 'object',
          properties: {
            service: {
              type: 'string',
              example: 'AI Orchestra Simulation - Avatar Renderer API'
            },
            version: {
              type: 'string',
              example: '1.0.0'
            },
            total_endpoints: {
              type: 'integer',
              example: 5
            },
            documentation_urls: {
              type: 'object',
              properties: {
                swagger_ui: { type: 'string', example: '/docs' },
                redoc: { type: 'string', example: '/redoc' },
                openapi_json: { type: 'string', example: '/openapi.json' }
              }
            },
            routes: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  path: { type: 'string', example: '/health' },
                  methods: { type: 'array', items: { type: 'string' }, example: ['GET'] },
                  name: { type: 'string', example: 'health_check' },
                  summary: { type: 'string', example: 'Health check endpoint' }
                }
              }
            },
            websocket_info: {
              type: 'object',
              properties: {
                url: { type: 'string', example: 'ws://localhost:3001' },
                purpose: { type: 'string', example: 'Real-time avatar streaming' },
                message_types: {
                  type: 'array',
                  items: { type: 'string' },
                  example: ['start_stream', 'phoneme_data', 'stop_stream']
                }
              }
            }
          }
        }
      }
    }
  },
  apis: [] // Will be populated with route documentation
};

const specs = swaggerJsdoc(swaggerOptions);

// Legacy class implementation removed - now using modular AvatarServer
// The old implementation has been refactored into:
// - src/server/AvatarServer.js - Main server logic
// - src/server/SessionManager.js - WebSocket session management
// - src/renderer/CanvasRenderer.js - 2D rendering
// - src/renderer/ThreeJSRenderer.js - 3D rendering
// - src/video/VideoEncoder.js - FFmpeg video encoding
// - src/config/ConfigManager.js - Configuration management
// - src/utils/StructuredLogger.js - Production logging

// The following methods are preserved for backward compatibility
// but now delegate to the modular components

/*
LEGACY CODE - PRESERVED FOR REFERENCE

Old implementation used a monolithic class with all functionality:
- Express server setup
- WebSocket management
- Canvas rendering
- Video encoding
- Session tracking

New implementation uses composition:
class AvatarRendererServer {
  constructor(port = 3001) {
    this.port = port;
    this.app = express();
    this.logger = console;
    this.tempDir = path.join(__dirname, 'temp');

    // HTTP server (WebSocket server will be attached later)
    this.server = http.createServer(this.app);

    // Active streaming sessions
    this.streamingSessions = new Map();

    // Ensure temp directory exists
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }

    this.setupMiddleware();
    this.setupRoutes();
    // WebSocket setup moved to start() method
  }

  setupMiddleware() {
    // Enable CORS for all routes
    this.app.use(cors());

    // Parse JSON bodies
    this.app.use(express.json({ limit: '50mb' }));

    // Parse URL-encoded bodies
    this.app.use(express.urlencoded({ extended: true }));

    // Add request logging
    this.app.use((req, res, next) => {
      this.logger.log(`${req.method} ${req.url}`);
      next();
    });
  }

  setupWebSocket() {
    this.wss.on('connection', (ws, req) => {
      const sessionId = crypto.randomBytes(8).toString('hex');
      this.logger.log(`WebSocket connection established: ${sessionId}`);

      // Create streaming session
      const session = {
        id: sessionId,
        ws: ws,
        isActive: false,
        currentPhonemes: [],
        startTime: null,
        canvas: null,
        animationFrame: null
      };

      this.streamingSessions.set(sessionId, session);

      // Handle incoming messages
      ws.on('message', (message) => {
        try {
          const data = JSON.parse(message.toString());
          this.handleWebSocketMessage(session, data);
        } catch (error) {
          this.logger.error(`WebSocket message error for ${sessionId}:`, error);
          ws.send(JSON.stringify({ type: 'error', message: 'Invalid message format' }));
        }
      });

      ws.on('close', () => {
        this.logger.log(`WebSocket connection closed: ${sessionId}`);
        this.stopStreamingSession(sessionId);
      });

      ws.on('error', (error) => {
        this.logger.error(`WebSocket error for ${sessionId}:`, error);
        this.stopStreamingSession(sessionId);
      });

      // Send welcome message
      ws.send(JSON.stringify({
        type: 'connected',
        sessionId: sessionId,
        message: 'Avatar streaming session established'
      }));
    });
  }

  handleWebSocketMessage(session, data) {
    switch (data.type) {
      case 'start_stream':
        this.startStreamingSession(session, data);
        break;
      case 'phoneme_data':
        this.handlePhonemeData(session, data);
        break;
      case 'stop_stream':
        this.stopStreamingSession(session.id);
        break;
      default:
        session.ws.send(JSON.stringify({
          type: 'error',
          message: `Unknown message type: ${data.type}`
        }));
    }
  }

  startStreamingSession(session, data) {
    const { width = 1920, height = 1080, fps = 30 } = data;

    session.canvas = createCanvas(width, height);
    session.ctx = session.canvas.getContext('2d');
    session.width = width;
    session.height = height;
    session.fps = fps;
    session.isActive = true;
    session.startTime = Date.now();
    session.currentPhonemes = [];
    session.lastFrameTime = 0;

    this.logger.log(`Started streaming session ${session.id} (${width}x${height}@${fps}fps)`);

    // Start animation loop
    this.startAnimationLoop(session);

    session.ws.send(JSON.stringify({
      type: 'stream_started',
      sessionId: session.id,
      width,
      height,
      fps
    }));
  }

  startAnimationLoop(session) {
    const animate = () => {
      if (!session.isActive) return;

      const currentTime = (Date.now() - session.startTime) / 1000; // Convert to seconds
      const mouthOpen = this.getMouthOpenAtTime(session.currentPhonemes, currentTime);

      // Clear canvas
      session.ctx.fillStyle = '#1a1a2e';
      session.ctx.fillRect(0, 0, session.width, session.height);

      // Draw avatar face
      this.drawAvatarFace(session.ctx, session.width, session.height, mouthOpen);

      // Convert canvas to base64 and send to client
      const frameData = session.canvas.toDataURL('image/jpeg', 0.8);

      if (session.ws.readyState === WebSocket.OPEN) {
        session.ws.send(JSON.stringify({
          type: 'frame',
          sessionId: session.id,
          timestamp: currentTime,
          frameData: frameData
        }));
      }

      // Schedule next frame
      session.animationFrame = setTimeout(animate, 1000 / session.fps);
    };

    animate();
  }

  handlePhonemeData(session, data) {
    const { phonemes, audioTimestamp } = data;

    if (phonemes && Array.isArray(phonemes)) {
      // Update phoneme data for real-time animation
      session.currentPhonemes = phonemes;

      // Adjust timing if audio timestamp provided
      if (audioTimestamp !== undefined) {
        session.startTime = Date.now() - (audioTimestamp * 1000);
      }

      this.logger.log(`Updated phonemes for session ${session.id}: ${phonemes.length} phonemes`);
    }
  }

  stopStreamingSession(sessionId) {
    const session = this.streamingSessions.get(sessionId);
    if (session) {
      session.isActive = false;
      if (session.animationFrame) {
        clearTimeout(session.animationFrame);
      }
      if (session.ws.readyState === WebSocket.OPEN) {
        session.ws.close();
      }
      this.streamingSessions.delete(sessionId);
      this.logger.log(`Stopped streaming session ${sessionId}`);
    }
  }

  setupRoutes() {
    // OpenAPI Documentation routes
    this.app.use('/docs', swaggerUi.serve, swaggerUi.setup(specs));

    // Alternative docs redirect
    this.app.get('/doc', (req, res) => {
      res.redirect('/docs');
    });

    // ReDoc documentation
    this.app.get('/redoc', (req, res) => {
      res.send(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>AI Orchestra Simulation - Avatar Renderer API</title>
          <meta charset="utf-8"/>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
          <style>
            body { margin: 0; padding: 0; }
          </style>
        </head>
        <body>
          <redoc spec-url='/openapi.json'></redoc>
          <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
        </body>
        </html>
      `);
    });

    // OpenAPI JSON schema
    this.app.get('/openapi.json', (req, res) => {
      res.setHeader('Content-Type', 'application/json');
      res.send(specs);
    });

    // API documentation summary
    this.app.get('/api-docs', (req, res) => {
      // Scan routes to build documentation
      const routes = [];
      this.app._router.stack.forEach((middleware) => {
        if (middleware.route) {
          const route = middleware.route;
          routes.push({
            path: route.path,
            methods: Object.keys(route.methods).filter(method => route.methods[method]),
            name: route.path.replace(/\//g, '_').substring(1) || 'root',
            summary: this.getRouteSummary(route.path)
          });
        }
      });

      res.json({
        service: 'AI Orchestra Simulation - Avatar Renderer API',
        version: '1.0.0',
        total_endpoints: routes.length,
        documentation_urls: {
          swagger_ui: '/docs',
          redoc: '/redoc',
          openapi_json: '/openapi.json'
        },
        routes: routes,
        websocket_info: {
          url: 'ws://localhost:3001',
          purpose: 'Real-time avatar streaming',
          message_types: ['start_stream', 'phoneme_data', 'stop_stream', 'frame', 'connected', 'stream_started', 'error']
        },
        capabilities: {
          rendering: 'Canvas-based 1920x1080@30fps',
          lip_sync: 'Phoneme-to-morph-target mapping',
          streaming: 'WebSocket real-time animation',
          video_generation: 'FFmpeg WebM encoding'
        }
      });
    });

    // API routes with OpenAPI annotations
    /**
     * @swagger
     * /:
     *   get:
     *     summary: Root endpoint
     *     description: Get service information and available endpoints
     *     responses:
     *       200:
     *         description: Service information
     *         content:
     *           application/json:
     *             schema:
     *               type: object
     *               properties:
     *                 service:
     *                   type: string
     *                   example: AI Orchestra Simulation - Avatar Renderer
     *                 version:
     *                   type: string
     *                   example: 1.0.0
     *                 status:
     *                   type: string
     *                   example: running
     *                 capabilities:
     *                   type: object
     *                 documentation:
     *                   type: object
     */
    this.app.get('/', (req, res) => {
      res.json({
        service: 'AI Orchestra Simulation - Avatar Renderer',
        version: '1.0.0',
        status: 'running',
        capabilities: {
          rendering: 'Canvas-based avatar animation',
          lip_sync: 'Phoneme-based mouth movement',
          streaming: 'WebSocket real-time updates',
          video_generation: 'FFmpeg-powered encoding'
        },
        documentation: {
          swagger_ui: '/docs',
          alternative: '/doc',
          redoc: '/redoc',
          openapi_json: '/openapi.json',
          api_summary: '/api-docs'
        },
        websocket: {
          url: 'ws://localhost:3001',
          purpose: 'Real-time avatar streaming'
        }
      });
    });

    /**
     * @swagger
     * /health:
     *   get:
     *     summary: Health check
     *     description: Check if the avatar renderer service is healthy
     *     responses:
     *       200:
     *         description: Service is healthy
     *         content:
     *           application/json:
     *             schema:
     *               $ref: '#/components/schemas/HealthResponse'
     */
    this.app.get('/health', (req, res) => {
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    /**
     * @swagger
     * /render/lipsync:
     *   post:
     *     summary: Render lip-sync video
     *     description: Generate avatar video with lip-sync animation from phoneme data
     *     requestBody:
     *       required: true
     *       content:
     *         application/json:
     *           schema:
     *             $ref: '#/components/schemas/LipSyncRequest'
     *     responses:
     *       200:
     *         description: Video generated successfully
     *         content:
     *           video/webm:
     *             schema:
     *               type: string
     *               format: binary
     *         headers:
     *           X-Processing-Time:
     *             description: Time taken to process the request
     *             schema:
     *               type: string
     *               example: "1500ms"
     *       400:
     *         description: Invalid request data
     *       500:
     *         description: Rendering failed
     */
    this.app.post('/render/lipsync', this.handleLipSyncRender.bind(this));
  }

  getRouteSummary(path) {
    const summaries = {
      '/': 'Root endpoint with service information',
      '/health': 'Health check endpoint',
      '/docs': 'Interactive API documentation (Swagger UI)',
      '/doc': 'Redirect to API documentation',
      '/redoc': 'ReDoc API documentation',
      '/openapi.json': 'OpenAPI 3.0 specification',
      '/api-docs': 'API endpoints summary and metadata',
      '/render/lipsync': 'Generate lip-sync video from phoneme data'
    };
    return summaries[path] || 'API endpoint';
  }

  async handleLipSyncRender(req, res) {
    const startTime = Date.now();
    const requestId = crypto.randomBytes(4).toString('hex');

    try {
      const { phonemes, audioUrl, model = 'face', duration } = req.body;

      this.logger.log(`[${requestId}] Starting lip-sync render`, {
        phonemesCount: phonemes?.length,
        audioUrl,
        model,
        duration
      });

      if (!phonemes || !Array.isArray(phonemes)) {
        return res.status(400).json({ error: 'phonemes array required' });
      }

      // Generate animated video with phoneme-based mouth animation
      const videoBuffer = await this.generateAnimatedVideo(phonemes, duration, requestId);

      const processingTime = Date.now() - startTime;
      this.logger.log(`[${requestId}] Render completed`, {
        duration: duration || this.calculateDuration(phonemes),
        processingTime: `${processingTime}ms`,
        videoSize: `${videoBuffer.length} bytes`
      });

      res.setHeader('Content-Type', 'video/webm');
      res.setHeader('Content-Length', videoBuffer.length);
      res.setHeader('X-Processing-Time', `${processingTime}ms`);
      res.send(videoBuffer);

    } catch (error) {
      const processingTime = Date.now() - startTime;
      this.logger.error(`[${requestId}] Render failed after ${processingTime}ms`, error);

      res.status(500).json({
        error: 'Render failed',
        message: error.message,
        requestId,
        processingTime: `${processingTime}ms`
      });
    }
  }

  async generateAnimatedVideo(phonemes, duration, requestId) {
    const fps = 30;
    const totalDuration = duration || this.calculateDuration(phonemes);
    const totalFrames = Math.ceil(totalDuration * fps);
    const width = 1920;
    const height = 1080;

    // Create temp directory for frames
    const frameDir = path.join(this.tempDir, `frames_${requestId}`);
    if (!fs.existsSync(frameDir)) {
      fs.mkdirSync(frameDir, { recursive: true });
    }

    try {
      // Generate frames
      for (let frame = 0; frame < totalFrames; frame++) {
        const time = frame / fps;
        const mouthOpen = this.getMouthOpenAtTime(phonemes, time);

        const canvas = createCanvas(width, height);
        const ctx = canvas.getContext('2d');

        // Draw background
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, width, height);

        // Draw avatar face
        this.drawAvatarFace(ctx, width, height, mouthOpen);

        // Save frame
        const framePath = path.join(frameDir, `frame_${frame.toString().padStart(6, '0')}.png`);
        const buffer = canvas.toBuffer('image/png');
        fs.writeFileSync(framePath, buffer);
      }

      // Create video using ffmpeg
      const videoPath = path.join(this.tempDir, `video_${requestId}.webm`);
      await this.createVideoFromFrames(frameDir, videoPath, fps);

      // Read video file
      const videoBuffer = fs.readFileSync(videoPath);

      // Cleanup temp files
      this.cleanupTempFiles(frameDir, videoPath);

      return videoBuffer;

    } catch (error) {
      // Cleanup on error
      this.cleanupTempFiles(frameDir);
      throw error;
    }
  }

  getMouthOpenAtTime(phonemes, time) {
    // Find current phoneme
    for (const phoneme of phonemes) {
      if (time >= phoneme.start && time <= phoneme.end) {
        // Map phoneme to mouth openness (0-1)
        const phonemeMap = {
          'AA': 1.0, 'AO': 0.9, 'A': 0.8, 'AE': 0.7, 'AH': 0.6,
          'E': 0.5, 'EH': 0.6, 'O': 0.7, 'OW': 0.6, 'U': 0.5,
          'UW': 0.4, 'I': 0.4, 'IY': 0.3, 'M': 0.1, 'P': 0.1,
          'B': 0.2, 'TH': 0.2, 'F': 0.2, 'V': 0.2, 'S': 0.1,
          'Z': 0.1, 'SH': 0.2, 'CH': 0.2, 'L': 0.3, 'R': 0.3
        };
        return phonemeMap[phoneme.phoneme] || 0.0;
      }
    }
    return 0.0; // Mouth closed
  }

  drawAvatarFace(ctx, width, height, mouthOpen) {
    const centerX = width / 2;
    const centerY = height / 2;

    // Draw head
    ctx.fillStyle = '#fdbcb4';
    ctx.beginPath();
    ctx.arc(centerX, centerY, 200, 0, Math.PI * 2);
    ctx.fill();

    // Draw eyes
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.arc(centerX - 60, centerY - 50, 15, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(centerX + 60, centerY - 50, 15, 0, Math.PI * 2);
    ctx.fill();

    // Draw mouth based on phoneme
    ctx.fillStyle = '#000';
    const mouthWidth = 80;
    const mouthHeight = 20 + (mouthOpen * 40); // 20-60 pixels
    ctx.beginPath();
    ctx.ellipse(centerX, centerY + 50, mouthWidth / 2, mouthHeight / 2, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  createVideoFromFrames(frameDir, outputPath, fps) {
    return new Promise((resolve, reject) => {
      const ffmpegProcess = spawn(ffmpeg, [
        '-framerate', fps.toString(),
        '-i', path.join(frameDir, 'frame_%06d.png'),
        '-c:v', 'libvpx-vp9',
        '-b:v', '1M',
        '-auto-alt-ref', '0',
        '-y', // Overwrite output
        outputPath
      ]);

      let stderr = '';
      ffmpegProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      ffmpegProcess.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`FFmpeg failed: ${stderr}`));
        }
      });

      ffmpegProcess.on('error', reject);
    });
  }

  cleanupTempFiles(...paths) {
    for (const filePath of paths) {
      try {
        if (fs.existsSync(filePath)) {
          if (fs.statSync(filePath).isDirectory()) {
            fs.rmSync(filePath, { recursive: true, force: true });
          } else {
            fs.unlinkSync(filePath);
          }
        }
      } catch (error) {
        this.logger.warn(`Failed to cleanup ${filePath}:`, error.message);
      }
    }
  }

  calculateDuration(phonemes) {
    if (!phonemes || phonemes.length === 0) return 0;
    const lastPhoneme = phonemes[phonemes.length - 1];
    return lastPhoneme.end || 0;
  }

  start() {
    this.server.listen(this.port, () => {
      this.logger.log(`Avatar Renderer Server started on port ${this.port}`);
      this.logger.log(`Health check: http://localhost:${this.port}/health`);
      this.logger.log(`Render endpoint: POST http://localhost:${this.port}/render/lipsync`);

      // Initialize WebSocket server after HTTP server is listening
      this.wss = new WebSocketServer({ server: this.server });
      this.setupWebSocket();

      this.logger.log(`WebSocket streaming: ws://localhost:${this.port}`);
    });
  }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const server = new AvatarRendererServer();
  server.start();
}

export default AvatarRendererServer;