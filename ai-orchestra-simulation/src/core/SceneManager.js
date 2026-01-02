import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Logger } from '../utils/Logger.js';

/**
 * Manages Three.js scene, camera, renderer, and controls for real-time facial animation
 * Optimized for 60fps performance with proper resource management
 *
 * @class SceneManager
 * @example
 * const config = {
 *   scene: { backgroundColor: 0x000000, antialias: true },
 *   camera: { fov: 75, near: 0.1, far: 1000, position: { x: 0, y: 0, z: 5 } }
 * };
 * const sceneManager = new SceneManager(config);
 * const components = await sceneManager.init();
 */
export class SceneManager {
  constructor(config) {
    this.config = config;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.audioListener = null;
    this.audio = null;
    this.htmlAudioElement = null; // Fallback for playback
    this.isInitialized = false;
    this.eventListeners = new Map();
    this.logger = Logger.getInstance();
  }

  validateConfig() {
    if (!this.config) {
      throw new Error('SceneManager requires a configuration object');
    }

    const required = ['scene', 'camera'];
    for (const key of required) {
      if (!this.config[key]) {
        throw new Error(`Missing required config section: ${key}`);
      }
    }

    // Set defaults for optional configurations
    this.config.lighting = this.config.lighting || {
      keyLight: {
        color: 0xffffff,
        intensity: 2.0,
        position: { x: 1, y: 1, z: 1 },
      },
      ambientLight: { color: 0xffffff, intensity: 1.0 },
    };
  }

  async init() {
    try {
      this.validateConfig();
      this.createScene();
      this.createCamera();
      await this.createRenderer();
      this.createControls();
      this.createLighting();
      this.createAudio();
      this.setupEventListeners();

      this.isInitialized = true;

      return {
        scene: this.scene,
        camera: this.camera,
        renderer: this.renderer,
        controls: this.controls,
        audio: this.audio,
      };
    } catch (error) {
      console.error('SceneManager initialization failed:', error);
      this.dispose();
      throw error;
    }
  }

  createScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(this.config.scene.backgroundColor);

