/**
 * CanvasRenderer - 2D Canvas-based avatar renderer
 * 
 * Fast, lightweight renderer using Node.js Canvas API.
 * Suitable for simple avatar animations with minimal resource usage.
 * Phase 2 MVP implementation - production-ready for basic use cases.
 */

import { createCanvas } from 'canvas';
import { BaseRenderer } from './BaseRenderer.js';

export class CanvasRenderer extends BaseRenderer {
  constructor(config = {}) {
    super(config);
    this.canvas = null;
    this.ctx = null;
  }

  async initialize() {
    try {
      this.validateConfig(this.config);

      // Create canvas
      this.canvas = createCanvas(this.config.width, this.config.height);
      this.ctx = this.canvas.getContext('2d');

      this.logger.log('CanvasRenderer initialized', {
        width: this.config.width,
        height: this.config.height,
        fps: this.config.fps
      });

      this.isInitialized = true;
      return true;
    } catch (error) {
      this.logger.error('Failed to initialize CanvasRenderer:', error);
      return false;
    }
  }

  async renderFrame(time, mouthOpen) {
    if (!this.isInitialized) {
      throw new Error('Renderer not initialized. Call initialize() first.');
    }

    // Clear canvas
    this.ctx.fillStyle = this.config.backgroundColor;
    this.ctx.fillRect(0, 0, this.config.width, this.config.height);

    // Draw avatar face
    this.drawAvatarFace(mouthOpen);

    // Return frame as buffer
    return this.canvas.toBuffer('image/png');
  }

  drawAvatarFace(mouthOpen) {
    const centerX = this.config.width / 2;
    const centerY = this.config.height / 2;
    const faceRadius = Math.min(this.config.width, this.config.height) / 4;

    // Draw face circle
    this.ctx.fillStyle = '#f4d1ae'; // Skin tone
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, faceRadius, 0, Math.PI * 2);
    this.ctx.fill();

    // Draw eyes
    const eyeY = centerY - faceRadius * 0.2;
    const eyeSpacing = faceRadius * 0.4;
    const eyeRadius = faceRadius * 0.08;

    this.ctx.fillStyle = '#2c3e50'; // Dark color for eyes
    this.ctx.beginPath();
    this.ctx.arc(centerX - eyeSpacing, eyeY, eyeRadius, 0, Math.PI * 2);
    this.ctx.arc(centerX + eyeSpacing, eyeY, eyeRadius, 0, Math.PI * 2);
    this.ctx.fill();

    // Draw mouth (animated based on phoneme)
    const mouthY = centerY + faceRadius * 0.3;
    const mouthWidth = faceRadius * 0.5;
    const mouthHeight = faceRadius * 0.3 * mouthOpen; // Animated height

    this.ctx.fillStyle = '#8b4513'; // Mouth color
    this.ctx.beginPath();
    this.ctx.ellipse(centerX, mouthY, mouthWidth, mouthHeight, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // Draw subtle smile curve when mouth closed
    if (mouthOpen < 0.3) {
      this.ctx.strokeStyle = '#8b4513';
      this.ctx.lineWidth = 3;
      this.ctx.beginPath();
      this.ctx.arc(centerX, mouthY - 10, mouthWidth * 0.8, 0.2, Math.PI - 0.2);
      this.ctx.stroke();
    }
  }

  async dispose() {
    this.canvas = null;
    this.ctx = null;
    this.isInitialized = false;
    this.logger.log('CanvasRenderer disposed');
  }

  getCapabilities() {
    return {
      type: 'canvas',
      supports3D: false,
      supportsMorphTargets: false,
      maxResolution: { width: 7680, height: 4320 }, // 8K max
      maxFPS: 120,
      description: 'Fast 2D canvas-based rendering for simple avatars'
    };
  }
}

export default CanvasRenderer;
