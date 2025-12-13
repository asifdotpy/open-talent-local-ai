/**
 * Avatar Renderer Service
 * Handles 3D avatar creation, rendering, and lip-sync animation
 * Part of Day 5-6 implementation
 */

import * as THREE from 'three';
import gsap from 'gsap';

export enum AvatarGender {
  MALE = 'male',
  FEMALE = 'female',
  NEUTRAL = 'neutral',
}

export enum AvatarSkinTone {
  LIGHT = 'light',
  MEDIUM = 'medium',
  DARK = 'dark',
  VERY_DARK = 'very_dark',
}

export interface AvatarConfig {
  gender: AvatarGender;
  skinTone: AvatarSkinTone;
  name?: string;
  hideIdentity?: boolean;
}

export interface AvatarState {
  isInitialized: boolean;
  isAnimating: boolean;
  currentExpression: 'neutral' | 'speaking' | 'listening';
  mouthOpen: number; // 0-1
}

export interface PhonemeFrame {
  time: number; // ms timestamp
  phoneme: string; // 'a', 'e', 'i', 'o', 'u', etc.
  intensity: number; // 0-1, mouth openness
}

export class AvatarRenderer {
  private scene: THREE.Scene | null = null;
  private camera: THREE.Camera | null = null;
  private renderer: THREE.WebGLRenderer | null = null;
  private canvas: HTMLCanvasElement | null = null;
  private avatar: THREE.Group | null = null;
  private head: THREE.Mesh | null = null;
  private jaw: THREE.Mesh | null = null;
  private leftEye: THREE.Mesh | null = null;
  private rightEye: THREE.Mesh | null = null;
  private state: AvatarState = {
    isInitialized: false,
    isAnimating: false,
    currentExpression: 'neutral',
    mouthOpen: 0,
  };
  private config: AvatarConfig = {
    gender: AvatarGender.NEUTRAL,
    skinTone: AvatarSkinTone.MEDIUM,
  };
  private animationFrameId: number | null = null;
  private phonemeAnimation: gsap.core.Tween | null = null;

