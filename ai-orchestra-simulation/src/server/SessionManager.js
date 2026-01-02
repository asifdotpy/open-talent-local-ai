/**
 * SessionManager - WebSocket session lifecycle management
 *
 * Handles WebSocket connections, session state, and resource management.
 * Features:
 * - Connection pooling with limits
 * - Graceful shutdown
 * - Reconnection logic
 * - Frame buffering
 * - Resource cleanup
 */

import crypto from 'crypto';
import { EventEmitter } from 'events';

export class SessionManager extends EventEmitter {
  constructor(config = {}) {
    super();

    this.config = {
      maxSessions: config.maxSessions || 100,
      sessionTimeout: config.sessionTimeout || 300000, // 5 minutes
      frameBufferSize: config.frameBufferSize || 30, // Buffer 30 frames
      heartbeatInterval: config.heartbeatInterval || 30000, // 30 seconds
      ...config
    };

    this.sessions = new Map();
    this.logger = config.logger || console;
    this.heartbeatTimer = null;
    this.isShuttingDown = false;
  }

  /**
   * Start session manager
   */
  start() {
    this.startHeartbeat();
    this.logger.log('SessionManager started', {
      maxSessions: this.config.maxSessions,
      sessionTimeout: this.config.sessionTimeout
    });
  }

  /**
   * Create a new session
   * @param {WebSocket} ws - WebSocket connection
   * @param {Object} metadata - Optional session metadata
   * @returns {Object|null} Session object or null if limit reached
   */
  createSession(ws, metadata = {}) {
    if (this.isShuttingDown) {
      this.logger.warn('Session creation rejected: shutting down');
      return null;
    }

    if (this.sessions.size >= this.config.maxSessions) {
      this.logger.warn('Session creation rejected: max sessions reached', {
        current: this.sessions.size,
        max: this.config.maxSessions
      });
      return null;
    }

    const sessionId = crypto.randomBytes(16).toString('hex');
    const session = {
      id: sessionId,
      ws: ws,
      metadata: metadata,
      isActive: false,
      isPaused: false,
      createdAt: Date.now(),
      lastActivity: Date.now(),
      frameBuffer: [],
      config: {
        width: 1920,
        height: 1080,
        fps: 30
      },
      stats: {
        framesSent: 0,
        messagesReceived: 0,
        errors: 0
      }
    };

    this.sessions.set(sessionId, session);

    this.logger.log('Session created', {
      sessionId,
      totalSessions: this.sessions.size,
      metadata
    });

    this.emit('session:created', session);
    return session;
  }

  /**
   * Get session by ID
   * @param {string} sessionId - Session ID
   * @returns {Object|null} Session object or null
   */
  getSession(sessionId) {
    return this.sessions.get(sessionId) || null;
  }

