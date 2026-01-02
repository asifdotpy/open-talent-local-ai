/**
 * AvatarServer - Express + WebSocket server for avatar rendering
 *
 * Provides HTTP API and WebSocket streaming for real-time avatar animation.
 * Modular architecture with pluggable renderers and session management.
 */

import cors from 'cors';
import crypto from 'crypto';
import express from 'express';
import http from 'http';
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { WebSocketServer } from 'ws';

import { CanvasRenderer } from '../renderer/CanvasRenderer.js';
import { R3FRenderer } from '../renderer/R3FRenderer.js';
import { VideoEncoder } from '../video/VideoEncoder.js';
import { SessionManager } from './SessionManager.js';

export class AvatarServer {
  constructor(config = {}) {
    this.config = {
      port: config.port || 3001,
      host: config.host || 'localhost',
      rendererType: config.rendererType || 'canvas', // 'canvas' or 'threejs'
      corsOrigins: config.corsOrigins || '*',
      requestLimit: config.requestLimit || '50mb',
      ...config
    };

    this.logger = config.logger || console;
    this.app = express();
    this.server = http.createServer(this.app);
    this.wss = null;
    this.sessionManager = null;
    this.renderer = null;
    this.videoEncoder = null;

    // Request tracking
    this.requestCount = 0;
    this.startTime = Date.now();
  }

  /**
   * Initialize server components
   */
  async initialize() {
    try {
      // Initialize session manager
      this.sessionManager = new SessionManager({
        logger: this.logger,
        maxSessions: this.config.maxSessions
      });

      // Initialize renderer based on config
      await this.initializeRenderer();

      // Initialize video encoder
      this.videoEncoder = new VideoEncoder({
        logger: this.logger
      });

      // Setup Express middleware
      this.setupMiddleware();

      // Setup routes
      this.setupRoutes();

      // Setup WebSocket server
      this.setupWebSocket();

      this.logger.log('AvatarServer initialized', {
        port: this.config.port,
        renderer: this.config.rendererType
      });

      return true;
    } catch (error) {
      this.logger.error('Failed to initialize AvatarServer:', error);
      return false;
    }
  }

  async initializeRenderer() {
    switch (this.config.rendererType) {
      case 'canvas':
        this.renderer = new CanvasRenderer({
          logger: this.logger,
          width: 1920,
          height: 1080,
          fps: 30
        });
        break;

      case 'r3f':
        this.renderer = new R3FRenderer({
          logger: this.logger,
          width: 1920,
          height: 1080,
          fps: 30,
          websocketPort: 3002,
          websocketHost: 'localhost',
          maxConnections: 50
        });
        break;

      case 'threejs':
        // Three.js renderer not implemented yet
        throw new Error('Three.js renderer not implemented');

      default:
        throw new Error(`Unsupported renderer type: ${this.config.rendererType}`);
    }

    const success = await this.renderer.initialize();
    if (!success) {
      throw new Error('Failed to initialize renderer');
    }

    this.logger.log('Renderer initialized', this.renderer.getCapabilities());
  }

  setupMiddleware() {
    // CORS
    this.app.use(cors({ origin: this.config.corsOrigins }));

    // JSON body parser
    this.app.use(express.json({ limit: this.config.requestLimit }));
    this.app.use(express.urlencoded({ extended: true, limit: this.config.requestLimit }));

    // Request logging
    this.app.use((req, res, next) => {
      const requestId = crypto.randomBytes(4).toString('hex');
      req.requestId = requestId;
      req.startTime = Date.now();

      this.logger.log(`[${requestId}] ${req.method} ${req.url}`);

      res.on('finish', () => {
        const duration = Date.now() - req.startTime;
        this.logger.log(`[${requestId}] ${res.statusCode} - ${duration}ms`);
      });

      this.requestCount++;
      next();
    });
  }

  setupRoutes() {
    // OpenAPI documentation
    const swaggerOptions = {
      definition: {
        openapi: '3.0.0',
        info: {
          title: 'Avatar Renderer API',
          version: '2.0.0',
          description: 'Production avatar rendering service with modular architecture'
        },
        servers: [
          { url: `http://${this.config.host}:${this.config.port}` }
        ]
      },
      apis: []
    };

    const specs = swaggerJsdoc(swaggerOptions);
    this.app.use('/docs', swaggerUi.serve, swaggerUi.setup(specs));

    // API routes
    this.app.get('/', this.handleRoot.bind(this));
    this.app.get('/health', this.handleHealth.bind(this));
    this.app.get('/metrics', this.handleMetrics.bind(this));
    this.app.get('/status', this.handleStatus.bind(this));
    this.app.get('/api-docs', this.handleApiDocs.bind(this));
    this.app.post('/render/lipsync', this.handleLipSyncRender.bind(this));

    // Error handling middleware
    this.app.use(this.errorHandler.bind(this));
  }

