/**
 * Phase 1 Integration Test - WebGL Avatar with Audio-Video Sync
 *
 * Tests the complete Phase 1 pipeline:
 * 1. Voice Service audio synthesis with phonemes
 * 2. Real-time WebGL rendering with morph target animation
 * 3. VideoRecorder canvas capture with audio sync
 * 4. Synchronization verification (<50ms tolerance)
 */

import { Application } from '../src/core/Application.js';
import { VoiceServiceIntegration } from '../src/integration/VoiceServiceIntegration.js';
import { Logger } from '../src/utils/Logger.js';
import { VideoRecorder } from '../src/video/VideoRecorder.js';

class Phase1IntegrationTest {
  constructor() {
    this.logger = Logger.getInstance();
    this.logger.log('INIT', 'Phase 1 Integration Test Starting...');

    // Components
    this.app = null;
    this.voiceService = null;
    this.videoRecorder = null;
    this.animationController = null;

    // Metrics
    this.metrics = {
      startTime: Date.now(),
      framesRendered: 0,
      phonemesAnimated: 0,
      syncErrors: [],
    };

    this.isRunning = false;
  }

  /**
   * Initialize Phase 1 components
   */
  async initialize() {
    try {
      this.logger.log('INIT', 'Initializing Avatar Application...');

      // Create application
      this.app = new Application({
        containerId: 'canvas-container',
        features: {
          enableAvatar: true,
          enableVideoRecording: true,
          enablePhonemeAnimation: true,
          enableRealTimeSync: true,
        },
      });

      await this.app.initialize();
      this.logger.log('SUCCESS', 'Application initialized');

      // Get animation controller
      this.animationController = this.app.getAnimationController?.();
      if (!this.animationController) {
        throw new Error('AnimationController not available');
      }

      // Initialize Voice Service integration
      this.logger.log('INIT', 'Initializing Voice Service Integration...');
      this.voiceService = new VoiceServiceIntegration({
        voiceServiceUrl: 'http://localhost:8002',
        enablePhonemes: true,
        enableVisualizer: true,
      });

      // Setup callbacks
      this.voiceService.setOnPhonemeUpdate((phoneme) => {
        this.onPhonemeUpdate(phoneme);
      });

      this.voiceService.setOnAudioReady((info) => {
        this.logger.log('SUCCESS', 'Audio ready from Voice Service', info);
      });

      // Initialize VideoRecorder
      const canvas = document.querySelector('canvas');
      if (!canvas) {
        throw new Error('Canvas element not found');
      }

      this.logger.log('INIT', 'Initializing VideoRecorder...');
      this.videoRecorder = new VideoRecorder(canvas, this.voiceService.audioContext, {
        fps: 60,
        videoBitrate: 2500,
        audioBitrate: 128,
      });

      if (!VideoRecorder.checkBrowserSupport()) {
        this.logger.warn('WARN', 'Browser does not support required codecs');
      }

      this.logger.log('SUCCESS', 'Phase 1 components initialized');
      return true;
    } catch (error) {
      this.logger.error('ERROR', `Initialization failed: ${error.message}`);
      return false;
    }
  }

  /**
   * Start animation and recording loop
   */
  start() {
    if (this.isRunning) return;

    this.isRunning = true;
    this.logger.log('START', 'Phase 1 test started');

    // Start video recording
    this.videoRecorder.startRecording();
    this.logger.log('START', 'Video recording started');

    // Start render loop
    this.renderLoop();
  }

  /**
   * Main render loop
   */
  renderLoop = () => {
    if (!this.isRunning) return;

    // Update animation
    if (this.animationController) {
      this.animationController.update();
    }

    // Update phoneme mapper
    if (this.animationController?.getPhonemeMapper) {
      this.animationController.getPhonemeMapper().update();
    }

    // Update voice service phoneme
    if (this.voiceService) {
      this.voiceService.updatePhoneme();
    }

    // Record frame
    if (this.videoRecorder) {
      this.videoRecorder.recordFrame();
    }

    // Render
    if (this.app) {
      this.app.render();
    }

    this.metrics.framesRendered++;

    requestAnimationFrame(this.renderLoop);
  };

