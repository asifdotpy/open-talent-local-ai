/**
 * Simple test runner for CoarticulationEngine
 * Runs basic validation tests without Jest dependencies
 */

import { CoarticulationEngine } from '../src/animation/CoarticulationEngine.js';

console.log('🧪 Testing CoarticulationEngine...\n');

// Test 1: Initialization
console.log('Test 1: Initialization');
try {
  const engine = new CoarticulationEngine();
  const stats = engine.getStatistics();

  console.log('✅ Engine initialized successfully');
  console.log(`   - Coarticulation rules: ${stats.rulesCount}`);
  console.log(`   - Assimilation patterns: ${stats.assimilationPatterns}`);
  console.log(`   - Look-ahead phonemes: ${stats.config.lookAheadPhonemes}`);
} catch (error) {
  console.log('❌ Initialization failed:', error.message);
}

// Test 2: Phoneme sequence processing
console.log('\nTest 2: Phoneme sequence processing');
try {
  const engine = new CoarticulationEngine();
  const sequence = [
    { phoneme: 'aa', intensities: { jawOpen: 0.9 } },
    { phoneme: 'b', intensities: { mouthClose: 0.8 } },
    { phoneme: 'ee', intensities: { jawOpen: 0.6 } },
  ];

  const result = engine.processPhonemeSequence(sequence);

  if (result.length === 3) {
    console.log('✅ Sequence processed successfully');
    console.log(`   - Input length: ${sequence.length}`);
    console.log(`   - Output length: ${result.length}`);
    console.log(`   - First phoneme: ${result[0].phoneme}`);
  } else {
    console.log('❌ Sequence processing failed');
  }
} catch (error) {
  console.log('❌ Sequence processing failed:', error.message);
}

// Test 3: Look-ahead buffer
console.log('\nTest 3: Look-ahead buffer');
try {
  const engine = new CoarticulationEngine();
  const sequence = ['aa', 'b', 'ee', 's'];

  const buffer = engine.buildLookAheadBuffer(sequence);

  if (buffer.length === 4 && buffer[0].length === 3) {
    console.log('✅ Look-ahead buffer built successfully');
    console.log(`   - Buffer length: ${buffer.length}`);
    console.log(`   - First item look-ahead: ${buffer[0].length}`);
    console.log(`   - First look-ahead phoneme: ${buffer[0][0].phoneme}`);
  } else {
    console.log('❌ Look-ahead buffer failed');
  }
} catch (error) {
  console.log('❌ Look-ahead buffer failed:', error.message);
}

// Test 4: Context building
console.log('\nTest 4: Context building');
try {
  const engine = new CoarticulationEngine();
  const sequence = ['aa', 'b', 'ee'];
  const lookAheadBuffer = engine.buildLookAheadBuffer(sequence);
  const timingData = [{ duration: 100 }, { duration: 80 }, { duration: 120 }];

  const context = engine.buildContext(1, sequence, lookAheadBuffer, timingData);

  if (context.previousPhoneme === 'aa' && context.nextPhoneme === 'ee') {
    console.log('✅ Context built successfully');
    console.log(`   - Previous phoneme: ${context.previousPhoneme}`);
    console.log(`   - Next phoneme: ${context.nextPhoneme}`);
    console.log(`   - Look-ahead items: ${context.lookAhead.length}`);
    console.log(`   - Position: ${context.position.toFixed(2)}`);
  } else {
    console.log('❌ Context building failed');
  }
} catch (error) {
  console.log('❌ Context building failed:', error.message);
}

// Test 5: Transition smoothing
console.log('\nTest 5: Transition smoothing');
try {
  const engine = new CoarticulationEngine();
  const phoneme = {
    phoneme: 'ee',
    intensities: { jawOpen: 0.6 },
    timing: { duration: 100 },
  };
  const context = {
    previousPhoneme: 'aa',
    nextPhoneme: 'ih',
    position: 0.5,
  };

  const result = engine.applyTransitionSmoothing(phoneme, context);

  if (result.timing.transitionType === 'smooth') {
    console.log('✅ Transition smoothing applied');
    console.log(`   - Transition type: ${result.timing.transitionType}`);
    console.log(`   - Duration: ${result.timing.duration}ms`);
  } else {
    console.log('❌ Transition smoothing failed');
  }
} catch (error) {
  console.log('❌ Transition smoothing failed:', error.message);
}

