/**
 * R3FRenderer - React Three Fiber renderer bridge
 *
 * Bridges the backend avatar rendering system with React Three Fiber frontend.
 * Instead of rendering frames locally, this renderer sends phoneme data via WebSocket
 * to connected R3F clients that handle the actual 3D rendering and lip-sync animation.
 *
 * Architecture:
 * - Extends BaseRenderer interface for compatibility
 * - WebSocket server for real-time communication with R3F clients
 * - Sends phoneme data instead of rendering frames
 * - Supports multiple concurrent R3F client connections
 * - Production-ready with connection pooling and error handling
 */

import { WebSocketServer } from 'ws';
import { BaseRenderer } from './BaseRenderer.js';

export class R3FRenderer extends BaseRenderer {
  constructor(config = {}) {
    super(config);

    // R3F-specific configuration
    this.config = {
      ...this.config,
      websocket: {
        port: config.websocketPort || 3002,
        host: config.websocketHost || 'localhost',
        maxConnections: config.maxConnections || 50,
        heartbeatInterval: config.heartbeatInterval || 30000, // 30 seconds
        ...config.websocket
      }
    };

    this.wss = null;
    this.connections = new Map(); // sessionId -> { ws, lastHeartbeat, sessionData }
    this.connectionCounter = 0;
  }

  async initialize() {
    try {
      this.validateConfig(this.config);

      // Initialize WebSocket server for R3F clients
      this.wss = new WebSocketServer({
        port: this.config.websocket.port,
        host: this.config.websocket.host
      });

      // Set up WebSocket event handlers
      this.setupWebSocketHandlers();

      this.logger.log('R3FRenderer initialized', {
        websocket: {
          port: this.config.websocket.port,
          host: this.config.websocket.host,
          maxConnections: this.config.websocket.maxConnections
        },
        renderer: {
          width: this.config.width,
          height: this.config.height,
          fps: this.config.fps
        }
      });

      this.isInitialized = true;
      return true;
    } catch (error) {
      this.logger.error('Failed to initialize R3FRenderer:', error);
      return false;
    }
  }

  setupWebSocketHandlers() {
    this.wss.on('connection', (ws, req) => {
      const sessionId = this.generateSessionId();
      const connection = {
        ws,
        sessionId,
        lastHeartbeat: Date.now(),
        connectedAt: Date.now(),
        sessionData: {
          ip: req.socket.remoteAddress,
          userAgent: req.headers['user-agent'],
          isActive: false
        }
      };

      // Check connection limit
      if (this.connections.size >= this.config.websocket.maxConnections) {
        ws.close(1008, 'Max connections reached');
        this.logger.warn('Rejected connection - max connections reached', {
          currentConnections: this.connections.size,
          maxConnections: this.config.websocket.maxConnections
        });
        return;
      }

      // Store connection
      this.connections.set(sessionId, connection);

      // Send welcome message with session info
      ws.send(JSON.stringify({
        type: 'connected',
        sessionId,
        message: 'R3F renderer session established',
        capabilities: this.getCapabilities(),
        timestamp: Date.now()
      }));

      this.logger.log('R3F client connected', {
        sessionId,
        totalConnections: this.connections.size,
        clientInfo: {
          ip: connection.sessionData.ip,
          userAgent: connection.sessionData.userAgent
        }
      });

      // Handle messages from R3F client
      ws.on('message', (message) => {
        this.handleWebSocketMessage(sessionId, message);
      });

      // Handle disconnection
      ws.on('close', (code, reason) => {
        this.handleDisconnection(sessionId, code, reason);
      });

      ws.on('error', (error) => {
        this.logger.error('WebSocket error', { sessionId, error });
        this.handleDisconnection(sessionId, 1006, 'WebSocket error');
      });

      // Start heartbeat monitoring
      this.startHeartbeat(sessionId);
    });

    // Start periodic cleanup of stale connections
    this.startConnectionCleanup();
  }

  generateSessionId() {
    this.connectionCounter++;
    return `r3f_${Date.now()}_${this.connectionCounter}`;
  }

  handleWebSocketMessage(sessionId, message) {
    try {
      const connection = this.connections.get(sessionId);
      if (!connection) return;

      const data = JSON.parse(message.toString());
      connection.lastHeartbeat = Date.now();

      this.logger.debug('Received message from R3F client', {
        sessionId,
        messageType: data.type
      });

      switch (data.type) {
        case 'heartbeat':
          // Client heartbeat - update last seen
          connection.lastHeartbeat = Date.now();
          break;

        case 'ready':
          // Client is ready to receive phoneme data
          connection.sessionData.isActive = true;
          connection.ws.send(JSON.stringify({
            type: 'ready_ack',
            sessionId,
            timestamp: Date.now()
          }));
          break;

        case 'disconnect':
          // Client wants to disconnect gracefully
          this.handleDisconnection(sessionId, 1000, 'client_disconnect');
          break;

        default:
          this.logger.warn('Unknown message type from R3F client', {
            sessionId,
            messageType: data.type
          });
      }
    } catch (error) {
      this.logger.error('Error handling WebSocket message', {
        sessionId,
        error: error.message
      });
    }
  }

  handleDisconnection(sessionId, code, reason) {
    const connection = this.connections.get(sessionId);
    if (!connection) return;

    this.logger.log('R3F client disconnected', {
      sessionId,
      code,
      reason: reason?.toString(),
      connectionDuration: Date.now() - connection.connectedAt
    });

    // Clean up connection
    this.connections.delete(sessionId);

    // Stop heartbeat for this session
    if (connection.heartbeatInterval) {
      clearInterval(connection.heartbeatInterval);
    }
  }