  /**
   * Handle phoneme updates from Voice Service
   */
  onPhonemeUpdate(phoneme) {
    if (!this.animationController) return;

    const mapper = this.animationController.getPhonemeMapper?.();
    if (mapper) {
      mapper.animatePhoneme(phoneme.label, 100);
      this.metrics.phonemesAnimated++;
    }

    // Log every 10th phoneme to reduce spam
    if (this.metrics.phonemesAnimated % 10 === 0) {
      this.logger.debug('PHONEME', `Animated ${this.metrics.phonemesAnimated} phonemes`);
    }
  }

  /**
   * Test synthesize -> render -> record flow
   */
  async testSynthesisFlow() {
    const testText = 'Hello, I am an AI avatar. Nice to meet you!';

    this.logger.log('TEST', `Synthesizing: "${testText}"`);

    try {
      // Synthesize speech
      const result = await this.voiceService.synthesizeSpeech(testText, {
        voice: 'default',
        speed: 1.0,
      });

      if (!result.success) {
        this.logger.error('ERROR', `Synthesis failed: ${result.error}`);
        return;
      }

      this.logger.log('SUCCESS', `Synthesis complete - ${result.phonemeCount} phonemes`);

      // Start render loop
      this.start();

      // Play audio
      this.voiceService.playAudio();
      this.logger.log('START', 'Audio playback started');

      // Wait for audio to complete
      const duration = result.duration * 1000 + 500; // Add 500ms buffer
      await new Promise(resolve => setTimeout(resolve, duration));

      // Stop recording and get stats
      await this.stop();

      return true;
    } catch (error) {
      this.logger.error('ERROR', `Test failed: ${error.message}`);
      return false;
    }
  }

  /**
   * Stop recording and verify sync
   */
  async stop() {
    this.isRunning = false;
    this.voiceService.stopAudio();

    this.logger.log('STOP', 'Animation loop stopped');

    // Stop video recording
    const videoStats = this.videoRecorder.stopRecording();
    this.logger.log('STOP', 'Video recording stopped', videoStats);

    // Check sync
    this.verifySynchronization(videoStats);

    // Export video
    const blob = this.videoRecorder.exportVideo('webm');
    this.downloadVideo(blob, 'phase1-avatar-test.webm');

    return this.getTestResults();
  }

  /**
   * Verify audio-video synchronization
   */
  verifySynchronization(videoStats) {
    const audioDuration = this.voiceService.getDuration() * 1000;
    const videoDuration = videoStats.duration;

    const syncError = Math.abs(audioDuration - videoDuration);
    const tolerance = 50; // milliseconds

    this.logger.log('SYNC', 'Synchronization Check', {
      audioDuration: `${audioDuration.toFixed(0)}ms`,
      videoDuration: `${videoDuration.toFixed(0)}ms`,
      syncError: `${syncError.toFixed(0)}ms`,
      tolerance: `${tolerance}ms`,
      status: syncError <= tolerance ? 'PASS' : 'FAIL',
    });

    if (syncError > tolerance) {
      this.metrics.syncErrors.push({
        error: syncError,
        timestamp: Date.now(),
      });
    }
  }

  /**
   * Download video blob
   */
  downloadVideo(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    this.logger.log('SUCCESS', `Video downloaded: ${filename} (${(blob.size / 1024 / 1024).toFixed(2)}MB)`);
  }

  /**
   * Get test results
   */
  getTestResults() {
    const elapsed = Date.now() - this.metrics.startTime;
    const fps = (this.metrics.framesRendered / (elapsed / 1000)).toFixed(1);

    return {
      success: this.metrics.syncErrors.length === 0,
      metrics: {
        totalTime: `${(elapsed / 1000).toFixed(2)}s`,
        framesRendered: this.metrics.framesRendered,
        fps: fps,
        phonemesAnimated: this.metrics.phonemesAnimated,
        syncErrors: this.metrics.syncErrors.length,
      },
    };
  }

  /**
   * Print test summary
   */
  printSummary() {
    const results = this.getTestResults();

    this.logger.log('SUMMARY', 'Phase 1 Integration Test Results', {
      success: results.success ? 'PASS' : 'FAIL',
      ...results.metrics,
    });

    return results;
  }
}

/**
 * Run Phase 1 integration test
 */
export async function runPhase1Test() {
  const test = new Phase1IntegrationTest();

  // Initialize
  const initialized = await test.initialize();
  if (!initialized) {
    return { success: false, error: 'Initialization failed' };
  }

  // Run synthesis flow
  const success = await test.testSynthesisFlow();

  // Print results
  const results = test.printSummary();

  return results;
}

export { Phase1IntegrationTest };
