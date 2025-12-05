import { Logger } from '../utils/Logger.js';

/**
 * Core debugging framework for transparency and diagnostics.
 */
export class DebugManager {
  constructor(app) {
    this.app = app;
    this.logger = Logger.getInstance();
    this.debugInfo = {
      detectionStrategy: 'N/A',
      vertexCount: 0,
      confidence: 'N/A',
      issues: 'N/A',
    };
  }

  initialize() {
    this.logger.log('DEBUG', 'Debug Manager initialized.');
  }

  update() {
    if (this.app.animationController) {
      const diagnostics = this.app.animationController.getDetectionDiagnostics();
      this.debugInfo.detectionStrategy = diagnostics.strategy;
      this.debugInfo.vertexCount = diagnostics.vertexCount;
      this.debugInfo.confidence = diagnostics.confidence;
      this.debugInfo.issues = diagnostics.issues;
    }
  }

  getDebugInfo() {
    return this.debugInfo;
  }
}
