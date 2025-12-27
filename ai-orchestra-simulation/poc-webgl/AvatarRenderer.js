/**
 * OpenTalent Avatar Renderer - WebGL/Three.js Implementation
 *
 * Handles real-time 3D avatar rendering with lip-sync
 * Includes fallback for browsers without WebGL 2.0 support
 *
 * @author OpenTalent Platform
 * @date November 14, 2025
 */

import * as THREE from 'three';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

/**
 * Main Avatar Renderer (WebGL 2.0)
 */
export class AvatarRenderer {
  constructor(containerElement) {
    this.container = containerElement;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.avatar = null;
    this.faceMesh = null;
    this.isAnimating = false;
    this.currentAudio = null;

    // Performance tracking
    this.fps = 0;
    this.frameCount = 0;
    this.lastTime = performance.now();

    this.init();
  }

  init() {
    // Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xf5f5f5);

    // Camera (portrait mode, focused on head/shoulders)
    this.camera = new THREE.PerspectiveCamera(
      35,  // FOV (narrow for professional look)
      this.container.clientWidth / this.container.clientHeight,
      0.1,
      1000
    );
    this.camera.position.set(0, 1.5, 2.5);
    this.camera.lookAt(0, 1.5, 0);

    // Renderer with high-quality settings
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
      powerPreference: 'high-performance'
    });

    this.renderer.setSize(
      this.container.clientWidth,
      this.container.clientHeight
    );
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.container.appendChild(this.renderer.domElement);

    // Lighting (professional interview setup)
    this.setupLighting();

    // Start render loop
    this.animate();

    console.log('✅ Three.js renderer initialized');
  }

  setupLighting() {
    // Key light (main light from front-right)
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
    keyLight.position.set(2, 3, 3);
    keyLight.castShadow = true;
    this.scene.add(keyLight);

    // Fill light (soften shadows from left)
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
    fillLight.position.set(-2, 2, 2);
    this.scene.add(fillLight);

    // Back light (rim lighting for depth)
    const backLight = new THREE.DirectionalLight(0xffffff, 0.3);
    backLight.position.set(0, 2, -3);
    this.scene.add(backLight);

    // Ambient light (general illumination)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambientLight);
  }

  async loadAvatar(modelPath) {
    console.log('📥 Loading avatar model:', modelPath);

    // Setup Draco compression loader (reduces file size by 80%)
    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderPath('/draco/');

    const gltfLoader = new GLTFLoader();
    gltfLoader.setDRACOLoader(dracoLoader);

    try {
      const gltf = await gltfLoader.loadAsync(modelPath);

      this.avatar = gltf.scene;
      this.scene.add(this.avatar);

      // Find mesh with facial morph targets
      this.findFaceMesh();

      console.log('✅ Avatar loaded successfully');
      console.log('📊 Available morph targets:',
        Object.keys(this.faceMesh?.morphTargetDictionary || {})
      );

      return true;
    } catch (error) {
      console.error('❌ Failed to load avatar:', error);
      throw error;
    }
  }

  findFaceMesh() {
    this.avatar.traverse((node) => {
      if (node.isMesh && node.morphTargetDictionary) {
        // Look for face mesh (usually has viseme morphs)
        const morphTargets = Object.keys(node.morphTargetDictionary);
        if (morphTargets.some(m => m.toLowerCase().includes('viseme'))) {
          console.log('✅ Found face mesh:', node.name);
          this.faceMesh = node;
        }
      }
    });

    if (!this.faceMesh) {
      console.warn('⚠️ No face mesh with morph targets found');
    }
  }

  playLipSync(audioBase64, phonemes) {
    console.log('🎤 Starting lip-sync playback');
    console.log('📊 Phonemes:', phonemes.length);

    // Stop any existing audio
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }

    // Create audio element
    const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
    this.currentAudio = audio;

    // Setup lip-sync animation
    audio.addEventListener('play', () => {
      console.log('▶️ Audio playing');
      this.isAnimating = true;
      this.animateLipSync(audio, phonemes);
    });

    audio.addEventListener('ended', () => {
      console.log('⏹️ Audio ended');
      this.isAnimating = false;
      this.resetMouth();
    });

    audio.addEventListener('error', (e) => {
      console.error('❌ Audio error:', e);
      this.isAnimating = false;
    });

    // Start playback
    audio.play().catch(err => {
      console.error('❌ Play failed (user interaction required):', err);
    });
  }

  animateLipSync(audio, phonemes) {
    if (!this.isAnimating || !this.faceMesh) return;

    // CRITICAL: Sync to audio.currentTime, NOT wall clock
    const currentTime = audio.currentTime;

    // Find current phoneme
    const currentPhoneme = phonemes.find(p =>
      currentTime >= p.start && currentTime < p.end
    );

    if (currentPhoneme) {
      // Map phoneme to viseme and apply
      const viseme = this.phonemeToViseme(currentPhoneme.phoneme);
      this.applyViseme(viseme, currentPhoneme);
    } else {
      // Between phonemes - neutral mouth
      this.applyViseme('viseme_sil');
    }

    // Continue animation
    requestAnimationFrame(() => this.animateLipSync(audio, phonemes));
  }

  phonemeToViseme(phoneme) {
    // Standard phoneme-to-viseme mapping (compatible with Ready Player Me)
    const mapping = {
      // Silence
      'sil': 'viseme_sil',

      // Vowels
      'AA': 'viseme_aa',  // "father"
      'AE': 'viseme_aa',  // "cat"
      'AH': 'viseme_aa',  // "but"
      'AO': 'viseme_O',   // "caught"
      'AW': 'viseme_O',   // "cow"
      'AY': 'viseme_aa',  // "hide"
      'EH': 'viseme_E',   // "red"
      'ER': 'viseme_E',   // "her"
      'EY': 'viseme_E',   // "ate"
      'IH': 'viseme_I',   // "it"
      'IY': 'viseme_I',   // "feet"
      'OW': 'viseme_O',   // "go"
      'OY': 'viseme_O',   // "boy"
      'UH': 'viseme_U',   // "book"
      'UW': 'viseme_U',   // "boot"

      // Consonants - Bilabials (lips together)
      'B': 'viseme_PP',   // "bat"
      'P': 'viseme_PP',   // "pat"
      'M': 'viseme_PP',   // "mat"

      // Consonants - Labiodentals (lip to teeth)
      'F': 'viseme_FF',   // "fat"
      'V': 'viseme_FF',   // "vat"

      // Consonants - Dental (tongue to teeth)
      'TH': 'viseme_TH',  // "thin"
      'DH': 'viseme_TH',  // "this"

      // Consonants - Alveolar (tongue to ridge)
      'T': 'viseme_DD',   // "top"
      'D': 'viseme_DD',   // "dog"
      'N': 'viseme_DD',   // "no"
      'L': 'viseme_DD',   // "let"
      'S': 'viseme_SS',   // "sit"
      'Z': 'viseme_SS',   // "zoo"

      // Consonants - Postalveolar
      'SH': 'viseme_CH',  // "she"
      'ZH': 'viseme_CH',  // "measure"
      'CH': 'viseme_CH',  // "church"
      'JH': 'viseme_CH',  // "judge"

      // Consonants - Velar (back of mouth)
      'K': 'viseme_kk',   // "cat"
      'G': 'viseme_kk',   // "go"
      'NG': 'viseme_nn',  // "sing"

      // Consonants - Glottal/Rhotic
      'HH': 'viseme_sil', // "hat"
      'R': 'viseme_RR',   // "red"
      'W': 'viseme_O',    // "wet"
      'Y': 'viseme_I',    // "yes"
    };

    return mapping[phoneme.toUpperCase()] || 'viseme_sil';
  }

  applyViseme(visemeName, phoneme = null) {
    if (!this.faceMesh) return;

    // Smooth transition (blend between visemes)
    const transitionSpeed = 0.3;

    // Reset all viseme influences towards 0
    Object.keys(this.faceMesh.morphTargetDictionary).forEach(key => {
      if (key.startsWith('viseme_')) {
        const index = this.faceMesh.morphTargetDictionary[key];
        const current = this.faceMesh.morphTargetInfluences[index];
        this.faceMesh.morphTargetInfluences[index] =
          current * (1 - transitionSpeed);
      }
    });

    // Set target viseme
    const index = this.faceMesh.morphTargetDictionary[visemeName];
    if (index !== undefined) {
      const current = this.faceMesh.morphTargetInfluences[index];
      this.faceMesh.morphTargetInfluences[index] =
        current + (1.0 - current) * transitionSpeed;
    }
  }

  resetMouth() {
    if (!this.faceMesh) return;

    // Smoothly return to neutral expression
    Object.keys(this.faceMesh.morphTargetDictionary).forEach(key => {
      if (key.startsWith('viseme_')) {
        const index = this.faceMesh.morphTargetDictionary[key];
        this.faceMesh.morphTargetInfluences[index] = 0;
      }
    });
  }

  animate = () => {
    // FPS tracking
    this.frameCount++;
    const currentTime = performance.now();
    if (currentTime - this.lastTime >= 1000) {
      this.fps = this.frameCount;
      this.frameCount = 0;
      this.lastTime = currentTime;

      // Log FPS every second (remove in production)
      if (this.fps < 30) {
        console.warn('⚠️ Low FPS detected:', this.fps);
      }
    }

    // Render scene
    this.renderer.render(this.scene, this.camera);

    // Continue loop
    requestAnimationFrame(this.animate);
  };

  getFPS() {
    return this.fps;
  }

  dispose() {
    // Cleanup resources
    if (this.currentAudio) {
      this.currentAudio.pause();
    }

    if (this.renderer) {
      this.renderer.dispose();
    }

    if (this.scene) {
      this.scene.traverse((object) => {
        if (object.geometry) {
          object.geometry.dispose();
        }
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach(material => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      });
    }

    console.log('🧹 Renderer disposed');
  }
}