    // Optimize scene for performance
    this.scene.matrixAutoUpdate = false; // Disable auto matrix updates for static scenes
  }

  createCamera() {
    this.camera = new THREE.PerspectiveCamera(
      this.config.camera.fov,
      window.innerWidth / window.innerHeight,
      this.config.camera.near,
      this.config.camera.far
    );

    const pos = this.config.camera.position;
    this.camera.position.set(pos.x, pos.y, pos.z);
  }

  async createRenderer() {
    const rendererConfig = {
      antialias: this.config.scene.antialias,
      powerPreference: 'high-performance',
      alpha: false,
      stencil: false,
      depth: true,
    };

    this.renderer = new THREE.WebGLRenderer(rendererConfig);

    // Validate WebGL context
    const gl = this.renderer.getContext();
    if (!gl) {
      throw new Error('WebGL not supported');
    }

    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1)); // Reduce to 1 for more stable FPS
    this.renderer.setClearColor(0x000000, 0); // Explicit clear color

    // Performance optimizations for real-time rendering
    this.renderer.shadowMap.enabled = false; // Disable shadows for performance
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;

    // Additional performance optimizations for complex models
    this.renderer.capabilities.logarithmicDepthBuffer = false; // Disable for better performance
    this.renderer.sortObjects = false; // Disable object sorting for static scenes

    // Aggressive performance settings for low-end devices
    this.renderer.setPixelRatio(1); // Force 1:1 pixel ratio for maximum performance
    this.renderer.powerPreference = 'low-power'; // Prefer integrated graphics if available

    document.body.appendChild(this.renderer.domElement);
  }

  createControls() {
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    const target = this.config.camera.target;
    this.controls.target.set(target.x, target.y, target.z);
    this.controls.enableDamping = false; // Disable damping for better performance
    this.controls.dampingFactor = 0.05; // Lower damping if re-enabled

    // Enable frustum culling for better performance
    this.scene.frustumCulled = true;
  }

  createLighting() {
    const { keyLight, ambientLight } = this.config.lighting;

    // Simplified lighting for better performance - just ambient light
    const ambient = new THREE.AmbientLight(
      ambientLight.color,
      ambientLight.intensity * 1.5 // Increase ambient to compensate for no directional light
    );
    this.scene.add(ambient);

    // Store references for potential runtime adjustments
    this.lights = {
      ambient: ambient,
    };
  }

  createAudio() {
    this.audioListener = new THREE.AudioListener();
    this.camera.add(this.audioListener);
    this.audio = new THREE.Audio(this.audioListener);
    this.scene.add(this.audio);

    // Setup HTML audio element as fallback for reliable playback
    this.htmlAudioElement = document.getElementById('speech-audio');
    if (!this.htmlAudioElement) {
      // Create it if it doesn't exist
      this.htmlAudioElement = document.createElement('audio');
      this.htmlAudioElement.id = 'speech-audio';
      this.htmlAudioElement.preload = 'auto';
      this.htmlAudioElement.style.display = 'none';
      document.body.appendChild(this.htmlAudioElement);
    }

    this.logger.log('INFO', 'Audio system initialized with THREE.Audio and HTML audio fallback');
  }

  setupEventListeners() {
    // Use bound methods to ensure proper cleanup
    const resizeHandler = this.handleResize.bind(this);
    window.addEventListener('resize', resizeHandler);
    this.eventListeners.set('resize', resizeHandler);

    // Add visibility change handler for performance optimization
    const visibilityHandler = this.handleVisibilityChange.bind(this);
    document.addEventListener('visibilitychange', visibilityHandler);
    this.eventListeners.set('visibilitychange', visibilityHandler);
  }

  handleResize() {
    if (!this.camera || !this.renderer) return;

    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  handleVisibilityChange() {
    // Pause rendering when tab is not visible for performance
    if (document.hidden && this.renderer) {
      this.renderer.setAnimationLoop(null);
    }
  }

  resize(width, height) {
    if (!this.camera || !this.renderer) return;

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  render() {
    if (!this.isInitialized || !this.renderer || !this.scene || !this.camera) {
      return;
    }

    this.controls?.update();
    this.renderer.render(this.scene, this.camera);
  }

  // Utility methods for runtime management
  updateLighting(lightingConfig) {
    if (this.lights && lightingConfig) {
      if (lightingConfig.ambientLight && this.lights.ambient) {
        this.lights.ambient.intensity = lightingConfig.ambientLight.intensity;
        this.lights.ambient.color.setHex(lightingConfig.ambientLight.color);
      }
    }
  }

  getPerformanceInfo() {
    if (!this.renderer) return null;

    return {
      memory: this.renderer.info.memory,
      render: this.renderer.info.render,
      fps: Math.round(1000 / performance.now()), // Approximate
    };
  }

  setRenderTarget(target) {
    if (this.renderer) {
      this.renderer.setRenderTarget(target);
    }
  }

  /**
   * Optimize materials for better performance
   */
  optimizeMaterials() {
    this.scene.traverse((child) => {
      if (child.isMesh && child.material) {
        const material = child.material;

        // Disable expensive material features
        if (material.isMeshStandardMaterial || material.isMeshPhysicalMaterial) {
          material.metalness = 0; // Disable metalness calculations
          material.roughness = 1; // Maximize roughness for simpler lighting
          material.envMapIntensity = 0; // Disable environment mapping
          material.aoMapIntensity = 0; // Disable ambient occlusion
          material.emissiveIntensity = 0; // Disable emissive
          material.clearcoat = 0; // Disable clearcoat
          material.clearcoatRoughness = 0;
          material.transmission = 0; // Disable transmission
          material.thickness = 0;
          material.ior = 1.0; // Reset index of refraction
        }

        // Force flat shading for simpler rendering
        material.flatShading = true;

        // Disable texture filtering for better performance
        if (material.map) {
          material.map.generateMipmaps = false;
          material.map.minFilter = THREE.LinearFilter;
          material.map.magFilter = THREE.LinearFilter;
        }

        if (material.normalMap) {
          material.normalMap.generateMipmaps = false;
          material.normalScale.set(0, 0); // Disable normal mapping
        }

        material.needsUpdate = true;
      }
    });

    this.logger.log('INFO', 'Materials optimized for performance');
  }

  getAudio() {
    return this.audio;
  }

  getHtmlAudioElement() {
    return this.htmlAudioElement;
  }

  /**
   * Sync THREE.Audio playback with HTML audio element
   * HTML audio element provides reliable playback while THREE.Audio provides Web Audio API features
   */
  syncAudioPlayback(audioPath) {
    if (this.htmlAudioElement) {
      this.htmlAudioElement.src = audioPath;
      this.htmlAudioElement.preload = 'auto';
      // Load the audio
      this.htmlAudioElement.load();
      this.logger.log('INFO', 'HTML audio element synced with:', audioPath);
    }
  }

  getScene() {
    return this.scene;
  }

  getCamera() {
    return this.camera;
  }

  getRenderer() {
    return this.renderer;
  }

  dispose() {
    // Clean up event listeners
    this.eventListeners.forEach((handler, event) => {
      if (event === 'resize') {
        window.removeEventListener(event, handler);
      } else {
        document.removeEventListener(event, handler);
      }
    });
    this.eventListeners.clear();

    // Dispose of Three.js resources
    if (this.controls) {
      this.controls.dispose();
      this.controls = null;
    }

    if (this.audio) {
      this.audio.disconnect();
      this.audio = null;
    }

    if (this.audioListener) {
      this.audioListener = null;
    }

    if (this.htmlAudioElement) {
      this.htmlAudioElement.pause();
      this.htmlAudioElement.src = '';
      this.htmlAudioElement = null;
    }

    // Dispose of lights
    if (this.lights) {
      Object.values(this.lights).forEach((light) => {
        if (this.scene && light) {
          this.scene.remove(light);
        }
        if (light.dispose) {
          light.dispose();
        }
      });
      this.lights = null;
    }

    // Dispose of renderer and remove DOM element
    if (this.renderer) {
      this.renderer.setAnimationLoop(null);
      this.renderer.dispose();
      if (this.renderer.domElement.parentNode) {
        this.renderer.domElement.parentNode.removeChild(
          this.renderer.domElement
        );
      }
      this.renderer = null;
    }

    // Clear scene
    if (this.scene) {
      this.scene.clear();
      this.scene = null;
    }

    this.camera = null;
    this.isInitialized = false;
  }
}
