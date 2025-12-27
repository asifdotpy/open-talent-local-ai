/**
 * Application configuration with validation
 */
import { developmentConfig } from '../../config/development.config.js'
import { productionConfig } from '../../config/production.config.js'

export class AppConfig {
  static getEnvironment() {
    // Detect environment
    if (process.env.NODE_ENV === 'production') {
      return 'production'
    }
    // Check if we're in a browser environment
    if (typeof window !== 'undefined' && window?.location?.hostname) {
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'development'
      }
    }
    return process.env.NODE_ENV || 'development'
  }
  static DEFAULT_CONFIG = {
    // Feature flags
    features: {
      enableAvatar: true, // Phase 1: Enable real-time avatar rendering
      enableAudioVisualization: true, // Show audio waveform when avatar is disabled
      enableWebRTCStreaming: true, // WebRTC client streaming (browser <-> services) - ENABLED for real-time interviews
      enableVideoRecording: true, // Phase 1: Enable video capture from canvas
      enablePhonemeAnimation: true, // Phase 1: Enable phoneme-based lip-sync
      enableRealTimeSync: true, // Phase 1: Real-time audio-video synchronization
      enableMicrophoneCapture: false, // Phase 1: Disable microphone for lip-sync testing (set to true for full interviews)
    },

    // Model presets for easy switching between different avatars
    modelPresets: {
      face: './renderer/assets/models/face.glb',
      metahuman: './renderer/assets/models/metaHumanHead.glb',
      conductor: './renderer/assets/models/conductor.gltf'
    },
    // Default model key from presets
    defaultModel: 'face',

    // Rendering settings
    scene: {
      backgroundColor: 0x1a233f,
      antialias: true,
    },

    // Camera settings
    camera: {
      fov: 45,
      near: 0.1,
      far: 1000,
      position: { x: 0, y: 1.2, z: 1.8 },
      target: { x: 0, y: 1.0, z: 0 },
    },

    // Animation settings
    animation: {
      mouthDisplacement: 0.1, // Reduced for better performance
      performanceLogInterval: 600, // frames - reduced frequency for better performance
      animationLogInterval: 600, // frames - reduced frequency for better performance
    },

    // Performance thresholds
    performance: {
      minFPS: 20, // Higher threshold for better user experience
      memoryWarningMB: 100,
    },

    // Asset paths
    assets: {
      speech: './assets/audio/speech.json',
      model: './renderer/assets/models/face.glb', // Default; may be overridden by modelPresets/defaultModel or URL param
      audio: './assets/audio/speech.mp3',
    },

    // Signaling configuration (used when enableWebRTCStreaming=true)
    webrtc: {
      signalingUrl: 'ws://localhost:8004/webrtc/signal', // Interview service WS
      iceServers: [
        { urls: ['stun:stun.l.google.com:19302'] }
      ],
    },

    // Model configuration for modular avatar management
    models: {
      face: {
        key: 'face',
        path: './renderer/assets/models/face.glb',
        type: 'morph-target',
        capabilities: ['lip-sync', 'facial-expression'],
        constraints: {
          maxVertices: 5000,
          maxMorphTargets: 52,
          requiredMorphTargets: [
            'jawOpen', 'mouthFunnel', 'mouthClose', 'mouthSmile',
            'mouthPucker', 'mouthRollUpper', 'mouthRollLower',
            'mouthStretch_L', 'mouthStretch_R', 'mouthFrown_L', 'mouthFrown_R',
            'jawForward', 'jawLeft', 'jawRight'
          ] // Expanded for comprehensive phoneme support
        },
        fallback: 'face',
        metadata: {
          name: 'Face.glb (Three.js FaceCap)',
          description: 'Lightweight avatar with full lip-sync support',
          vertexCount: 4368,
          morphTargetCount: 52,
          author: 'Three.js',
          license: 'MIT'
        }
      },
      metahuman: {
        key: 'metahuman',
        path: './assets/models/metaHumanHead.glb',
        type: 'morph-target',
        capabilities: ['lip-sync', 'facial-expression'],
        constraints: {
          maxVertices: 10000,
          maxMorphTargets: 100,
          requiredMorphTargets: ['jawOpen', 'mouthFunnel', 'mouthClose', 'mouthSmile']
        },
        fallback: 'face',
        metadata: {
          name: 'MetaHuman Head',
          description: 'High-quality MetaHuman avatar head',
          vertexCount: 8000,
          morphTargetCount: 100,
          author: 'Epic Games',
          license: 'MetaHuman'
        }
      },
      conductor: {
        key: 'conductor',
        path: './assets/models/conductor.gltf',
        type: 'gltf',
        capabilities: ['animation'],
        constraints: {
          maxVertices: 15000,
          maxMorphTargets: 0,
          requiredMorphTargets: []
        },
        fallback: 'face',
        metadata: {
          name: 'Conductor Avatar',
          description: 'Animated conductor avatar',
          vertexCount: 12000,
          morphTargetCount: 0,
          author: 'OpenTalent',
          license: 'Proprietary'
        }
      }
    },
  };

  static validate(config) {
    const required = ['features', 'scene', 'camera', 'animation', 'performance', 'assets', 'models'];
    const missing = required.filter((key) => !config[key]);

    if (missing.length > 0) {
      throw new Error(`Missing config keys: ${missing.join(', ')}`);
    }

    // Validate nested required properties
    this.validateFeatures(config.features);
    this.validateScene(config.scene);
    this.validateCamera(config.camera);
    this.validateAnimation(config.animation);
    this.validatePerformance(config.performance);
    this.validateAssets(config.assets);
    this.validateModels(config.models);

    return config;
  }

  static validateScene(scene) {
    if (typeof scene.backgroundColor !== 'number') {
      throw new Error('scene.backgroundColor must be a number');
    }
    if (typeof scene.antialias !== 'boolean') {
      throw new Error('scene.antialias must be a boolean');
    }
  }

  static validateCamera(camera) {
    const requiredNumbers = ['fov', 'near', 'far'];
    requiredNumbers.forEach((prop) => {
      if (typeof camera[prop] !== 'number') {
        throw new Error(`camera.${prop} must be a number`);
      }
    });

    const requiredObjects = ['position', 'target'];
    requiredObjects.forEach((prop) => {
      if (!camera[prop] || typeof camera[prop] !== 'object') {
        throw new Error(`camera.${prop} must be an object`);
      }

      ['x', 'y', 'z'].forEach((axis) => {
        if (typeof camera[prop][axis] !== 'number') {
          throw new Error(`camera.${prop}.${axis} must be a number`);
        }
      });
    });
  }

  static validateAnimation(animation) {
    if (typeof animation.mouthDisplacement !== 'number') {
      throw new Error('animation.mouthDisplacement must be a number');
    }
    if (typeof animation.performanceLogInterval !== 'number') {
      throw new Error('animation.performanceLogInterval must be a number');
    }
    if (typeof animation.animationLogInterval !== 'number') {
      throw new Error('animation.animationLogInterval must be a number');
    }
  }

  static validatePerformance(performance) {
    if (typeof performance.minFPS !== 'number') {
      throw new Error('performance.minFPS must be a number');
    }
    if (typeof performance.memoryWarningMB !== 'number') {
      throw new Error('performance.memoryWarningMB must be a number');
    }
  }

  static validateFeatures(features) {
    if (typeof features.enableAvatar !== 'boolean') {
      throw new Error('features.enableAvatar must be a boolean');
    }
    if (typeof features.enableAudioVisualization !== 'boolean') {
      throw new Error('features.enableAudioVisualization must be a boolean');
    }
    if (typeof features.enableWebRTCStreaming !== 'boolean') {
      throw new Error('features.enableWebRTCStreaming must be a boolean');
    }
    if (typeof features.enableVideoRecording !== 'boolean') {
      throw new Error('features.enableVideoRecording must be a boolean');
    }
    if (typeof features.enablePhonemeAnimation !== 'boolean') {
      throw new Error('features.enablePhonemeAnimation must be a boolean');
    }
    if (typeof features.enableRealTimeSync !== 'boolean') {
      throw new Error('features.enableRealTimeSync must be a boolean');
    }
    if (typeof features.enableMicrophoneCapture !== 'boolean') {
      throw new Error('features.enableMicrophoneCapture must be a boolean');
    }
  }

  static validateAssets(assets) {
    const requiredPaths = ['speech', 'model', 'audio'];
    requiredPaths.forEach((path) => {
      if (typeof assets[path] !== 'string') {
        throw new Error(`assets.${path} must be a string`);
      }
    });
  }

  static validateWebRTC(webrtc) {
    if (!webrtc || typeof webrtc !== 'object') return;
    if (typeof webrtc.signalingUrl !== 'string') {
      throw new Error('webrtc.signalingUrl must be a string');
    }
    if (!Array.isArray(webrtc.iceServers)) {
      throw new Error('webrtc.iceServers must be an array');
    }
  }

  static validateModels(models) {
    // Check that we have at least the face model
    if (!models.face || !models.face.key) {
      throw new Error('models.face configuration is required');
    }
    if (!models.face.constraints) {
      throw new Error('models.face.constraints are required');
    }
  }

  static get() {
    const env = this.getEnvironment()
    const envConfig = env === 'production' ? productionConfig : developmentConfig

    const merged = this.deepMerge(this.DEFAULT_CONFIG, envConfig)
    return this.validate(merged)
  }

  static merge(customConfig) {
    const merged = this.deepMerge(this.DEFAULT_CONFIG, customConfig);
    return this.validate(merged);
  }

  static deepMerge(target, source) {
    const result = { ...target };

    for (const key in source) {
      if (
        source[key] &&
        typeof source[key] === 'object' &&
        !Array.isArray(source[key])
      ) {
        result[key] = this.deepMerge(target[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }

    return result;
  }
}
