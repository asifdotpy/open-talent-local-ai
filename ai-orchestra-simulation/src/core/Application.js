import * as THREE from 'three';
import { SceneManager } from './SceneManager.js';
import { AssetManager } from './AssetManager.js';
import { MeshManager } from './MeshManager.js';
import { AnimationController } from '../animation/AnimationController.js';
import { MorphTargetAnimationController } from '../animation/MorphTargetAnimationController.js';
import { GUIManager } from '../ui/GUIManager.js';
import { MouthSelectionGUI } from '../ui/MouthSelectionGUI.js';
import { AudioVisualization } from '../ui/AudioVisualization.js';
import { PerformanceMonitor } from '../utils/PerformanceMonitor.js';
import { Logger } from '../utils/Logger.js';
import { AppConfig } from '../config/AppConfig.js';
import { DebugManager } from './DebugManager.js';

/**
 * Main application class that orchestrates all components
 */
export class Application {
  constructor(container) {
    this.container = container;
    this.logger = Logger.getInstance();
    this.config = AppConfig.get();
    // Allow selecting model via presets and URL param (?model=face|metahuman|conductor)
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const paramModelKey = urlParams.get('model');
      const presets = this.config.modelPresets || {};
      const defaultKey = this.config.defaultModel;
      if (defaultKey && presets[defaultKey]) {
        this.config.assets.model = presets[defaultKey];
        this.logger.log('INFO', `Using default model preset: ${defaultKey} -> ${this.config.assets.model}`);
      }
      if (paramModelKey && presets[paramModelKey]) {
        this.config.assets.model = presets[paramModelKey];
        this.logger.log('INFO', `Overriding model via URL param: ${paramModelKey} -> ${this.config.assets.model}`);
      }
    } catch (e) {
      // Non-fatal; fall back to configured assets.model
      this.logger.log('WARNING', 'Model preset selection failed, using configured model path', { error: e?.message });
    }
    this.isInitialized = false;
    this.isRunning = false;

    // Core managers (conditionally initialized)
    this.sceneManager = null;
    this.assetManager = null;
    this.meshManager = null;
    this.animationController = null;
    this.guiManager = null;
    this.mouthSelectionGUI = null;
    this.audioVisualization = null;
    this.performanceMonitor = null;
    this.debugManager = null;

    // Animation loop
    this.clock = new THREE.Clock();
    this.animationId = null;

    // Event handlers
    this.onKeyDown = this.onKeyDown.bind(this);

