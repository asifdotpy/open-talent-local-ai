/**
 * Default Configuration
 * 
 * Base configuration values that can be overridden by environment-specific configs
 */

export const defaultConfig = {
  // Server configuration
  server: {
    port: 3001,
    host: 'localhost',
    corsOrigins: '*',
    requestLimit: '50mb'
  },

  // Renderer configuration
  renderer: {
    type: process.env.RENDERER_TYPE || 'canvas', // Production uses Canvas renderer only
    width: parseInt(process.env.VIDEO_WIDTH) || 1920,
    height: parseInt(process.env.VIDEO_HEIGHT) || 1080,
    fps: parseInt(process.env.VIDEO_FPS) || 30,
    backgroundColor: '#1a1a2e'
  },

  // Model configuration (for Three.js renderer)
  model: {
    path: './assets/models/face.glb',
    scale: { x: 1, y: 1, z: 1 },
    position: { x: 0, y: 1.2, z: 0 },
    cameraPosition: { x: 0, y: 1.2, z: 1.8 }
  },

  // Video encoding configuration
  video: {
    codec: 'libvpx-vp9',
    format: 'webm',
    bitrate: '1M',
    audioCodec: 'libopus',
    verbose: false
  },

  // Session management configuration
  session: {
    maxSessions: 100,
    sessionTimeout: 300000, // 5 minutes
    frameBufferSize: 30,
    heartbeatInterval: 30000 // 30 seconds
  },

  // Logging configuration
  logging: {
    level: 'info', // 'debug', 'info', 'warn', 'error'
    format: 'json', // 'json' or 'text'
    includeTimestamp: true,
    includeRequestId: true
  },

  // Feature flags
  features: {
    enableWebSocket: true,
    enableVideoRendering: true,
    enableMetrics: true,
    enableSwagger: true
  }
};

export default defaultConfig;
