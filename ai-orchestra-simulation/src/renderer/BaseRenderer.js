/**
 * BaseRenderer - Abstract base class for avatar renderers
 * 
 * Defines the interface that all renderer implementations must follow.
 * Supports both Canvas-based 2D rendering and Three.js 3D rendering.
 */

export class BaseRenderer {
  constructor(config = {}) {
    if (new.target === BaseRenderer) {
      throw new Error('BaseRenderer is abstract and cannot be instantiated directly');
    }

    this.config = {
      width: 1920,
      height: 1080,
      fps: 30,
      backgroundColor: '#1a1a2e',
      ...config
    };

    this.logger = config.logger || console;
    this.isInitialized = false;
  }

  /**
   * Initialize the renderer
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    throw new Error('initialize() must be implemented by subclass');
  }

  /**
   * Render a single frame at the given time
   * @param {number} time - Current time in seconds
   * @param {number} mouthOpen - Mouth openness value (0-1)
   * @returns {Promise<Buffer>} Frame data as buffer
   */
  async renderFrame(time, mouthOpen) {
    throw new Error('renderFrame() must be implemented by subclass');
  }

  /**
   * Clean up renderer resources
   */
  async dispose() {
    throw new Error('dispose() must be implemented by subclass');
  }

  /**
   * Get renderer capabilities
   * @returns {Object} Capabilities object
   */
  getCapabilities() {
    return {
      type: 'base',
      supports3D: false,
      supportsMorphTargets: false,
      maxResolution: { width: this.config.width, height: this.config.height },
      maxFPS: this.config.fps
    };
  }

  /**
   * Validate renderer configuration
   * @param {Object} config - Configuration to validate
   * @throws {Error} If configuration is invalid
   */
  validateConfig(config) {
    if (config.width && (config.width < 100 || config.width > 7680)) {
      throw new Error(`Invalid width: ${config.width}. Must be between 100 and 7680`);
    }
    if (config.height && (config.height < 100 || config.height > 4320)) {
      throw new Error(`Invalid height: ${config.height}. Must be between 100 and 4320`);
    }
    if (config.fps && (config.fps < 1 || config.fps > 120)) {
      throw new Error(`Invalid fps: ${config.fps}. Must be between 1 and 120`);
    }
  }
}

export default BaseRenderer;