    this.logger.log('INFO', `Application created - Avatar: ${this.config.features.enableAvatar ? 'ENABLED' : 'DISABLED'}`);
  }

  async initialize() {
    if (this.isInitialized) {
      this.logger.log('WARNING', 'Application already initialized');
      return;
    }

    try {
      this.logger.log('INFO', 'Initializing application...');

      // Initialize core managers
      this.assetManager = new AssetManager();
      this.performanceMonitor = new PerformanceMonitor(this.config);
      this.debugManager = new DebugManager(this);

      // Conditionally initialize 3D components
      if (this.config.features.enableAvatar) {
        await this.initializeAvatarComponents();
      } else {
        await this.initializeAudioOnlyComponents();
      }

      // Setup event listeners
      this.setupEventListeners();

      this.isInitialized = true;
      this.logger.log('SUCCESS', `Application initialized (${this.config.features.enableAvatar ? 'with avatar' : 'audio-only mode'})`);
    } catch (error) {
      this.logger.log('ERROR', 'Failed to initialize application', error);
      throw error;
    }
  }

  async initializeAvatarComponents() {
    this.logger.log('INFO', 'Initializing avatar components...');

    // Initialize 3D managers
    this.sceneManager = new SceneManager(this.config);
    this.meshManager = new MeshManager();

    // Initialize scene
    await this.sceneManager.init();
    this.debugManager.initialize();

    // Load assets
    const audioObject = this.sceneManager.getAudio();
    await this.assetManager.loadAllAssets(this.config.assets, audioObject);

    // Initialize mesh manager with loaded assets
    const headMesh = await this.meshManager.initialize({ model: this.assetManager.getAsset('model') });

    // Check if model is too complex and simplify if needed
    const gltfModel = this.assetManager.getAsset('model');
    let modelToAdd = gltfModel;

    if (gltfModel && gltfModel.scene) {
      // Count total vertices in the model
      let totalVertices = 0;
      gltfModel.scene.traverse((child) => {
        if (child.isMesh && child.geometry) {
          totalVertices += child.geometry.attributes.position?.count || 0;
        }
      });

      // If model is too complex (>20k vertices), create a simplified version
      if (totalVertices > 20000) {
        this.logger.log('WARNING', `Model has ${totalVertices} vertices - creating simplified version for better performance`);

        // Create simplified scene
        const simplifiedScene = new THREE.Scene();

        gltfModel.scene.traverse((child) => {
          if (child.isMesh) {
            const simplifiedMesh = this.meshManager.simplifyGeometry(child, 0.03); // Keep only 3% of vertices for extreme performance
            simplifiedScene.add(simplifiedMesh);

            // Update head mesh reference if this was the head mesh
            if (child === headMesh) {
              // Re-initialize mesh manager with simplified mesh
              this.meshManager.headMesh = simplifiedMesh;
              this.meshManager.initializeMouthTracking();
            }
          } else {
            // Copy non-mesh objects (lights, cameras, etc.)
            simplifiedScene.add(child.clone());
          }
        });

        modelToAdd = { scene: simplifiedScene };
        this.logger.log('SUCCESS', 'Model aggressively simplified for better performance');
      }
    }

    // Add the model scene to the main scene for rendering
    if (modelToAdd && modelToAdd.scene) {
      this.sceneManager.getScene().add(modelToAdd.scene);
      this.logger.log('SUCCESS', 'GLTF model added to scene');

      // Optimize materials for better performance
      this.sceneManager.optimizeMaterials();
    }

    // Initialize animation controller - try morph targets first, then vertex-based
    const speechData = this.assetManager.getAsset('speech');

    // Try morph target animation first (better performance and compatibility)
    this.logger.log('INFO', 'Attempting to initialize morph target-based animation...');
    this.animationController = new MorphTargetAnimationController(headMesh, this.config, speechData, audioObject, this.meshManager);
    const morphTargetSuccess = this.animationController.initialize();

    if (!morphTargetSuccess) {
      this.logger.log('WARNING', 'Morph target animation failed - model lacks morph targets for lip-sync');
      this.logger.log('INFO', 'Falling back to vertex-based animation (may cause performance issues)');
      // Fall back to vertex-based animation
      this.animationController = new AnimationController(headMesh, this.config, speechData, audioObject, this.meshManager);
      this.animationController.initialize();
      this.logger.log('INFO', 'Vertex-based animation initialized - expect lower FPS during lip-sync');
      this.logger.log('WARNING', '⚠️  PERFORMANCE WARNING: This model lacks morph targets, causing vertex manipulation');
      this.logger.log('INFO', '💡 TIP: Lip-sync is DISABLED by default. Use GUI toggle to enable when needed');
      this.logger.log('INFO', '🔧 For best results, use a 3D model with facial morph targets (blend shapes)');
    } else {
      this.logger.log('SUCCESS', 'Morph target animation initialized successfully');
    }

    // Initialize GUI
    this.guiManager = new GUIManager({
      animationController: this.animationController,
      performanceMonitor: this.performanceMonitor,
      debugManager: this.debugManager,
    });

    // Initialize mouth selection GUI for advanced vertex detection
    this.mouthSelectionGUI = new MouthSelectionGUI(this.meshManager, this.sceneManager.getScene());

    // Connect HTML audio element to animation controller for reliable playback
    if (this.animationController && this.animationController.setHtmlAudioElement) {
      const htmlAudio = this.sceneManager.getHtmlAudioElement();
      if (htmlAudio) {
        this.animationController.setHtmlAudioElement(htmlAudio);
        // Sync audio file path
        this.sceneManager.syncAudioPlayback(this.config.assets.audio);
        htmlAudio.src = this.config.assets.audio;
        htmlAudio.load();
        this.logger.log('SUCCESS', 'HTML audio element connected to animation controller');
      }
    }

    this.logger.log('SUCCESS', 'Avatar components initialized');
  }

  async initializeAudioOnlyComponents() {
    this.logger.log('INFO', 'Initializing audio-only components...');

    // Create audio visualization container
    const audioVizContainer = document.createElement('div');
    audioVizContainer.id = 'audio-visualization-container';
    audioVizContainer.style.cssText = `
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 10;
      text-align: center;
    `;

    const title = document.createElement('h2');
    title.textContent = 'Audio Interview Mode';
    title.style.cssText = `
      color: #e0e0e0;
      font-family: Arial, sans-serif;
      margin-bottom: 20px;
    `;

    const subtitle = document.createElement('p');
    subtitle.textContent = 'Avatar will be added later - audio analysis active';
    subtitle.style.cssText = `
      color: #a0a0a0;
      font-family: Arial, sans-serif;
      margin-bottom: 30px;
    `;

    audioVizContainer.appendChild(title);
    audioVizContainer.appendChild(subtitle);
    this.container.appendChild(audioVizContainer);

    // Load only audio assets
    await this.assetManager.loadAudioAssets(this.config.assets);

    // Set up HTML audio element for audio-only mode
    const htmlAudio = document.getElementById('speech-audio');
    if (htmlAudio) {
      htmlAudio.src = this.config.assets.audio;
      htmlAudio.load();
      this.logger.log('SUCCESS', 'HTML audio element configured for audio-only mode');
    }

    // Initialize audio visualization
    if (this.config.features.enableAudioVisualization) {
      if (htmlAudio) {
        this.audioVisualization = new AudioVisualization(audioVizContainer, htmlAudio);
        await this.audioVisualization.initialize();
        this.logger.log('SUCCESS', 'Audio visualization initialized');
      }
    }

    // Initialize GUI for audio controls
    this.guiManager = new GUIManager({
      performanceMonitor: this.performanceMonitor,
      debugManager: this.debugManager,
      audioOnly: true,
    });

    this.logger.log('SUCCESS', 'Audio-only components initialized');
  }

  start() {
    if (!this.isInitialized) {
      throw new Error('Application must be initialized before starting');
    }

    if (this.isRunning) {
      this.logger.log('WARNING', 'Application already running');
      return;
    }

    this.isRunning = true;

    // Start audio visualization if in audio-only mode
    if (!this.config.features.enableAvatar && this.audioVisualization) {
      this.audioVisualization.start();

      // Attempt to auto-play audio (will be blocked by browser if no user interaction)
      const htmlAudio = document.getElementById('speech-audio');
      if (htmlAudio) {
        htmlAudio.play().catch(error => {
          this.logger.log('WARNING', 'Auto-play blocked by browser - user must click Play Audio button');
        });
      }
    }

    // Don't auto-start animation - let user control via GUI
    this.animate();

    this.logger.log('INFO', `Application started (${this.config.features.enableAvatar ? 'with avatar' : 'audio-only mode'})`);
  }

  stop() {
    if (!this.isRunning) {
      return;
    }

    this.isRunning = false;

    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }

    // Stop audio visualization
    if (this.audioVisualization) {
      this.audioVisualization.stop();
    }

    // Stop animation controller if it exists
    if (this.animationController) {
      this.animationController.stop();
    }

    this.logger.log('INFO', 'Application stopped');
  }

  animate() {
    if (!this.isRunning) {
      return;
    }

    this.animationId = requestAnimationFrame(() => this.animate());

    const currentTime = performance.now();
    const deltaTime = this.clock.getDelta() * 1000; // Convert to milliseconds

    // Update animation controller only if it's actively playing (avatar mode only)
    if (this.config.features.enableAvatar && this.animationController && this.animationController.getAnimationState().isPlaying) {
      this.animationController.update();
    }

    // Update performance monitor with precise timing
    this.performanceMonitor.update(deltaTime);

    // Update debug manager
    if (this.debugManager) {
      this.debugManager.update();
    }

    // Render scene only in avatar mode
    if (this.config.features.enableAvatar && this.sceneManager) {
      this.sceneManager.render();
    }

    // Update GUI less frequently for performance (every 30 frames instead of 10)
    if (this.guiManager && this.performanceMonitor.frameCount % 30 === 0) {
      this.guiManager.update();
    }
  }

  resize(width, height) {
    if (this.sceneManager) {
      this.sceneManager.resize(width, height);
    }
  }

  setupEventListeners() {
    document.addEventListener('keydown', this.onKeyDown);
    this.logger.log('INFO', 'Event listeners setup');
  }

  onKeyDown(event) {
    switch (event.key.toLowerCase()) {
      case 'm':
        // Toggle mouth helpers visibility
        if (this.mouthSelectionGUI) {
          this.mouthSelectionGUI.toggleHelpers();
        }
        break;
      case 'escape':
        // Emergency stop
        this.stop();
        break;
    }
  }

  dispose() {
    this.stop();

    // Remove event listeners
    document.removeEventListener('keydown', this.onKeyDown);

    // Dispose audio visualization
    if (this.audioVisualization) {
      this.audioVisualization.dispose();
    }

    // Dispose avatar components (only if they exist)
    if (this.mouthSelectionGUI) {
      this.mouthSelectionGUI.dispose();
    }

    if (this.guiManager) {
      this.guiManager.dispose();
    }

    if (this.animationController) {
      this.animationController.dispose();
    }

    if (this.meshManager) {
      this.meshManager.dispose();
    }

    if (this.assetManager) {
      this.assetManager.dispose();
    }

    if (this.sceneManager) {
      this.sceneManager.dispose();
    }

    this.logger.log('INFO', 'Application disposed');
  }
}