// Test 6: Anticipatory coarticulation
console.log('\nTest 6: Anticipatory coarticulation');
try {
  const engine = new CoarticulationEngine();
  const phoneme = {
    phoneme: 'aa',
    intensities: { mouthPucker: 0.3, mouthFunnel: 0.2 },
  };
  const context = {
    lookAhead: [
      { phoneme: 'ow', distance: 1, weight: 0.8 },
      { phoneme: 'ee', distance: 2, weight: 0.6 },
    ],
  };

  const result = engine.applyAnticipatoryCoarticulation(phoneme, context);

  // Should show some influence from rounded vowel 'ow'
  if (result.intensities.mouthPucker > 0.3) {
    console.log('✅ Anticipatory coarticulation working');
    console.log(`   - Original mouthPucker: 0.3`);
    console.log(`   - Modified mouthPucker: ${result.intensities.mouthPucker.toFixed(3)}`);
  } else {
    console.log('❌ Anticipatory coarticulation failed');
  }
} catch (error) {
  console.log('❌ Anticipatory coarticulation failed:', error.message);
}

// Test 7: Assimilation effects
console.log('\nTest 7: Assimilation effects');
try {
  const engine = new CoarticulationEngine();
  const phoneme = {
    phoneme: 'f',
    intensities: { mouthClose: 0.6 },
  };
  const context = { previousPhoneme: 'b' };

  const result = engine.applyAssimilationEffects(phoneme, context);

  if (result.intensities.mouthClose !== 0.6) {
    console.log('✅ Assimilation effects applied');
    console.log(`   - Original intensity: 0.6`);
    console.log(`   - Modified intensity: ${result.intensities.mouthClose.toFixed(3)}`);
  } else {
    console.log('❌ Assimilation effects failed');
  }
} catch (error) {
  console.log('❌ Assimilation effects failed:', error.message);
}

// Test 8: Cluster optimization
console.log('\nTest 8: Cluster optimization');
try {
  const engine = new CoarticulationEngine();
  const phoneme = {
    phoneme: 's',
    intensities: { mouthClose: 0.7 },
    timing: { duration: 100 },
  };
  const context = {
    previousPhoneme: 't',
    nextPhoneme: 'r',
  };

  const result = engine.applyClusterOptimization(phoneme, context);

  if (result.intensities.mouthClose < 0.7 && result.timing.duration < 100) {
    console.log('✅ Cluster optimization working');
    console.log(`   - Reduced intensity: ${result.intensities.mouthClose.toFixed(3)}`);
    console.log(`   - Reduced duration: ${result.timing.duration}ms`);
  } else {
    console.log('❌ Cluster optimization failed');
  }
} catch (error) {
  console.log('❌ Cluster optimization failed:', error.message);
}

// Test 9: Utility functions
console.log('\nTest 9: Utility functions');
try {
  const engine = new CoarticulationEngine();

  // Test vowel identification
  const isVowel = engine.isVowel('aa') && !engine.isVowel('b');
  const isConsonant = engine.isConsonant('s') && !engine.isConsonant('ee');

  // Test smoothing
  const smoothed = engine.smoothTransition(0.8, 0.5, 0.5);

  if (isVowel && isConsonant && smoothed > 0.7 && smoothed < 0.9) {
    console.log('✅ Utility functions working');
    console.log(`   - Vowel detection: ✓`);
    console.log(`   - Consonant detection: ✓`);
    console.log(`   - Transition smoothing: ✓ (${smoothed.toFixed(3)})`);
  } else {
    console.log('❌ Utility functions failed');
  }
} catch (error) {
  console.log('❌ Utility functions failed:', error.message);
}

// Test 10: Statistics and export
console.log('\nTest 10: Statistics and export');
try {
  const engine = new CoarticulationEngine();
  const stats = engine.getStatistics();
  const config = engine.exportConfiguration();

  if (stats.rulesCount > 100 && config.coarticulationRules) {
    console.log('✅ Statistics and export working');
    console.log(`   - Rules count: ${stats.rulesCount}`);
    console.log(`   - Assimilation patterns: ${stats.assimilationPatterns}`);
    console.log(`   - Config exported: ✓`);
  } else {
    console.log('❌ Statistics and export failed');
  }
} catch (error) {
  console.log('❌ Statistics and export failed:', error.message);
}

console.log('\n🎉 CoarticulationEngine testing complete!');
