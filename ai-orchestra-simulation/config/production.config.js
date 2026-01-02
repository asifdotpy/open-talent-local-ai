export const productionConfig = {
  models: {
    production: {
      key: 'face',
      // Lock to face.glb in production
      allowModelSwitch: false
    }
  },
  features: {
    enableAvatar: true,
    enableAudioVisualization: false,
    enableWebRTCStreaming: true,
    enableVideoRecording: true,
    enablePhonemeAnimation: true,
    enableRealTimeSync: true,
  },
  performance: {
    minFPS: 30, // Higher requirement for production
    memoryWarningMB: 150,
  }
}
