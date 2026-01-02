/**
 * Avatar Rendering Server - Production Version 2.0
 *
 * Modular avatar rendering service with pluggable renderers and production features.
 *
 * Architecture:
 * - Modular renderer system (Canvas 2D / Three.js 3D)
 * - WebSocket session management with connection pooling
 * - Production logging and monitoring
 * - Environment-based configuration
 * - Health checks and metrics endpoints
 *
 * Usage:
 *   node avatar-renderer-v2.js                      # Development (Canvas renderer)
 *   NODE_ENV=production node avatar-renderer-v2.js  # Production (Three.js renderer)
 *   RENDERER_TYPE=threejs node avatar-renderer-v2.js # Force Three.js
 *   PORT=3002 node avatar-renderer-v2.js            # Custom port
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Modular components
import { getConfig } from './src/config/ConfigManager.js';
import { AvatarServer } from './src/server/AvatarServer.js';
import { StructuredLogger } from './src/utils/StructuredLogger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Main application class - Maintains backward compatibility
 * while using new modular architecture under the hood
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

    this.logger.info('Initializing Avatar Renderer Server', {
      version: '2.0.0',
      environment: configManager.getEnvironment(),
      renderer: config.renderer.type
    });

    // Initialize modular server with configuration
    this.server = new AvatarServer({
      port: config.server.port,
      host: config.server.host,
      rendererType: config.renderer.type,
      corsOrigins: config.server.corsOrigins,
      requestLimit: config.server.requestLimit,
      maxSessions: config.session.maxSessions,
      logger: this.logger
    });

    this.port = config.server.port;
    this.tempDir = path.join(__dirname, 'temp');

    // Ensure temp directory exists
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
  }

  /**
   * Start the server
   */
  async start() {
    try {
      this.logger.info('Starting Avatar Renderer Server...');
      await this.server.start();

      this.logger.info('Server started successfully', {
        port: this.port,
        endpoints: {
          health: `http://localhost:${this.port}/health`,
          metrics: `http://localhost:${this.port}/metrics`,
          status: `http://localhost:${this.port}/status`,
          docs: `http://localhost:${this.port}/docs`,
          api_summary: `http://localhost:${this.port}/api-docs`,
          render: `http://localhost:${this.port}/render/lipsync`,
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
      this.logger.info('Stopping Avatar Renderer Server...');
      await this.server.stop();
      this.logger.info('Server stopped successfully');
    } catch (error) {
      this.logger.error('Error stopping server', error);
      throw error;
    }
  }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const port = process.env.PORT ? parseInt(process.env.PORT) : 3001;
  const server = new AvatarRendererServer(port);

  // Graceful shutdown handling
  const shutdown = async () => {
    console.log('\nReceived shutdown signal...');
    try {
      await server.stop();
      process.exit(0);
    } catch (error) {
      console.error('Error during shutdown:', error);
      process.exit(1);
    }
  };

  // Increase max listeners to prevent EventEmitter leak warnings
  process.setMaxListeners(20);

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);

  // Start server
  server.start().catch((error) => {
    console.error('Fatal error starting server:', error);
    process.exit(1);
  });
}

export default AvatarRendererServer;
export { AvatarRendererServer };
