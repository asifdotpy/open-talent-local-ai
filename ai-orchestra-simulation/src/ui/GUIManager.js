import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import { Logger } from '../utils/Logger.js';

/**
 * Manages GUI controls for lip-sync animation and performance monitoring.
 */
export class GUIManager {
  constructor({ animationController, performanceMonitor, debugManager, audioOnly = false }) {
    this.animationController = animationController;
    this.performanceMonitor = performanceMonitor;
    this.debugManager = debugManager;
    this.audioOnly = audioOnly;
    this.gui = new GUI();
    this.logger = Logger.getInstance();

    this.init();
  }

  init() {
    this.gui.title(this.audioOnly ? 'Audio Interview Controls' : 'AI Orchestra Controls');

    if (!this.audioOnly) {
      this.createAnimationControls();
    }

    this.createAudioControls();
    this.createPerformanceMonitor();

    if (!this.audioOnly) {
      this.createDebugInfo();
    }

    this.logger.log('SUCCESS', `GUI Manager initialized (${this.audioOnly ? 'audio-only' : 'full'} mode).`);
  }

  createAnimationControls() {
    const animFolder = this.gui.addFolder('Animation');

    // Animation state controls
    animFolder.add({ play: () => this.animationController.start() }, 'play').name('Start Animation');
    animFolder.add({ stop: () => this.animationController.stop() }, 'stop').name('Stop Animation');
    animFolder.add({ reset: () => this.animationController.resetToOriginalState() }, 'reset').name('Reset Mesh');

    // Add lip-sync toggle for performance control
    const lipSyncControl = { enabled: false }; // Start disabled for performance
    animFolder.add(lipSyncControl, 'enabled').name('Enable Lip-Sync').onChange((value) => {
      if (value) {
        this.animationController.start();
        // Notify performance monitor that lip-sync is active
        if (this.performanceMonitor && this.performanceMonitor.setLipSyncActive) {
          this.performanceMonitor.setLipSyncActive(true);
        }
        console.log('Lip-sync enabled - expect some FPS reduction');
      } else {
        this.animationController.stop();
        // Notify performance monitor that lip-sync is inactive
        if (this.performanceMonitor && this.performanceMonitor.setLipSyncActive) {
          this.performanceMonitor.setLipSyncActive(false);
        }
        console.log('Lip-sync disabled - FPS should improve');
      }
    });

    animFolder.open();
  }

  createAudioControls() {
    const audioFolder = this.gui.addFolder('Audio');

    // Audio playback controls
    audioFolder.add({ play: () => this.playAudio() }, 'play').name('Play Audio');
    audioFolder.add({ pause: () => this.pauseAudio() }, 'pause').name('Pause Audio');
    audioFolder.add({ stop: () => this.stopAudio() }, 'stop').name('Stop Audio');

    // Volume control
    const volumeControl = { volume: 0.8 };
    audioFolder.add(volumeControl, 'volume', 0, 1, 0.1).name('Volume').onChange((value) => {
      const audioElement = document.getElementById('speech-audio');
      if (audioElement) {
        audioElement.volume = value;
      }
    });

    // Audio info
    if (this.audioOnly) {
      audioFolder.add({ info: 'Audio visualization shows real-time frequency analysis' }, 'info').name('Mode Info').disable();
    }

    audioFolder.open();
  }

  playAudio() {
    const audioElement = document.getElementById('speech-audio');
    if (audioElement) {
      const existingCtx = audioElement._audioContext;
      if (existingCtx) {
        if (existingCtx.state === 'suspended') {
          existingCtx.resume().catch(err => console.error('Failed to resume audioContext:', err));
        }
        audioElement.play().catch(error => console.error('Failed to play audio:', error));
      } else {
        // Fallback: direct play (visualization may not be wired yet)
        audioElement.play().catch(error => console.error('Failed to play audio:', error));
      }
    }
  }

  pauseAudio() {
    const audioElement = document.getElementById('speech-audio');
    if (audioElement) {
      audioElement.pause();
    }
  }

  stopAudio() {
    const audioElement = document.getElementById('speech-audio');
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
    }
  }

  createPerformanceMonitor() {
    const perfFolder = this.gui.addFolder('Performance');

    // Create dummy objects for GUI binding
    const perfStats = { fps: 0, memory: 0 };
    perfFolder.add(perfStats, 'fps', 0, 120).name('FPS').listen();
    perfFolder.add(perfStats, 'memory', 0, 200).name('Memory (MB)').listen();

    // Update function to refresh values
    this.updatePerformanceStats = () => {
      const report = this.performanceMonitor.getPerformanceReport();
      if (report && report.current) {
        perfStats.fps = report.current.fps || 0;
        perfStats.memory = report.current.memory || 0;
      }
    };

    perfFolder.open();
  }

  createDebugInfo() {
    const debugFolder = this.gui.addFolder('Debug Info');

    // Create dummy objects for GUI binding
    const debugStats = {
      strategy: 'Vertex-based',
      vertexCount: 0,
      confidence: 0,
      issues: 'None'
    };

    debugFolder.add(debugStats, 'strategy').name('Strategy').listen();
    debugFolder.add(debugStats, 'vertexCount').name('Mouth Vertices').listen();
    debugFolder.add(debugStats, 'confidence').name('Confidence').listen();
    debugFolder.add(debugStats, 'issues').name('Issues').listen();

    // Update function to refresh values
    this.updateDebugStats = () => {
      // Guard for audio-only mode or missing animation controller
      if (!this.animationController || typeof this.animationController.getDetectionDiagnostics !== 'function') {
        return;
      }
      const diagnostics = this.animationController.getDetectionDiagnostics();
      if (!diagnostics) {
        return;
      }
      debugStats.strategy = diagnostics.strategy ?? 'N/A';
      debugStats.vertexCount = diagnostics.vertexCount ?? 0;
      debugStats.confidence = diagnostics.confidence ?? 0;
      const issues = Array.isArray(diagnostics.issues) ? diagnostics.issues : [];
      debugStats.issues = issues.join(', ') || 'None';
    };

    debugFolder.open();
  }

  update() {
    if (this.updatePerformanceStats) {
      this.updatePerformanceStats();
    }
    if (this.updateDebugStats) {
      this.updateDebugStats();
    }
  }

  dispose() {
    if (this.gui) {
      this.gui.destroy();
    }
    this.logger.log('SUCCESS', 'GUI manager disposed');
  }
}
