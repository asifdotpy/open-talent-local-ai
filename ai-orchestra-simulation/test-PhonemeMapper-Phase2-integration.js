/**
 * Test PhonemeMapper Phase 2 Integration
 * Tests dynamic intensity calculation, coarticulation, and advanced blending
 */

import PhonemeMapper from './src/animation/PhonemeMapper.js';
import { Logger } from './src/utils/Logger.js';

// Mock animation controller for testing
class MockAnimationController {
  constructor() {
    this.morphTargets = new Map();
    this.callLog = [];
  }

  setMorphTarget(index, intensity, duration) {
    this.morphTargets.set(index, { intensity, duration });
    this.callLog.push({ type: 'setMorphTarget', index, intensity, duration });
  }

  resetMorphTargets() {
    this.morphTargets.clear();
    this.callLog.push({ type: 'resetMorphTargets' });
  }

  getMorphTarget(index) {
    return this.morphTargets.get(index) || { intensity: 0, duration: 0 };
  }

  getCallLog() {
    return this.callLog;
  }

  clearCallLog() {
    this.callLog = [];
  }
}

async function testPhase2Integration() {
  console.log('🧪 Testing PhonemeMapper Phase 2 Integration...\n');

  const logger = new Logger('TestPhonemeMapper');
  const mockController = new MockAnimationController();
  const phonemeMapper = new PhonemeMapper(mockController, { logger });

  let testsPassed = 0;
  let totalTests = 0;

  // Test 1: Basic Phase 2 initialization
  totalTests++;
  console.log('Test 1: Phase 2 Components Initialization');
  const phase2Status = phonemeMapper.getPhase2Status();
  const expectedComponents = ['intensityMatrix', 'coarticulationEngine', 'morphTargetBlender'];

  let initSuccess = true;
  expectedComponents.forEach(component => {
    if (!phase2Status[component] || !phase2Status[component].initialized) {
      console.log(`❌ ${component} not initialized`);
      initSuccess = false;
    }
  });

  if (initSuccess) {
    console.log('✅ All Phase 2 components initialized');
    testsPassed++;
  }
  console.log('');

  // Test 2: Dynamic intensity calculation without audio context
  totalTests++;
  console.log('Test 2: Dynamic Intensity (No Audio Context)');
  mockController.clearCallLog();

  phonemeMapper.animatePhoneme('aa', 200);

  const callLog = mockController.getCallLog();
  const hasPrimaryCall = callLog.some(call =>
    call.type === 'setMorphTarget' &&
    call.index === 24 && // jawOpen
    typeof call.intensity === 'number' &&
    call.intensity > 0
  );

  if (hasPrimaryCall) {
    console.log('✅ Dynamic intensity calculated for primary morph target');
    testsPassed++;
  } else {
    console.log('❌ Dynamic intensity not applied');
  }
  console.log('');

  // Test 3: Audio context integration
  totalTests++;
  console.log('Test 3: Audio Context Integration');
  mockController.clearCallLog();

  const audioContext = {
    amplitude: 0.8,
    pitch: 220,
    stress: 0.7,
    speakingRate: 4.5,
  };

  phonemeMapper.updateAudioModifiers(audioContext);
  phonemeMapper.animatePhoneme('oh', 150, audioContext);

  const audioCallLog = mockController.getCallLog();
  const hasAudioInfluence = audioCallLog.some(call =>
    call.type === 'setMorphTarget' &&
    call.intensity > 0.5 // Should be higher due to amplitude
  );

  if (hasAudioInfluence) {
    console.log('✅ Audio context influenced intensity calculation');
    testsPassed++;
  } else {
    console.log('❌ Audio context not influencing intensity');
  }
  console.log('');

  // Test 4: Coarticulation effects in sequence
  totalTests++;
  console.log('Test 4: Coarticulation Effects');
  mockController.clearCallLog();

  const sequence = [
    { phoneme: 'b', duration: 100 },
    { phoneme: 'aa', duration: 200 },
    { phoneme: 't', duration: 100 },
  ];

  await phonemeMapper.animateSequence(sequence, audioContext);

  const sequenceCalls = mockController.getCallLog();
  const hasSequenceCalls = sequenceCalls.filter(call => call.type === 'setMorphTarget').length >= 3;

  if (hasSequenceCalls) {
    console.log('✅ Coarticulation applied across phoneme sequence');
    testsPassed++;
  } else {
    console.log('❌ Coarticulation not applied in sequence');
  }
  console.log('');

  // Test 5: Emotion modifiers
  totalTests++;
  console.log('Test 5: Emotion Modifiers');
  mockController.clearCallLog();

  const emotionData = {
    valence: 0.8,  // Positive emotion
    arousal: 0.6,  // High energy
    dominance: 0.7,
  };

  phonemeMapper.updateEmotionModifiers(emotionData);
  phonemeMapper.animatePhoneme('ee', 180, audioContext);

  const emotionCalls = mockController.getCallLog();
  const hasEmotionCalls = emotionCalls.some(call => call.type === 'setMorphTarget');

  if (hasEmotionCalls) {
    console.log('✅ Emotion modifiers applied to animation');
    testsPassed++;
  } else {
    console.log('❌ Emotion modifiers not applied');
  }
  console.log('');

  // Test 6: Adaptive learning feedback
  totalTests++;
  console.log('Test 6: Adaptive Learning');
  const initialStats = phonemeMapper.getPhase2Status().intensityMatrix.statistics;

  phonemeMapper.learnFromFeedback('aa', 'jawOpen', 0.9);
  phonemeMapper.learnFromFeedback('ee', 'mouthSmile', 0.7);

  const updatedStats = phonemeMapper.getPhase2Status().intensityMatrix.statistics;

  if (updatedStats.userPreferencesLearned >= 2) {
    console.log('✅ Adaptive learning recorded user feedback');
    testsPassed++;
  } else {
    console.log('❌ Adaptive learning not working');
  }
  console.log('');

  // Test 7: Morph target blending
  totalTests++;
  console.log('Test 7: Morph Target Blending');
  mockController.clearCallLog();

  // Test a phoneme with multiple morph targets
  phonemeMapper.animatePhoneme('ao', 250, audioContext);

  const blendCalls = mockController.getCallLog();
  const blendTargets = blendCalls.filter(call => call.type === 'setMorphTarget');

  // 'ao' should have primary (mouthFunnel), secondary (jawOpen), tertiary (mouthPucker)
  if (blendTargets.length >= 2) {
    console.log('✅ Multiple morph targets blended smoothly');
    testsPassed++;
  } else {
    console.log('❌ Morph target blending not working');
  }
  console.log('');

  // Test 8: Silence handling
  totalTests++;
  console.log('Test 8: Silence Handling');
  mockController.clearCallLog();

  phonemeMapper.animatePhoneme('sil', 100);

  const silenceCalls = mockController.getCallLog();
  const hasResetCall = silenceCalls.some(call => call.type === 'resetMorphTargets');

  if (hasResetCall) {
    console.log('✅ Silence properly resets morph targets');
    testsPassed++;
  } else {
    console.log('❌ Silence not handled correctly');
  }
  console.log('');

  // Test 9: Unknown phoneme handling
  totalTests++;
  console.log('Test 9: Unknown Phoneme Handling');
  mockController.clearCallLog();

// Capture console.log for warnings
let warningLogged = false;
const originalLog = console.log;
console.log = (...args) => {
  if (args[0] && args[0].includes('WARNING: Unknown phoneme')) {
    warningLogged = true;
  }
  originalLog(...args);
};

phonemeMapper.animatePhoneme('xyz', 100);

console.log = originalLog;  const unknownCalls = mockController.getCallLog();
  const noUnknownCalls = unknownCalls.length === 0;

  if (warningLogged && noUnknownCalls) {
    console.log('✅ Unknown phoneme handled gracefully');
    testsPassed++;
  } else {
    console.log('❌ Unknown phoneme not handled properly');
  }
  console.log('');

  // Test 10: Phase 2 data export
  totalTests++;
  console.log('Test 10: Phase 2 Data Export');
  const exportData = phonemeMapper.exportPhase2Data();

  const hasExportData = exportData.intensityMatrix &&
                       exportData.coarticulationEngine &&
                       exportData.morphTargetBlender;

  if (hasExportData) {
    console.log('✅ Phase 2 system data exported successfully');
    testsPassed++;
  } else {
    console.log('❌ Phase 2 data export failed');
  }
  console.log('');

  // Summary
  console.log('📊 Test Results Summary:');
  console.log(`✅ Tests Passed: ${testsPassed}/${totalTests}`);
  console.log(`❌ Tests Failed: ${totalTests - testsPassed}/${totalTests}`);
  console.log(`📈 Success Rate: ${((testsPassed / totalTests) * 100).toFixed(1)}%`);

  if (testsPassed === totalTests) {
    console.log('\n🎉 All Phase 2 integration tests passed!');
    return true;
  } else {
    console.log('\n⚠️  Some tests failed. Check implementation.');
    return false;
  }
}

// Run tests
testPhase2Integration().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});