  startHeartbeat(sessionId) {
    const connection = this.connections.get(sessionId);
    if (!connection) return;

    connection.heartbeatInterval = setInterval(() => {
      const now = Date.now();
      const timeSinceLastHeartbeat = now - connection.lastHeartbeat;

      // Check if client is still alive (allow 2x heartbeat interval)
      if (timeSinceLastHeartbeat > this.config.websocket.heartbeatInterval * 2) {
        this.logger.warn('R3F client heartbeat timeout', {
          sessionId,
          timeSinceLastHeartbeat
        });
        connection.ws.close(1008, 'Heartbeat timeout');
        return;
      }

      // Send heartbeat to client
      try {
        connection.ws.send(JSON.stringify({
          type: 'heartbeat',
          timestamp: now
        }));
      } catch (error) {
        this.logger.error('Failed to send heartbeat', { sessionId, error });
        connection.ws.close(1008, 'Heartbeat send failed');
      }
    }, this.config.websocket.heartbeatInterval);
  }

  startConnectionCleanup() {
    // Clean up stale connections every 5 minutes
    setInterval(() => {
      const now = Date.now();
      const staleThreshold = this.config.websocket.heartbeatInterval * 3; // 3x heartbeat interval

      for (const [sessionId, connection] of this.connections.entries()) {
        const timeSinceLastHeartbeat = now - connection.lastHeartbeat;

        if (timeSinceLastHeartbeat > staleThreshold) {
          this.logger.warn('Cleaning up stale R3F connection', {
            sessionId,
            timeSinceLastHeartbeat
          });
          connection.ws.close(1008, 'Stale connection');
        }
      }
    }, 300000); // 5 minutes
  }

  /**
   * Send phoneme data to all connected R3F clients
   * This replaces the traditional renderFrame() method
   */
  async renderFrame(time, mouthOpen, phonemeData = null) {
    if (!this.isInitialized) {
      throw new Error('R3FRenderer not initialized. Call initialize() first.');
    }

    // Prepare phoneme data for R3F clients
    const frameData = {
      type: 'phoneme_frame',
      timestamp: time,
      mouthOpen,
      phonemeData,
      serverTime: Date.now()
    };

    // Send to all active connections
    let sentCount = 0;
    for (const [sessionId, connection] of this.connections.entries()) {
      if (connection.sessionData.isActive && connection.ws.readyState === 1) { // OPEN
        try {
          connection.ws.send(JSON.stringify(frameData));
          sentCount++;
        } catch (error) {
          this.logger.error('Failed to send frame to R3F client', {
            sessionId,
            error: error.message
          });
          // Mark connection as potentially unhealthy
          connection.sessionData.isActive = false;
        }
      }
    }

    this.logger.debug('Sent phoneme frame to R3F clients', {
      totalConnections: this.connections.size,
      activeConnections: sentCount,
      timestamp: time,
      mouthOpen
    });

    // Return success indicator (not actual frame buffer)
    return Buffer.from(JSON.stringify({
      type: 'frame_sent',
      clientsReached: sentCount,
      totalClients: this.connections.size,
      timestamp: time
    }));
  }

  /**
   * Broadcast custom message to all connected R3F clients
   */
  async broadcastMessage(message) {
    if (!this.isInitialized) return false;

    const messageData = {
      type: 'broadcast',
      ...message,
      serverTime: Date.now()
    };

    let sentCount = 0;
    for (const [sessionId, connection] of this.connections.entries()) {
      if (connection.sessionData.isActive && connection.ws.readyState === 1) {
        try {
          connection.ws.send(JSON.stringify(messageData));
          sentCount++;
        } catch (error) {
          this.logger.error('Failed to broadcast to R3F client', {
            sessionId,
            error: error.message
          });
        }
      }
    }

    this.logger.log('Broadcast message sent', {
      messageType: message.type,
      clientsReached: sentCount,
      totalClients: this.connections.size
    });

    return sentCount > 0;
  }

  async dispose() {
    this.logger.log('Disposing R3FRenderer...');

    // Close all WebSocket connections
    for (const [sessionId, connection] of this.connections.entries()) {
      try {
        if (connection.heartbeatInterval) {
          clearInterval(connection.heartbeatInterval);
        }
        connection.ws.close(1000, 'Server shutdown');
      } catch (error) {
        this.logger.error('Error closing connection', { sessionId, error });
      }
    }

    this.connections.clear();

    // Close WebSocket server
    if (this.wss) {
      this.wss.close();
      this.wss = null;
    }

    this.isInitialized = false;
    this.logger.log('R3FRenderer disposed');
  }

  getCapabilities() {
    return {
      type: 'r3f',
      supports3D: true,
      supportsMorphTargets: true,
      maxResolution: { width: 3840, height: 2160 }, // 4K max
      maxFPS: 60,
      websocket: {
        port: this.config.websocket.port,
        host: this.config.websocket.host,
        maxConnections: this.config.websocket.maxConnections
      },
      description: 'React Three Fiber renderer with WebSocket bridge for real-time 3D avatar animation'
    };
  }

  /**
   * Get current connection statistics
   */
  getConnectionStats() {
    const stats = {
      totalConnections: this.connections.size,
      activeConnections: 0,
      totalSessions: this.connectionCounter
    };

    for (const connection of this.connections.values()) {
      if (connection.sessionData.isActive) {
        stats.activeConnections++;
      }
    }

    return stats;
  }
}

export default R3FRenderer;