/**
 * Fallback Renderer (for browsers without WebGL 2.0)
 * Uses Canvas 2D for audio visualization
 */
export class AudioVisualizationFallback {
  constructor(containerElement) {
    this.container = containerElement;
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.audioContext = null;
    this.analyser = null;
    this.isAnimating = false;

    // Setup canvas
    this.canvas.width = 1280;
    this.canvas.height = 720;
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.container.appendChild(this.canvas);

    // Create caption container
    this.captionDiv = document.createElement('div');
    this.captionDiv.style.cssText = `
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 24px;
      max-width: 80%;
      text-align: center;
      font-family: Arial, sans-serif;
    `;
    this.container.style.position = 'relative';
    this.container.appendChild(this.captionDiv);

    console.log('✅ Fallback renderer initialized (Canvas 2D + Audio Visualization)');
  }

  async loadAvatar(modelPath) {
    // Load static avatar image instead of 3D model
    const img = new Image();
    img.crossOrigin = 'anonymous';

    // Convert GLB path to PNG (assume we have static images)
    const imagePath = modelPath.replace('.glb', '.png');

    return new Promise((resolve, reject) => {
      img.onload = () => {
        this.avatarImage = img;
        this.drawStaticAvatar();
        console.log('✅ Static avatar image loaded');
        resolve(true);
      };

      img.onerror = () => {
        console.warn('⚠️ Avatar image not found, using placeholder');
        this.avatarImage = null;
        this.drawPlaceholder();
        resolve(true); // Don't reject - continue with placeholder
      };

      img.src = imagePath;
    });
  }

