export const developmentConfig = {
  models: {
    production: {
      key: 'face',
      // Allow model switching in dev
      allowModelSwitch: true
    },
    development: {
      presets: {
        face: './assets/models/face.glb',
        metahuman: './assets/models/metaHumanHead.glb',
        conductor: './assets/models/conductor.gltf'
      }
    }
  },
  features: {
    enableAvatar: true,
    enableAudioVisualization: true, // Show both in dev
    enableWebRTCStreaming: true,
    enableVideoRecording: true,
    enablePhonemeAnimation: true,
    enableRealTimeSync: true,
  },
  performance: {
    minFPS: 20, // Lower requirement for dev testing
    memoryWarningMB: 100,
  }
}