  /**
   * Update session activity timestamp
   * @param {string} sessionId - Session ID
   */
  touchSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.lastActivity = Date.now();
    }
  }

  /**
   * Start streaming for a session
   * @param {string} sessionId - Session ID
   * @param {Object} config - Streaming configuration
   */
  startStreaming(sessionId, config = {}) {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }

    session.isActive = true;
    session.isPaused = false;
    session.config = { ...session.config, ...config };
    session.startTime = Date.now();

    this.logger.log('Streaming started', {
      sessionId,
      config: session.config
    });

    this.emit('session:started', session);
  }

  /**
   * Pause streaming for a session
   * @param {string} sessionId - Session ID
   */
  pauseStreaming(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.isPaused = true;
      this.logger.log('Streaming paused', { sessionId });
      this.emit('session:paused', session);
    }
  }

  /**
   * Resume streaming for a session
   * @param {string} sessionId - Session ID
   */
  resumeStreaming(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.isPaused = false;
      this.logger.log('Streaming resumed', { sessionId });
      this.emit('session:resumed', session);
    }
  }

  /**
   * Stop streaming for a session
   * @param {string} sessionId - Session ID
   */
  stopStreaming(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.isActive = false;
      session.isPaused = false;

      const duration = session.startTime ? (Date.now() - session.startTime) / 1000 : 0;

      this.logger.log('Streaming stopped', {
        sessionId,
        duration: `${duration.toFixed(2)}s`,
        framesSent: session.stats.framesSent
      });

      this.emit('session:stopped', session);
    }
  }

  /**
   * Add frame to session buffer
   * @param {string} sessionId - Session ID
   * @param {Object} frame - Frame data
   */
  bufferFrame(sessionId, frame) {
    const session = this.sessions.get(sessionId);
    if (!session) return;

    session.frameBuffer.push(frame);

    // Limit buffer size
    if (session.frameBuffer.length > this.config.frameBufferSize) {
      session.frameBuffer.shift(); // Remove oldest frame
    }
  }

  /**
   * Send frame to client
   * @param {string} sessionId - Session ID
   * @param {Object} frameData - Frame data to send
   * @returns {boolean} Success status
   */
  sendFrame(sessionId, frameData) {
    const session = this.sessions.get(sessionId);
    if (!session || !session.isActive || session.isPaused) {
      return false;
    }

    try {
      if (session.ws.readyState === 1) { // WebSocket.OPEN
        session.ws.send(JSON.stringify(frameData));
        session.stats.framesSent++;
        this.touchSession(sessionId);
        return true;
      }
    } catch (error) {
      this.logger.error('Failed to send frame', { sessionId, error: error.message });
      session.stats.errors++;
    }

    return false;
  }

  /**
   * Close a session
   * @param {string} sessionId - Session ID
   * @param {string} reason - Close reason
   */
  closeSession(sessionId, reason = 'normal') {
    const session = this.sessions.get(sessionId);
    if (!session) return;

    this.stopStreaming(sessionId);

    try {
      if (session.ws.readyState === 1) { // WebSocket.OPEN
        session.ws.close(1000, reason);
      }
    } catch (error) {
      this.logger.warn('Error closing WebSocket', { sessionId, error: error.message });
    }

    this.sessions.delete(sessionId);

    const lifespan = (Date.now() - session.createdAt) / 1000;

    this.logger.log('Session closed', {
      sessionId,
      reason,
      lifespan: `${lifespan.toFixed(2)}s`,
      framesSent: session.stats.framesSent,
      totalSessions: this.sessions.size
    });

    this.emit('session:closed', { sessionId, reason, session });
  }

  /**
   * Start heartbeat to check for stale sessions
   */
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.checkStaleSessions();
    }, this.config.heartbeatInterval);
  }

  /**
   * Check for and close stale sessions
   */
  checkStaleSessions() {
    const now = Date.now();
    const staleSessionIds = [];

    for (const [sessionId, session] of this.sessions.entries()) {
      const idleTime = now - session.lastActivity;

      if (idleTime > this.config.sessionTimeout) {
        staleSessionIds.push(sessionId);
      }
    }

    if (staleSessionIds.length > 0) {
      this.logger.log('Closing stale sessions', { count: staleSessionIds.length });
      staleSessionIds.forEach(id => this.closeSession(id, 'timeout'));
    }
  }

  /**
   * Get session statistics
   * @returns {Object} Statistics object
   */
  getStats() {
    const stats = {
      totalSessions: this.sessions.size,
      activeSessions: 0,
      pausedSessions: 0,
      totalFramesSent: 0,
      totalErrors: 0
    };

    for (const session of this.sessions.values()) {
      if (session.isActive && !session.isPaused) stats.activeSessions++;
      if (session.isPaused) stats.pausedSessions++;
      stats.totalFramesSent += session.stats.framesSent;
      stats.totalErrors += session.stats.errors;
    }

    return stats;
  }

  /**
   * Graceful shutdown
   * @returns {Promise<void>}
   */
  async shutdown() {
    this.isShuttingDown = true;

    this.logger.log('SessionManager shutting down', {
      activeSessions: this.sessions.size
    });

    // Stop heartbeat
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    // Close all sessions
    const sessionIds = Array.from(this.sessions.keys());
    for (const sessionId of sessionIds) {
      this.closeSession(sessionId, 'server_shutdown');
    }

    this.logger.log('SessionManager shutdown complete');
    this.emit('shutdown');
  }
}

export default SessionManager;