  setupWebSocket() {
    this.wss = new WebSocketServer({ server: this.server });

    this.wss.on('connection', (ws, req) => {
      const session = this.sessionManager.createSession(ws, {
        ip: req.socket.remoteAddress,
        userAgent: req.headers['user-agent']
      });

      if (!session) {
        ws.close(1008, 'Max sessions reached');
        return;
      }

      // Send welcome message
      ws.send(JSON.stringify({
        type: 'connected',
        sessionId: session.id,
        message: 'Avatar streaming session established',
        capabilities: this.renderer.getCapabilities()
      }));

      // Handle messages
      ws.on('message', (message) => {
        this.handleWebSocketMessage(session, message);
      });

      ws.on('close', () => {
        this.sessionManager.closeSession(session.id, 'client_disconnect');
      });

      ws.on('error', (error) => {
        this.logger.error('WebSocket error', { sessionId: session.id, error });
        this.sessionManager.closeSession(session.id, 'error');
      });
    });

    this.sessionManager.start();
  }

  handleWebSocketMessage(session, message) {
    try {
      const data = JSON.parse(message.toString());
      this.sessionManager.touchSession(session.id);
      session.stats.messagesReceived++;

      switch (data.type) {
        case 'start_stream':
          this.sessionManager.startStreaming(session.id, data.config);
          break;
        case 'stop_stream':
          this.sessionManager.stopStreaming(session.id);
          break;
        case 'pause_stream':
          this.sessionManager.pauseStreaming(session.id);
          break;
        case 'resume_stream':
          this.sessionManager.resumeStreaming(session.id);
          break;
        case 'phoneme_data':
          this.handlePhonemeData(session, data);
          break;
        case 'ready':
          // Client acknowledges connection and is ready
          this.logger.log('Client ready', { sessionId: session.id });
          session.ws.send(JSON.stringify({
            type: 'ready_ack',
            sessionId: session.id,
            message: 'Server ready for streaming'
          }));
          break;
        default:
          session.ws.send(JSON.stringify({
            type: 'error',
            message: `Unknown message type: ${data.type}`
          }));
      }
    } catch (error) {
      this.logger.error('WebSocket message error', { sessionId: session.id, error });
      session.ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid message format'
      }));
    }
  }

  async handlePhonemeData(session, data) {
    // Update session phoneme data for rendering
    session.phonemes = data.phonemes || [];
    session.audioTimestamp = data.audioTimestamp;

    // Render and send frame if streaming is active
    if (session.isActive && !session.isPaused) {
      const currentTime = (Date.now() - session.startTime) / 1000;
      const mouthOpen = this.getMouthOpenAtTime(session.phonemes, currentTime);

      try {
        const frameBuffer = await this.renderer.renderFrame(currentTime, mouthOpen);
        const frameData = frameBuffer.toString('base64');

        this.sessionManager.sendFrame(session.id, {
          type: 'frame',
          sessionId: session.id,
          timestamp: currentTime,
          frameData: `data:image/png;base64,${frameData}`
        });
      } catch (error) {
        this.logger.error('Frame rendering error', { sessionId: session.id, error });
      }
    }
  }

  getMouthOpenAtTime(phonemes, time) {
    if (!phonemes || phonemes.length === 0) return 0.0;

    for (const phoneme of phonemes) {
      if (time >= phoneme.start && time <= phoneme.end) {
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
    return 0.0;
  }

  // Route handlers
  handleRoot(req, res) {
    res.json({
      service: 'Avatar Renderer API',
      version: '2.0.0',
      status: 'running',
      renderer: this.renderer.getCapabilities(),
      documentation: {
        swagger: '/docs',
        api_summary: '/api-docs',
        health: '/health',
        metrics: '/metrics',
        status: '/status'
      }
    });
  }

  handleHealth(req, res) {
    const isHealthy = this.renderer.isInitialized && this.sessionManager;
    res.status(isHealthy ? 200 : 503).json({
      status: isHealthy ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      uptime: ((Date.now() - this.startTime) / 1000).toFixed(2),
      renderer: this.renderer.isInitialized ? 'ready' : 'not_ready'
    });
  }

  handleMetrics(req, res) {
    const sessionStats = this.sessionManager.getStats();
    const uptime = (Date.now() - this.startTime) / 1000;

    res.json({
      uptime: uptime.toFixed(2),
      requests: {
        total: this.requestCount,
        rate: (this.requestCount / uptime).toFixed(2)
      },
      sessions: sessionStats,
      renderer: this.renderer.getCapabilities()
    });
  }

  handleStatus(req, res) {
    res.json({
      server: {
        port: this.config.port,
        host: this.config.host,
        uptime: ((Date.now() - this.startTime) / 1000).toFixed(2)
      },
      renderer: this.renderer.getCapabilities(),
      sessions: this.sessionManager.getStats(),
      memory: process.memoryUsage()
    });
  }

  handleApiDocs(req, res) {
    res.json({
      service: 'Avatar Renderer API',
      version: '2.0.0',
      endpoints: [
        { path: '/', method: 'GET', description: 'Service information' },
        { path: '/health', method: 'GET', description: 'Health check' },
        { path: '/metrics', method: 'GET', description: 'Performance metrics' },
        { path: '/status', method: 'GET', description: 'System status' },
        { path: '/api-docs', method: 'GET', description: 'API documentation' },
        { path: '/render/lipsync', method: 'POST', description: 'Render lip-sync video' }
      ],
      websocket: {
        url: `ws://${this.config.host}:${this.config.port}`,
        messages: ['start_stream', 'stop_stream', 'pause_stream', 'resume_stream', 'phoneme_data']
      }
    });
  }

  async handleLipSyncRender(req, res) {
    const startTime = Date.now();
    const requestId = req.requestId;

    try {
      const { phonemes, audioUrl, duration } = req.body;

      if (!phonemes || !Array.isArray(phonemes)) {
        return res.status(400).json({ error: 'phonemes array required' });
      }

      this.logger.log(`[${requestId}] Starting lip-sync render`, {
        phonemesCount: phonemes.length,
        duration
      });

      // Generate video frames
      const totalDuration = duration || this.calculateDuration(phonemes);
      const fps = 30;
      const frames = [];

      for (let i = 0; i < Math.ceil(totalDuration * fps); i++) {
        const time = i / fps;
        const mouthOpen = this.getMouthOpenAtTime(phonemes, time);
        const frameBuffer = await this.renderer.renderFrame(time, mouthOpen);
        frames.push(frameBuffer);
      }

      // Encode video
      const outputPath = `/tmp/avatar_${requestId}.webm`;
      await this.videoEncoder.encodeFromBuffers(frames, outputPath, fps, audioUrl);

      // Read and send video
      const fs = await import('fs');
      const videoBuffer = fs.readFileSync(outputPath);

      const processingTime = Date.now() - startTime;
      this.logger.log(`[${requestId}] Render completed`, {
        duration: totalDuration,
        processingTime: `${processingTime}ms`,
        videoSize: `${videoBuffer.length} bytes`
      });

      res.setHeader('Content-Type', 'video/webm');
      res.setHeader('Content-Length', videoBuffer.length);
      res.setHeader('X-Processing-Time', `${processingTime}ms`);
      res.send(videoBuffer);

      // Cleanup
      fs.unlinkSync(outputPath);

    } catch (error) {
      const processingTime = Date.now() - startTime;
      this.logger.error(`[${requestId}] Render failed`, { error, processingTime });

      res.status(500).json({
        error: 'Render failed',
        message: error.message,
        requestId,
        processingTime: `${processingTime}ms`
      });
    }
  }

  calculateDuration(phonemes) {
    if (!phonemes || phonemes.length === 0) return 0;
    const lastPhoneme = phonemes[phonemes.length - 1];
    return lastPhoneme.end || 0;
  }

  errorHandler(err, req, res, next) {
    this.logger.error('Request error', {
      requestId: req.requestId,
      error: err.message,
      stack: err.stack
    });

    res.status(err.status || 500).json({
      error: err.message || 'Internal server error',
      requestId: req.requestId
    });
  }

  /**
   * Start the server
   */
  async start() {
    const success = await this.initialize();
    if (!success) {
      throw new Error('Failed to initialize server');
    }

    return new Promise((resolve) => {
      this.server.listen(this.config.port, this.config.host, () => {
        this.logger.log(`Avatar Renderer Server running on ${this.config.host}:${this.config.port}`);
        this.logger.log(`Swagger UI: http://${this.config.host}:${this.config.port}/docs`);
        this.logger.log(`WebSocket: ws://${this.config.host}:${this.config.port}`);
        resolve();
      });
    });
  }

  /**
   * Stop the server gracefully
   */
  async stop() {
    this.logger.log('Shutting down Avatar Renderer Server...');

    // Stop session manager
    if (this.sessionManager) {
      await this.sessionManager.shutdown();
    }

    // Close WebSocket server
    if (this.wss) {
      this.wss.close();
    }

    // Dispose renderer
    if (this.renderer) {
      await this.renderer.dispose();
    }

    // Close HTTP server
    return new Promise((resolve) => {
      this.server.close(() => {
        this.logger.log('Server shutdown complete');
        resolve();
      });
    });
  }
}

export default AvatarServer;
