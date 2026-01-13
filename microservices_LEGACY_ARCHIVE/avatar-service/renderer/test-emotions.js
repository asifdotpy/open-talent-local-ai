#!/usr/bin/env node

/**
 * test-emotions.js - Test script for emotion system
 * Tests EmotionEngine and ExpressionController functionality
 */

import { EmotionEngine, EmotionStates } from './EmotionEngine.js'
import { ExpressionController } from './ExpressionController.js'

console.log('=== Testing Emotion System ===\n')

// Test 1: EmotionEngine basic functionality
console.log('Test 1: EmotionEngine initialization and state transitions')
const engine = new EmotionEngine({
  transitionDuration: 1000,
  blinkInterval: 3000,
  easing: 'smooth'
})

console.log('Initial emotion:', engine.targetEmotion.name)
console.log('Initial morph weights:', engine.getCurrentMorphWeights())

// Test emotion transition
console.log('\nTransitioning to HAPPY emotion...')
engine.setEmotion(EmotionStates.HAPPY, 500)
console.log('Target emotion:', engine.targetEmotion.name)
console.log('Transition progress:', engine.transitionProgress)

// Simulate time passing
for (let i = 0; i < 5; i++) {
  engine.update(100) // 100ms steps
  console.log(`After ${(i + 1) * 100}ms - Progress: ${(engine.transitionProgress * 100).toFixed(1)}%`)
}

console.log('Final morph weights:', engine.getCurrentMorphWeights())
console.log('\n---\n')

// Test 2: Sentiment to Emotion mapping
console.log('Test 2: Sentiment to Emotion mapping')
const testSentiments = [
  { value: 0.8, context: 'feedback', expected: 'happy' },
  { value: 0.3, context: 'interview', expected: 'professional' },
  { value: -0.3, context: 'interview', expected: 'thoughtful' },
  { value: -0.6, context: 'feedback', expected: 'sad' },
  { value: 0.1, context: 'question', expected: 'thoughtful' }
]

testSentiments.forEach(test => {
  const emotion = EmotionEngine.getEmotionFromSentiment(test.value, test.context)
  console.log(`Sentiment: ${test.value.toFixed(1)}, Context: ${test.context} → Emotion: ${emotion.name} (expected: ${test.expected})`)
})

console.log('\n---\n')

// Test 3: ExpressionController with blending
console.log('Test 3: ExpressionController with phoneme + emotion blending')
const controller = new ExpressionController({
  emotionTransitionDuration: 500,
  lipSyncWeight: 1.0,
  emotionWeight: 0.7,
  idleAnimationEnabled: false // Disable for testing consistency
})

// Set emotion
controller.setEmotion(EmotionStates.PROFESSIONAL)
console.log('Set emotion to PROFESSIONAL')

// Simulate phoneme weights (from lip-sync)
const phonemeWeights = {
  jawOpen: 0.6,
  mouthFunnel: 0.2,
  mouthClose: 0.0,
  mouthSmile: 0.0
}

console.log('\nPhoneme weights (lip-sync):', phonemeWeights)

// Get blended weights
const blendedWeights = controller.getBlendedMorphWeights(phonemeWeights)
console.log('\nBlended morph weights (phoneme + emotion):')
Object.entries(blendedWeights).forEach(([key, value]) => {
  if (value > 0.01) {
    console.log(`  ${key}: ${value.toFixed(3)}`)
  }
})

// Get as array for Three.js
const weightsArray = controller.getBlendedMorphWeightsArray(phonemeWeights)
console.log('\nAs array for Three.js:', weightsArray.map(w => w.toFixed(3)))

console.log('\n---\n')

// Test 4: Emotion analytics
console.log('Test 4: Emotion history and analytics')
const analyticsController = new ExpressionController()

// Simulate emotion changes
const emotionSequence = [
  { emotion: EmotionStates.NEUTRAL, duration: 100 },
  { emotion: EmotionStates.PROFESSIONAL, duration: 200 },
  { emotion: EmotionStates.HAPPY, duration: 150 },
  { emotion: EmotionStates.THOUGHTFUL, duration: 100 },
  { emotion: EmotionStates.PROFESSIONAL, duration: 150 }
]

emotionSequence.forEach(({ emotion, duration }) => {
  analyticsController.setEmotion(emotion)
  analyticsController.update(duration)
})

const analytics = analyticsController.getAnalytics()
console.log('Emotion analytics:')
console.log('  Current emotion:', analytics.currentEmotion)
console.log('  Emotion history length:', analytics.emotionHistory.length)
console.log('  Emotion distribution:', analytics.emotionDistribution)
console.log('  Average intensity:', analytics.averageIntensity.toFixed(2))
console.log('  Blending config:', analytics.blendingConfig)

console.log('\n---\n')

// Test 5: Phase-based emotion adjustment
console.log('Test 5: Conversation phase-based emotion adjustment')
const phases = ['intro', 'main', 'conclusion']
const baseSentiment = 0.5

phases.forEach(phase => {
  const emotion = ExpressionController.getEmotionForPhase(phase, baseSentiment)
  const multiplier = EmotionEngine.getIntensityMultiplier(phase)
  console.log(`Phase: ${phase}, Multiplier: ${multiplier}, Emotion: ${emotion.name}, Adjusted intensity: ${emotion.intensity.toFixed(2)}`)
})

console.log('\n---\n')

// Test 6: Blinking animation
console.log('Test 6: Blinking animation')
const blinkController = new ExpressionController({
  blinkInterval: 500, // Fast for testing
  blinkDuration: 100,
  idleAnimationEnabled: true
})

blinkController.setEmotion(EmotionStates.NEUTRAL)

// Simulate time to trigger blink
for (let t = 0; t < 800; t += 50) {
  blinkController.update(50)
  const weights = blinkController.getBlendedMorphWeights()
  if (t === 500 || t === 550 || t === 600) {
    console.log(`At ${t}ms - eyeWiden: ${weights.eyeWiden.toFixed(3)}, eyeNarrow: ${weights.eyeNarrow.toFixed(3)}`)
  }
}

console.log('\n=== All Tests Completed Successfully ===')
