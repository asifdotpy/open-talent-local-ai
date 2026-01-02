/**
 * Phase 3: AppConfig - Configuration for avatar service integration
 * Provides model and rendering configuration for ThreeJSRenderer
 */

export class AppConfig {
  static get() {
    return {
      models: {
        face: {
          path: '/models/face.glb',
          morphTargets: {
            A: 'A',
            E: 'E',
            I: 'I',
            O: 'O',
            U: 'U',
            a: 'a',
            e: 'e',
            i: 'i',
            o: 'o',
            u: 'u'
          },
          scale: 1.0,
          position: [0, 0, 0],
          rotation: [0, 0, 0]
        },
        production: {
          path: '/models/face.glb',
          morphTargets: {
            A: 'A',
            E: 'E',
            I: 'I',
            O: 'O',
            U: 'U'
          },
          scale: 1.0,
          position: [0, 0, 0],
          rotation: [0, 0, 0]
        }
      },
      rendering: {
        width: 1920,
        height: 1080,
        fps: 30,
        backgroundColor: 0x1a233f,
        lighting: {
          ambient: { intensity: 0.6 },
          directional: {
            intensity: 0.8,
            position: [5, 10, 7.5]
          }
        },
        camera: {
          fov: 35,
          near: 0.1,
          far: 1000,
          position: [0, 1.4, 2.2],
          lookAt: [0, 1.3, 0]
        }
      },
      performance: {
        maxCacheSize: 50,
        cacheTTL: 30 * 60 * 1000, // 30 minutes
        maxWorkers: 4,
        frameBufferPoolSize: 10
      }
    }
  }
}
