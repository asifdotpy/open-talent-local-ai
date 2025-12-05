/**
 * AI Orchestra Simulation - Shared Avatar Animation Library
 * 
 * This module exports the core avatar rendering and animation components
 * for use by other services (e.g., avatar-service).
 * 
 * @module ai-orchestra-simulation
 */

// Core Components
export { Application } from './src/core/Application.js';
export { AssetManager } from './src/core/AssetManager.js';
export { DebugManager } from './src/core/DebugManager.js';
export { MeshManager } from './src/core/MeshManager.js';
export { SceneManager } from './src/core/SceneManager.js';

// Animation Controllers
export { AnimationController } from './src/animation/AnimationController.js';
export { MorphTargetAnimationController } from './src/animation/MorphTargetAnimationController.js';
export { PhonemeMapper } from './src/animation/PhonemeMapper.js';

// UI Components
export { CaptionsOverlay } from './src/ui/CaptionsOverlay.js';
export { GUIManager } from './src/ui/GUIManager.js';
export { MouthSelectionGUI } from './src/ui/MouthSelectionGUI.js';

// Utilities
export { Logger } from './src/utils/Logger.js';
export { PerformanceMonitor } from './src/utils/PerformanceMonitor.js';

// Network
export { WebRTCClient } from './src/network/WebRTCClient.js';

// Integration - Phase 1
export { VoiceServiceIntegration } from './src/integration/VoiceServiceIntegration.js';
export { VideoRecorder } from './src/video/VideoRecorder.js';

// Configuration
export { AppConfig } from './src/config/AppConfig.js';
export { ConfigManager, getConfig } from './src/config/ConfigManager.js';

// Server Components (Production - Version 2.0)
export { AvatarServer } from './src/server/AvatarServer.js';
export { SessionManager } from './src/server/SessionManager.js';

// Renderer Components (Production - Version 2.0)
export { BaseRenderer } from './src/renderer/BaseRenderer.js';
export { CanvasRenderer } from './src/renderer/CanvasRenderer.js';

// Video Encoding (Production - Version 2.0)
export { VideoEncoder } from './src/video/VideoEncoder.js';

// Logging (Production - Version 2.0)
export { StructuredLogger } from './src/utils/StructuredLogger.js';

// Main Server Class (Production - Version 2.0)
export { AvatarRendererServer } from './avatar-renderer-v2.js';

/**
 * Create a new avatar application instance with default configuration
 * 
 * @param {Object} config - Application configuration
 * @returns {Application} Configured application instance
 */
export function createAvatarApplication(config = {}) {
    const app = new Application(config);
    return app;
}

/**
 * Create animation controller based on mesh capabilities
 * 
 * @param {THREE.Mesh} mesh - The 3D mesh
 * @param {Object} config - Configuration
 * @param {Object} speechData - Speech data for lip-sync
 * @param {THREE.Audio} audioObject - Audio object
 * @param {MeshManager} meshManager - Mesh manager instance
 * @returns {AnimationController|MorphTargetAnimationController} Animation controller
 */
export function createAnimationController(mesh, config, speechData, audioObject, meshManager) {
    // Try morph target animation first (better performance)
    const morphController = new MorphTargetAnimationController(mesh, config, speechData, audioObject, meshManager);
    
    if (morphController.initialize()) {
        return morphController;
    }
    
    // Fallback to vertex-based animation
    const vertexController = new AnimationController(mesh, config, speechData, audioObject, meshManager);
    vertexController.initialize();
    return vertexController;
}
