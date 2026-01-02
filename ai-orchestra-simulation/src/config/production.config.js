/**
 * Production Configuration
 *
 * Production-specific configuration overrides
 */

export const productionConfig = {
  // Server configuration
  server: {
    port: process.env.PORT || 3001,
    host: process.env.HOST || '0.0.0.0',
    corsOrigins: process.env.CORS_ORIGINS || '*',
    requestLimit: '50mb'
  },

  // Renderer configuration
  renderer: {
    type: 'canvas', // Production uses Canvas renderer
    width: parseInt(process.env.VIDEO_WIDTH) || 1920,
    height: parseInt(process.env.VIDEO_HEIGHT) || 1080,
    fps: parseInt(process.env.VIDEO_FPS) || 30,
    backgroundColor: '#1a1a2e'
  },

  // Model configuration
  model: {
    path: process.env.MODEL_PATH || './assets/models/face.glb',
    scale: { x: 1, y: 1, z: 1 },
    position: { x: 0, y: 1.2, z: 0 },
    cameraPosition: { x: 0, y: 1.2, z: 1.8 }
  },

  // Video encoding configuration
  video: {
    codec: 'libvpx-vp9',
    format: 'webm',
    bitrate: process.env.VIDEO_BITRATE || '2M', // Higher bitrate for production
    audioCodec: 'libopus',
    verbose: false
  },

  // Session management configuration
  session: {
    maxSessions: parseInt(process.env.MAX_SESSIONS) || 200, // Higher limit in production
    sessionTimeout: parseInt(process.env.SESSION_TIMEOUT) || 300000,
    frameBufferSize: 30,
    heartbeatInterval: 30000
  },

  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: 'json', // Always JSON in production
    includeTimestamp: true,
    includeRequestId: true
  },

  // Feature flags
  features: {
    enableWebSocket: true,
    enableVideoRendering: true,
    enableMetrics: true,
    enableSwagger: process.env.ENABLE_SWAGGER !== 'false' // Disable if explicitly set
  }
};

export default productionConfig;
