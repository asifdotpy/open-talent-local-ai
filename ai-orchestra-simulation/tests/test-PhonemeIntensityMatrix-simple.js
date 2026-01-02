/**
 * Simple test runner for PhonemeIntensityMatrix
 * Runs basic validation tests without Jest dependencies
 */

import { PhonemeIntensityMatrix } from '../src/animation/PhonemeIntensityMatrix.js';

console.log('🧪 Testing PhonemeIntensityMatrix...\n');

// Test 1: Initialization
console.log('Test 1: Initialization');
try {
  const matrix = new PhonemeIntensityMatrix();
  const stats = matrix.getStatistics();

  console.log('✅ Matrix initialized successfully');
  console.log(`   - Phonemes: ${stats.phonemes}`);
  console.log(`   - Morph targets: ${stats.morphTargets}`);
  console.log(`   - Total mappings: ${stats.totalMappings}`);
  console.log(`   - Active mappings: ${stats.activeMappings}`);
} catch (error) {
  console.log('❌ Initialization failed:', error.message);
}

// Test 2: Base intensity calculation
console.log('\nTest 2: Base intensity calculation');
try {
  const matrix = new PhonemeIntensityMatrix();

  const aaJaw = matrix.baseIntensityMatrix['aa']['jawOpen'];
  const eeJaw = matrix.baseIntensityMatrix['ee']['jawOpen'];

  if (aaJaw > eeJaw) {
    console.log('✅ Vowel jaw opening intensities correct');
  } else {
    console.log('❌ Vowel jaw opening intensities incorrect');
  }

  const mClose = matrix.baseIntensityMatrix['m']['mouthClose'];
  const fClose = matrix.baseIntensityMatrix['f']['mouthClose'];

  if (mClose > fClose) {
    console.log('✅ Consonant lip compression intensities correct');
  } else {
    console.log('❌ Consonant lip compression intensities incorrect');
  }
} catch (error) {
  console.log('❌ Base intensity calculation failed:', error.message);
}

// Test 3: Audio modifiers
console.log('\nTest 3: Audio modifiers');
try {
  const matrix = new PhonemeIntensityMatrix();

  matrix.updateAudioModifiers({
    amplitude: 0.8,
    pitch: 250,
    stress: 0.9,
    speakingRate: 5.0
  });

  if (matrix.audioModifiers.amplitude > 1.0) {
    console.log('✅ Audio amplitude modifier applied');
  } else {
    console.log('❌ Audio amplitude modifier failed');
  }

  if (matrix.audioModifiers.pitch > 0.8) {
    console.log('✅ Audio pitch modifier applied');
  } else {
    console.log('❌ Audio pitch modifier failed');
  }
} catch (error) {
  console.log('❌ Audio modifiers test failed:', error.message);
}

// Test 4: Emotion modifiers
console.log('\nTest 4: Emotion modifiers');
try {
  const matrix = new PhonemeIntensityMatrix();

  matrix.updateEmotionModifiers({
    valence: 0.8,
    arousal: 0.7,
    dominance: 0.6
  });

  if (matrix.emotionModifiers.valence === 0.8) {
    console.log('✅ Emotion valence modifier applied');
  } else {
    console.log('❌ Emotion valence modifier failed');
  }

  const smileFactor = matrix.calculateEmotionFactor('mouthSmile');
  if (smileFactor > 0) {
    console.log('✅ Emotion factor calculation working');
  } else {
    console.log('❌ Emotion factor calculation failed');
  }
} catch (error) {
  console.log('❌ Emotion modifiers test failed:', error.message);
}

// Test 5: Dynamic intensity calculation
console.log('\nTest 5: Dynamic intensity calculation');
try {
  const matrix = new PhonemeIntensityMatrix();

  // Set up modifiers
  matrix.updateAudioModifiers({ amplitude: 0.8 });
  matrix.updateEmotionModifiers({ valence: 1.0 });

  const baseIntensity = matrix.baseIntensityMatrix['aa']['jawOpen'];
  const dynamicIntensity = matrix.calculateDynamicIntensity('aa', 'jawOpen');

  if (dynamicIntensity > baseIntensity) {
    console.log('✅ Dynamic intensity calculation working');
    console.log(`   - Base: ${baseIntensity.toFixed(3)}, Dynamic: ${dynamicIntensity.toFixed(3)}`);
  } else {
    console.log('❌ Dynamic intensity calculation failed');
  }

  // Test coarticulation
  const context = { previousPhoneme: 'b' };
  const coarticulatedIntensity = matrix.calculateDynamicIntensity('aa', 'mouthClose', context);

  if (coarticulatedIntensity < matrix.baseIntensityMatrix['aa']['mouthClose']) {
    console.log('✅ Coarticulation effects applied');
  } else {
    console.log('❌ Coarticulation effects failed');
  }
} catch (error) {
  console.log('❌ Dynamic intensity calculation failed:', error.message);
}

// Test 6: Intensity profile generation
console.log('\nTest 6: Intensity profile generation');
try {
  const matrix = new PhonemeIntensityMatrix();
  const phonemeSequence = ['aa', 'b', 'ee', 's'];

  const profile = matrix.getIntensityProfile(phonemeSequence);

  if (profile.length === 4) {
    console.log('✅ Intensity profile generated');
    console.log(`   - Profile length: ${profile.length}`);
    console.log(`   - First phoneme: ${profile[0].phoneme}`);
    console.log(`   - Context includes previous/next: ${profile[1].context.previousPhoneme !== undefined}`);
  } else {
    console.log('❌ Intensity profile generation failed');
  }
} catch (error) {
  console.log('❌ Intensity profile generation failed:', error.message);
}

// Test 7: Adaptive learning
console.log('\nTest 7: Adaptive learning');
try {
  const matrix = new PhonemeIntensityMatrix();

  const initialMultiplier = matrix.getUserPreferenceMultiplier('aa', 'jawOpen');
  matrix.learnFromFeedback('aa', 'jawOpen', 1.5);
  const updatedMultiplier = matrix.getUserPreferenceMultiplier('aa', 'jawOpen');

  if (updatedMultiplier > initialMultiplier) {
    console.log('✅ Adaptive learning working');
    console.log(`   - Initial: ${initialMultiplier}, Updated: ${updatedMultiplier.toFixed(3)}`);
    console.log(`   - History size: ${matrix.performanceHistory.length}`);
  } else {
    console.log('❌ Adaptive learning failed');
  }
} catch (error) {
  console.log('❌ Adaptive learning test failed:', error.message);
}

// Test 8: Export functionality
console.log('\nTest 8: Export functionality');
try {
  const matrix = new PhonemeIntensityMatrix();
  matrix.learnFromFeedback('aa', 'jawOpen', 1.2);

  const exportData = matrix.exportMatrix();

  if (exportData.baseIntensityMatrix && exportData.statistics) {
    console.log('✅ Matrix export working');
    console.log(`   - Has base matrix: ${!!exportData.baseIntensityMatrix}`);
    console.log(`   - Has statistics: ${!!exportData.statistics}`);
    console.log(`   - User preferences learned: ${exportData.statistics.userPreferencesLearned}`);
  } else {
    console.log('❌ Matrix export failed');
  }
} catch (error) {
  console.log('❌ Export functionality test failed:', error.message);
}

console.log('\n🎉 PhonemeIntensityMatrix testing complete!');
