import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { Logger } from '../utils/Logger.js';

/**
 * Manages asset loading with validation and error handling
 */
export class AssetManager {
  constructor() {
    this.assets = new Map();
    this.loaders = this.createLoaders();
    this.logger = Logger.getInstance();
  }

  createLoaders() {
    const gltfLoader = new GLTFLoader();

    // Setup KTX2 loader for texture support
    const ktx2Loader = new KTX2Loader()
      .setTranscoderPath('https://cdn.jsdelivr.net/npm/three@0.164.0/examples/jsm/libs/basis/')
      .detectSupport(new THREE.WebGLRenderer({ antialias: true }));

    gltfLoader.setKTX2Loader(ktx2Loader);
    gltfLoader.setMeshoptDecoder(MeshoptDecoder);

    return {
      gltf: gltfLoader,
      file: new THREE.FileLoader(),
      audio: new THREE.AudioLoader(),
    };
  }

  async validateAssetPaths(assetPaths) {
    this.logger.log('ASSET', 'Validating asset paths...');

    const validationPromises = Object.entries(assetPaths).map(
      async ([key, path]) => {
        try {
          const response = await fetch(path, { method: 'HEAD' });
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }
          this.logger.log('SUCCESS', `Asset validated: ${key}`, {
            path,
            status: response.status,
          });
          return { key, path, valid: true };
        } catch (error) {
          this.logger.log('ERROR', `Asset validation failed: ${key}`, {
            path,
            error: error.message,
          });
          return { key, path, valid: false, error: error.message };
        }
      }
    );

    const results = await Promise.all(validationPromises);
    const invalidAssets = results.filter((r) => !r.valid);

    if (invalidAssets.length > 0) {
      this.logger.log('ERROR', 'Some assets are not accessible', {
        invalidAssets,
      });
      return false;
    }

    this.logger.log('SUCCESS', 'All asset paths validated successfully');
    return true;
  }

  async loadSpeechData(path) {
    return new Promise((resolve, reject) => {
      this.logger.log('ASSET', `Loading speech data from: ${path}`);

      this.loaders.file.load(
        path,
        (data) => {
          try {
            const speechData = JSON.parse(data);
            this.assets.set('speechData', speechData);
            this.logger.log('SUCCESS', 'Speech data parsed successfully', {
              wordCount: speechData.words?.length,
            });
            resolve(speechData);
          } catch (e) {
            this.logger.log('ERROR', 'Error parsing speech.json:', e);
            reject(e);
          }
        },
        undefined,
        (error) => {
          this.logger.log('ERROR', `Error loading speech.json:`, error);
          reject(error);
        }
      );
    });
  }

  async loadModel(path) {
    return new Promise((resolve, reject) => {
      this.logger.log('ASSET', `Loading GLTF model from: ${path}`);

      this.loaders.gltf.load(
        path,
        (gltf) => {
          this.logger.log('SUCCESS', 'GLTF model loaded successfully');
          this.assets.set('model', gltf);
          resolve(gltf);
        },
        undefined,
        (error) => {
          this.logger.log('ERROR', 'Error loading GLTF model:', error);
          reject(error);
        }
      );
    });
  }

  async loadAudio(path, audioObject) {
    return new Promise((resolve, reject) => {
      this.logger.log('ASSET', `Loading audio from: ${path}`);

      // Check if audioObject is valid
      if (!audioObject) {
        const error = new Error(
          'Audio object is null - ensure AudioListener is properly initialized'
        );
        this.logger.log('ERROR', 'Audio loading failed:', error.message);
        reject(error);
        return;
      }

      this.loaders.audio.load(
        path,
        (buffer) => {
          try {
            this.logger.log(
              'SUCCESS',
              'Audio buffer loaded, setting to audio object'
            );
            audioObject.setBuffer(buffer);
            this.assets.set('audioBuffer', buffer);
            this.logger.log(
              'SUCCESS',
              'Audio loaded and configured successfully'
            );
            resolve(buffer);
          } catch (setBufferError) {
            this.logger.log(
              'ERROR',
              'Error setting audio buffer:',
              setBufferError
            );
            reject(setBufferError);
          }
        },
        (progress) => {
          this.logger.log('ASSET', 'Audio loading progress:', {
            loaded: progress.loaded,
            total: progress.total,
            percentage: Math.round((progress.loaded / progress.total) * 100),
          });
        },
        (error) => {
          const errorMessage =
            error?.message ||
            error?.toString() ||
            'Unknown audio loading error';
          this.logger.log('ERROR', 'Error loading audio:', {
            error: errorMessage,
            path,
            suggestion:
              'Check if audio file exists and server supports audio MIME types',
          });
          reject(new Error(`Audio loading failed: ${errorMessage}`));
        }
      );
    });
  }

  async loadAllAssets(assetPaths, audioObject) {
    try {
      const pathsValid = await this.validateAssetPaths(assetPaths);
      if (!pathsValid) {
        throw new Error(
          'Asset path validation failed - check server setup and file paths'
        );
      }

      const [speechData, model] = await Promise.all([
        this.loadSpeechData(assetPaths.speech),
        this.loadModel(assetPaths.model),
      ]);

      await this.loadAudio(assetPaths.audio, audioObject);

      this.logger.log('SUCCESS', 'All assets loaded successfully');
      return { speechData, model };
    } catch (error) {
      this.logger.log('ERROR', 'Asset loading failed:', error);

      if (
        error.message.includes('404') ||
        error.message.includes('validation failed')
      ) {
        this.logger.log('ERROR', 'Asset loading troubleshooting:', {
          suggestion:
            'Ensure server is running from project root with: python3 -m http.server 8000',
          expectedPaths: assetPaths,
          currentURL: window.location.href,
        });
      }
      throw error;
    }
  }

  async loadAudioAssets(assetPaths) {
    try {
      // Validate only audio-related paths
      const audioPaths = {
        speech: assetPaths.speech,
        audio: assetPaths.audio
      };

      const pathsValid = await this.validateAssetPaths(audioPaths);
      if (!pathsValid) {
        throw new Error('Audio asset path validation failed');
      }

      // In audio-only mode, we only need speech data
      // The HTML audio element will load the audio file directly
      const speechData = await this.loadSpeechData(assetPaths.speech);

      this.logger.log('SUCCESS', 'Audio assets loaded successfully (audio-only mode)');
      return { speechData };
    } catch (error) {
      this.logger.log('ERROR', 'Audio asset loading failed:', error);
      throw error;
    }
  }

  getAsset(key) {
    return this.assets.get(key);
  }

  getAssets() {
    return this.assets;
  }

  hasAsset(key) {
    return this.assets.has(key);
  }

  dispose() {
    this.assets.clear();
  }
}