  /**
   * Initialize Three.js scene and avatar
   */
  async initialize(config: AvatarConfig): Promise<void> {
    this.config = { ...config };

    // Get or create canvas
    if (!this.canvas) {
      this.canvas = document.createElement('canvas');
      this.canvas.style.width = '100%';
      this.canvas.style.height = '100%';
    }

    // Create scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xf0f0f0);

    // Create camera
    this.camera = new THREE.PerspectiveCamera(
      75,
      this.canvas.clientWidth / this.canvas.clientHeight,
      0.1,
      1000
    );
    this.camera.position.z = 2.5;

    // Create renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
    });
    this.renderer.setSize(
      this.canvas.clientWidth,
      this.canvas.clientHeight,
      false
    );
    this.renderer.setPixelRatio(window.devicePixelRatio);

    // Setup lighting
    this.setupLighting();

    // Create avatar
    this.avatar = new THREE.Group();
    this.scene.add(this.avatar);

    await this.loadAvatarModel(config.gender);

    // Start render loop
    this.startRenderLoop();

    this.state.isInitialized = true;
    console.log('✅ Avatar initialized');
  }

  /**
   * Setup 3-point lighting
   */
  private setupLighting(): void {
    if (!this.scene) return;

    // Key light (main light)
    const keyLight = new THREE.DirectionalLight(0xffffff, 0.8);
    keyLight.position.set(2, 2, 2);
    this.scene.add(keyLight);

    // Fill light (soften shadows)
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
    fillLight.position.set(-2, 1, 1);
    this.scene.add(fillLight);

    // Back light (separation)
    const backLight = new THREE.DirectionalLight(0xffffff, 0.3);
    backLight.position.set(0, -1, -2);
    this.scene.add(backLight);

    // Ambient light (overall illumination)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambientLight);
  }

  /**
   * Load avatar model (geometric shapes for MVP)
   */
  async loadAvatarModel(gender: AvatarGender): Promise<void> {
    if (!this.avatar) return;

    // Clear existing model
    this.avatar.clear();

    const skinColor = this.getSkinColor();

    // Head (sphere)
    const headGeometry = new THREE.SphereGeometry(0.8, 32, 32);
    const headMaterial = new THREE.MeshPhongMaterial({
      color: skinColor,
      shininess: 30,
    });
    this.head = new THREE.Mesh(headGeometry, headMaterial);
    this.head.position.y = 0.2;
    this.avatar.add(this.head);

    // Jaw (box, positioned below head)
    const jawGeometry = new THREE.BoxGeometry(0.7, 0.4, 0.5);
    const jawMaterial = new THREE.MeshPhongMaterial({
      color: skinColor,
      shininess: 30,
    });
    this.jaw = new THREE.Mesh(jawGeometry, jawMaterial);
    this.jaw.position.set(0, -0.4, 0.3);
    this.jaw.castShadow = true;
    this.jaw.receiveShadow = true;
    this.avatar.add(this.jaw);

    // Eyes
    this.createEyes(skinColor);

    // Mouth (simple plane for visual feedback)
    const mouthGeometry = new THREE.PlaneGeometry(0.3, 0.1);
    const mouthMaterial = new THREE.MeshPhongMaterial({
      color: 0xff6b9d,
      emissive: 0xff6b9d,
    });
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
    mouth.position.set(0, -0.6, 0.5);
    this.avatar.add(mouth);

    console.log('✅ Avatar model loaded');
  }

  /**
   * Create eyes for the avatar
   */
  private createEyes(skinColor: number): void {
    if (!this.avatar) return;

    // Eye whites (larger sphere)
    const eyeWhiteGeometry = new THREE.SphereGeometry(0.15, 16, 16);
    const eyeWhiteMaterial = new THREE.MeshPhongMaterial({
      color: 0xffffff,
      shininess: 60,
    });

    // Left eye
    this.leftEye = new THREE.Mesh(eyeWhiteGeometry, eyeWhiteMaterial);
    this.leftEye.position.set(-0.25, 0.7, 0.7);
    this.avatar.add(this.leftEye);

    // Right eye
    this.rightEye = new THREE.Mesh(eyeWhiteGeometry, eyeWhiteMaterial);
    this.rightEye.position.set(0.25, 0.7, 0.7);
    this.avatar.add(this.rightEye);

    // Pupils
    const pupilGeometry = new THREE.SphereGeometry(0.08, 16, 16);
    const pupilMaterial = new THREE.MeshPhongMaterial({
      color: 0x000000,
      shininess: 100,
    });

    const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
    leftPupil.position.set(0, 0, 0.1);
    this.leftEye.add(leftPupil);

    const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
    rightPupil.position.set(0, 0, 0.1);
    this.rightEye.add(rightPupil);
  }

  /**
   * Get skin color based on tone
   */
  private getSkinColor(): number {
    const colors = {
      [AvatarSkinTone.LIGHT]: 0xf4a882,
      [AvatarSkinTone.MEDIUM]: 0xc68642,
      [AvatarSkinTone.DARK]: 0x8b6914,
      [AvatarSkinTone.VERY_DARK]: 0x4a3728,
    };
    return colors[this.config.skinTone] || colors[AvatarSkinTone.MEDIUM];
  }

  /**
   * Play lip-sync animation based on phonemes
   */
  async playLipSyncAnimation(phonemeFrames: PhonemeFrame[]): Promise<void> {
    if (!this.state.isInitialized || !this.jaw) {
      console.error('Avatar not initialized');
      return;
    }

    // Sort frames by time
    const sortedFrames = [...phonemeFrames].sort((a, b) => a.time - b.time);

    // Kill existing animation
    if (this.phonemeAnimation) {
      this.phonemeAnimation.kill();
    }

    this.state.isAnimating = true;
    this.setExpression('speaking');

    // Animate jaw rotation for each phoneme
    for (const frame of sortedFrames) {
      const jawRotation = frame.intensity * 0.5; // Max 0.5 radians (~28 degrees)

      // Use GSAP for smooth animation between phonemes
      await new Promise((resolve) => {
        const startTime = Date.now();
        const duration = frame.intensity === 0 ? 50 : 100; // Quick close, slower open

        const animate = () => {
          const elapsed = Date.now() - startTime;
          const progress = Math.min(elapsed / duration, 1);

          if (this.jaw) {
            this.jaw.rotation.x = gsap.utils.interpolate(0, jawRotation, progress);
          }

          if (progress < 1) {
            requestAnimationFrame(animate);
          } else {
            resolve(undefined);
          }
        };

        animate();
      });
    }

    // Return to neutral expression
    this.setExpression('neutral');
    this.state.isAnimating = false;

    console.log('✅ Lip-sync animation complete');
  }

  /**
   * Change avatar expression
   */
  setExpression(expression: 'neutral' | 'speaking' | 'listening'): void {
    this.state.currentExpression = expression;

    if (!this.head) return;

    switch (expression) {
      case 'speaking':
        // Open mouth slightly during speaking
        this.state.mouthOpen = 0.3;
        break;
      case 'listening':
        // Neutral with slight engagement
        this.state.mouthOpen = 0;
        break;
      case 'neutral':
        this.state.mouthOpen = 0;
        break;
    }
  }

  /**
   * Update avatar appearance (gender, skin tone)
   */
  updateAppearance(config: Partial<AvatarConfig>): void {
    this.config = { ...this.config, ...config };

    if (config.gender || config.skinTone) {
      this.loadAvatarModel(this.config.gender);
    }
  }

  /**
   * Get canvas element for React mounting
   */
  getCanvas(): HTMLCanvasElement {
    if (!this.canvas) {
      this.canvas = document.createElement('canvas');
    }
    return this.canvas;
  }

  /**
   * Get current state
   */
  getState(): AvatarState {
    return { ...this.state };
  }

  /**
   * Start the render loop
   */
  private startRenderLoop(): void {
    const animate = () => {
      this.animationFrameId = requestAnimationFrame(animate);
      this.render();
    };
    animate();
  }

  /**
   * Render the scene
   */
  private render(): void {
    if (!this.renderer || !this.scene || !this.camera) return;

    // Gentle head bobbing animation
    if (this.avatar && this.state.currentExpression === 'listening') {
      this.avatar.position.y = Math.sin(Date.now() * 0.002) * 0.05;
    }

    this.renderer.render(this.scene, this.camera);
  }

  /**
   * Handle window resize
   */
  onWindowResize(): void {
    if (!this.canvas || !this.renderer || !this.camera) return;

    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;

    (this.camera as THREE.PerspectiveCamera).aspect = width / height;
    (this.camera as THREE.PerspectiveCamera).updateProjectionMatrix();

    this.renderer.setSize(width, height, false);
  }

  /**
   * Record animation as video (for demo purposes)
   */
  async recordAnimation(duration: number): Promise<Blob> {
    // This would require additional setup with Canvas.captureStream()
    // For now, return a placeholder
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(new Blob([], { type: 'video/mp4' }));
      }, duration);
    });
  }

  /**
   * Dispose and cleanup
   */
  dispose(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
    }

    if (this.phonemeAnimation) {
      this.phonemeAnimation.kill();
    }

    if (this.renderer) {
      this.renderer.dispose();
    }

    if (this.scene) {
      this.scene.clear();
    }

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.avatar = null;
    this.state.isInitialized = false;

    console.log('✅ Avatar renderer disposed');
  }
}

// Export singleton instance
export const avatarRenderer = new AvatarRenderer();