  drawStaticAvatar() {
    if (this.avatarImage) {
      // Center avatar image
      const x = (this.canvas.width - 640) / 2;
      const y = (this.canvas.height - 480) / 2 - 60;
      this.ctx.drawImage(this.avatarImage, x, y, 640, 480);
    }
  }

  drawPlaceholder() {
    // Draw simple placeholder
    this.ctx.fillStyle = '#f5f5f5';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    this.ctx.fillStyle = '#333';
    this.ctx.font = '48px Arial';
    this.ctx.textAlign = 'center';
    this.ctx.fillText('OpenTalent Interview', this.canvas.width / 2, 200);

    this.ctx.font = '24px Arial';
    this.ctx.fillText('Audio-only mode', this.canvas.width / 2, 250);
  }

  playLipSync(audioBase64, phonemes) {
    console.log('🎤 Starting audio playback (fallback mode)');

    // Initialize audio context (must be done after user interaction)
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      this.bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(this.bufferLength);
    }

    // Create audio element
    const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);

    // Connect to analyser for visualization
    const source = this.audioContext.createMediaElementSource(audio);
    source.connect(this.analyser);
    this.analyser.connect(this.audioContext.destination);

    // Play audio
    audio.play();

    // Start visualization
    this.isAnimating = true;
    this.animateWaveform(audio);

    // Show captions
    this.showCaptions(phonemes);

    // Stop animation when done
    audio.addEventListener('ended', () => {
      this.isAnimating = false;
      this.captionDiv.textContent = '';
    });
  }

  animateWaveform(audio) {
    if (!this.isAnimating) return;

    // Clear and redraw avatar
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    if (this.avatarImage) {
      this.drawStaticAvatar();
    } else {
      this.drawPlaceholder();
    }

    // Get frequency data
    this.analyser.getByteFrequencyData(this.dataArray);

    // Draw waveform visualization at bottom
    const barWidth = (this.canvas.width / this.bufferLength) * 2.5;
    let x = 0;

    for (let i = 0; i < this.bufferLength; i++) {
      const barHeight = (this.dataArray[i] / 255) * 100;

      // Gradient color
      const hue = (i / this.bufferLength) * 360;
      this.ctx.fillStyle = `hsl(${hue}, 70%, 50%)`;
      this.ctx.fillRect(x, this.canvas.height - barHeight, barWidth, barHeight);

      x += barWidth + 1;
    }

    // Continue animation
    requestAnimationFrame(() => this.animateWaveform(audio));
  }

  showCaptions(phonemes) {
    // Show phoneme-based captions (accessibility feature)
    // In production, this would reconstruct the original text
    this.captionDiv.textContent = 'Audio playing...';

    // Could implement real-time phoneme display here
    // For now, just indicate audio is playing
  }

  dispose() {
    this.isAnimating = false;
    if (this.audioContext) {
      this.audioContext.close();
    }
    console.log('🧹 Fallback renderer disposed');
  }
}

/**
 * Factory function to create appropriate renderer based on browser capabilities
 */
export function createAvatarRenderer(containerElement) {
  // Test for WebGL 2.0 support
  const canvas = document.createElement('canvas');
  const gl2 = canvas.getContext('webgl2');

  if (gl2) {
    console.log('✅ WebGL 2.0 detected - Using Three.js renderer');
    return new AvatarRenderer(containerElement);
  }

  // Test for WebGL 1.0 support
  const gl1 = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

  if (gl1) {
    console.log('⚠️ Only WebGL 1.0 available - Using fallback renderer');
    // Could implement a WebGL 1.0 renderer here
    // For now, use audio visualization
    return new AudioVisualizationFallback(containerElement);
  }

  // No WebGL at all - use fallback
  console.log('⚠️ No WebGL support - Using audio visualization fallback');
  return new AudioVisualizationFallback(containerElement);
}
