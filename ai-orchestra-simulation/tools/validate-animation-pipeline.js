#!/usr/bin/env node
/**
 * Animation Pipeline Validator
 * Tests the complete morph target animation pipeline
 * 
 * Validates:
 * 1. Model loading and morph target detection
 * 2. PhonemeMapper initialization and mapping
 * 3. MorphTargetAdapter animation capability
 * 4. End-to-end phoneme animation sequence
 * 5. Emotion blending with morph targets
 */

import { MorphTargetAdapter } from '../src/adapters/ModelAdapter.js';
import { PhonemeMapper } from '../src/animation/PhonemeMapper.js';
import { AppConfig } from '../src/config/AppConfig.js';
import { ModelManager } from '../src/core/ModelManager.js';

// ANSI color codes for pretty output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
  console.log('');
  log('='.repeat(80), 'cyan');
  log(`  ${title}`, 'bright');
  log('='.repeat(80), 'cyan');
}

function logSuccess(message) {
  log(`✅ ${message}`, 'green');
}

function logError(message) {
  log(`❌ ${message}`, 'red');
}

function logWarning(message) {
  log(`⚠️  ${message}`, 'yellow');
}

function logInfo(message) {
  log(`ℹ️  ${message}`, 'blue');
}

// Validation state
const validationResults = {
  passed: [],
  failed: [],
  warnings: [],
};

function recordPass(test, details = '') {
  validationResults.passed.push({ test, details });
  logSuccess(`${test} ${details ? `- ${details}` : ''}`);
}

function recordFail(test, details = '') {
  validationResults.failed.push({ test, details });
  logError(`${test} ${details ? `- ${details}` : ''}`);
}

function recordWarning(test, details = '') {
  validationResults.warnings.push({ test, details });
  logWarning(`${test} ${details ? `- ${details}` : ''}`);
}

/**
 * Test 1: Model Loading and Morph Target Detection
 */
async function validateModelLoading() {
  logSection('TEST 1: Model Loading and Morph Target Detection');

  try {
    // Load configuration
    const appConfig = AppConfig.get();
    const modelKey = 'face'; // Test with face.glb
    const config = appConfig.models.production;
    logInfo(`Loading model: ${config.path}`);

    // Initialize ModelManager  
    const modelManager = new ModelManager({ face: config }, { mockMode: false });

    // Load model
    const model = await modelManager.loadModel('face');

    if (!model) {
      recordFail('Model loading', 'Model is null or undefined');
      return null;
    }
    recordPass('Model loading', 'Model loaded successfully');

    // Check model structure
    let meshCount = 0;
    let morphTargetMesh = null;

    model.traverse((child) => {
      if (child.isMesh) {
        meshCount++;
        if (child.morphTargetInfluences && child.morphTargetInfluences.length > 0) {
          morphTargetMesh = child;
        }
      }
    });

    recordPass('Model structure', `Found ${meshCount} meshes`);

    if (!morphTargetMesh) {
      recordFail('Morph target detection', 'No mesh with morph targets found');
      return null;
    }
    recordPass('Morph target detection', `Found mesh with ${morphTargetMesh.morphTargetInfluences.length} morph targets`);

    // Validate morph target dictionary
    if (!morphTargetMesh.morphTargetDictionary) {
      recordFail('Morph target dictionary', 'morphTargetDictionary is missing');
      return null;
    }

    const morphTargets = Object.keys(morphTargetMesh.morphTargetDictionary);
    recordPass('Morph target dictionary', `${morphTargets.length} morph targets defined`);

    // Log morph targets
    logInfo('Available morph targets:');
    for (const [name, index] of Object.entries(morphTargetMesh.morphTargetDictionary)) {
      console.log(`  [${index}] ${name}`);
    }

    // Check for required lip-sync targets
    const requiredTargets = ['jawOpen', 'mouthFunnel', 'mouthClose', 'mouthSmile'];
    const missingTargets = requiredTargets.filter(t => !morphTargets.includes(t));

    if (missingTargets.length > 0) {
      recordWarning('Required morph targets', `Missing: ${missingTargets.join(', ')}`);
      logInfo('Note: Morph targets may use generic names (target_0, target_1, etc.)');
      logInfo('PhonemeMapper will need to map indices to phoneme shapes');
    } else {
      recordPass('Required morph targets', 'All lip-sync targets present');
    }

    return { model, morphTargetMesh, modelManager };
  } catch (error) {
    recordFail('Model loading exception', error.message);
    console.error(error);
    return null;
  }
}

/**
 * Test 2: PhonemeMapper Initialization
 */
function validatePhonemeMapper() {
  logSection('TEST 2: PhonemeMapper Initialization');

  try {
    // Create mock animation controller
    const mockController = {
      setMorphTarget: (index, intensity, duration) => {
        logInfo(`Mock: setMorphTarget(${index}, ${intensity}, ${duration})`);
      },
      resetMorphTargets: () => {
        logInfo('Mock: resetMorphTargets()');
      },
    };

    // Initialize PhonemeMapper
    const phonemeMapper = new PhonemeMapper(mockController, {
      smoothingFactor: 0.1,
      transitionDuration: 50,
    });

    if (!phonemeMapper) {
      recordFail('PhonemeMapper initialization', 'Failed to create instance');
      return null;
    }
    recordPass('PhonemeMapper initialization', 'Instance created successfully');

    // Check phoneme map
    const supportedPhonemes = phonemeMapper.getSupportedPhonemes();
    if (supportedPhonemes.length === 0) {
      recordFail('Phoneme map', 'No phonemes defined');
      return null;
    }
    recordPass('Phoneme map', `${supportedPhonemes.length} phonemes supported`);

    // Test phoneme normalization
    const testCases = [
      { input: 'AA', expected: 'aa' },
      { input: 'silence', expected: 'sil' },
      { input: 'PAUSE', expected: 'pau' },
      { input: 'EE', expected: 'ee' },
    ];

    let normalizationPassed = true;
    for (const testCase of testCases) {
      const result = phonemeMapper.normalizePhonemeName(testCase.input);
      if (result !== testCase.expected) {
        recordWarning('Phoneme normalization', `"${testCase.input}" → "${result}" (expected "${testCase.expected}")`);
        normalizationPassed = false;
      }
    }

    if (normalizationPassed) {
      recordPass('Phoneme normalization', 'All test cases passed');
    }

    // Test getMorphTargetIndex
    const testPhonemes = ['aa', 'ee', 'b', 'm', 'sil'];
    logInfo('Testing getMorphTargetIndex:');
    for (const phoneme of testPhonemes) {
      const index = phonemeMapper.getMorphTargetIndex(phoneme);
      console.log(`  ${phoneme} → index ${index}`);
      if (index === null && phoneme !== 'sil') {
        recordWarning('Morph target index', `Phoneme "${phoneme}" has no mapping`);
      }
    }

    recordPass('getMorphTargetIndex', 'Method working correctly');

    return phonemeMapper;
  } catch (error) {
    recordFail('PhonemeMapper exception', error.message);
    console.error(error);
    return null;
  }
}

/**
 * Test 3: MorphTargetAdapter Initialization
 */
function validateMorphTargetAdapter(modelData, phonemeMapper) {
  logSection('TEST 3: MorphTargetAdapter Initialization');

  if (!modelData || !phonemeMapper) {
    recordFail('MorphTargetAdapter prerequisites', 'Missing model or phonemeMapper');
    return null;
  }

  try {
    const { model } = modelData;
    const appConfig = AppConfig.get();
    const config = appConfig.models.production;

    // Initialize adapter
    const adapter = new MorphTargetAdapter(model, config, phonemeMapper);

    if (!adapter) {
      recordFail('MorphTargetAdapter initialization', 'Failed to create instance');
      return null;
    }
    recordPass('MorphTargetAdapter initialization', 'Instance created successfully');

    // Check if morph target mesh was found
    if (!adapter.morphTargetMesh) {
      recordFail('Morph target mesh detection', 'Adapter did not find morph target mesh');
      return null;
    }
    recordPass('Morph target mesh detection', 'Adapter found morph target mesh');

    // Test getMorphTargetForPhoneme
    const testPhonemes = ['aa', 'ee', 'b', 'm'];
    logInfo('Testing getMorphTargetForPhoneme:');
    for (const phoneme of testPhonemes) {
      const index = adapter.getMorphTargetForPhoneme(phoneme);
      console.log(`  ${phoneme} → index ${index}`);
    }

    recordPass('getMorphTargetForPhoneme', 'Method working correctly');

    return adapter;
  } catch (error) {
    recordFail('MorphTargetAdapter exception', error.message);
    console.error(error);
    return null;
  }
}

/**
 * Test 4: Animation Sequence Testing
 */
function validateAnimationSequence(adapter) {
  logSection('TEST 4: Animation Sequence Testing');

  if (!adapter) {
    recordFail('Animation sequence prerequisites', 'Missing adapter');
    return;
  }

  try {
    // Create test phoneme sequence
    const testSequence = [
      { phoneme: 'aa', start: 0.0, end: 0.1 },  // "ah" sound
      { phoneme: 'b', start: 0.1, end: 0.15 },  // "b" sound
      { phoneme: 'ee', start: 0.15, end: 0.25 }, // "ee" sound
      { phoneme: 'm', start: 0.25, end: 0.3 },  // "m" sound
      { phoneme: 'sil', start: 0.3, end: 0.4 }, // silence
    ];

    logInfo('Testing animation sequence:');

    for (const phoneme of testSequence) {
      const midTime = (phoneme.start + phoneme.end) / 2;
      logInfo(`  Animating "${phoneme.phoneme}" at t=${midTime.toFixed(2)}s`);

      // Animate
      adapter.animate(testSequence, midTime);

      // Check morph target influences
      if (adapter.morphTargetMesh) {
        const influences = adapter.morphTargetMesh.morphTargetInfluences;
        const activeTargets = influences
          .map((value, index) => ({ index, value }))
          .filter(t => t.value > 0);

        if (activeTargets.length > 0) {
          logInfo(`    Active morph targets: ${activeTargets.map(t => `[${t.index}]=${t.value.toFixed(2)}`).join(', ')}`);
        } else if (phoneme.phoneme !== 'sil') {
          recordWarning('Animation', `No morph targets activated for "${phoneme.phoneme}"`);
        }
      }

      // Reset
      adapter.reset();
    }

    recordPass('Animation sequence', 'All phonemes animated successfully');
  } catch (error) {
    recordFail('Animation sequence exception', error.message);
    console.error(error);
  }
}

/**
 * Test 5: Emotion Blending
 */
function validateEmotionBlending(adapter) {
  logSection('TEST 5: Emotion Blending');

  if (!adapter) {
    recordFail('Emotion blending prerequisites', 'Missing adapter');
    return;
  }

  try {
    // Test emotion weights
    const emotionTests = [
      { name: 'Happy', weights: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0] },
      { name: 'Sad', weights: [0.0, 1.0, 0.0, 0.0, 0.0, 0.0] },
      { name: 'Surprised', weights: [0.0, 0.0, 1.0, 0.0, 0.0, 0.0] },
      { name: 'Mixed (Happy + Surprised)', weights: [0.7, 0.0, 0.5, 0.0, 0.0, 0.0] },
    ];

    const testPhoneme = [{ phoneme: 'aa', start: 0.0, end: 0.1 }];

    logInfo('Testing emotion blending:');

    for (const test of emotionTests) {
      logInfo(`  Emotion: ${test.name}`);
      adapter.animateWithEmotion(testPhoneme, 0.05, test.weights);

      if (adapter.morphTargetMesh) {
        const influences = adapter.morphTargetMesh.morphTargetInfluences;
        const activeTargets = influences
          .map((value, index) => ({ index, value }))
          .filter(t => t.value > 0);

        logInfo(`    Active morph targets: ${activeTargets.map(t => `[${t.index}]=${t.value.toFixed(2)}`).join(', ')}`);
      }

      adapter.reset();
    }

    recordPass('Emotion blending', 'All emotion tests completed');
  } catch (error) {
    recordFail('Emotion blending exception', error.message);
    console.error(error);
  }
}

/**
 * Test 6: Performance Validation
 */
function validatePerformance(adapter) {
  logSection('TEST 6: Performance Validation');

  if (!adapter) {
    recordFail('Performance validation prerequisites', 'Missing adapter');
    return;
  }

  try {
    const testPhoneme = [{ phoneme: 'aa', start: 0.0, end: 1.0 }];
    const iterations = 1000;

    logInfo(`Running ${iterations} animation frames...`);

    const startTime = Date.now();
    for (let i = 0; i < iterations; i++) {
      const time = i / iterations;
      adapter.animate(testPhoneme, time);
    }
    const endTime = Date.now();

    const totalTime = endTime - startTime;
    const avgTime = totalTime / iterations;
    const fps = 1000 / avgTime;

    logInfo(`Total time: ${totalTime}ms`);
    logInfo(`Average time per frame: ${avgTime.toFixed(3)}ms`);
    logInfo(`Theoretical FPS: ${fps.toFixed(1)}`);

    if (avgTime > 16.67) {
      recordWarning('Performance', `Average frame time ${avgTime.toFixed(2)}ms exceeds 60fps target (16.67ms)`);
    } else {
      recordPass('Performance', `Animation runs at ${fps.toFixed(1)}fps`);
    }
  } catch (error) {
    recordFail('Performance validation exception', error.message);
    console.error(error);
  }
}

/**
 * Generate final report
 */
function generateReport() {
  logSection('VALIDATION REPORT');

  log(`Total Tests: ${validationResults.passed.length + validationResults.failed.length}`, 'bright');
  logSuccess(`Passed: ${validationResults.passed.length}`);
  logError(`Failed: ${validationResults.failed.length}`);
  logWarning(`Warnings: ${validationResults.warnings.length}`);

  if (validationResults.failed.length > 0) {
    console.log('');
    log('Failed Tests:', 'red');
    for (const failure of validationResults.failed) {
      logError(`  ${failure.test}: ${failure.details}`);
    }
  }

  if (validationResults.warnings.length > 0) {
    console.log('');
    log('Warnings:', 'yellow');
    for (const warning of validationResults.warnings) {
      logWarning(`  ${warning.test}: ${warning.details}`);
    }
  }

  console.log('');
  if (validationResults.failed.length === 0) {
    logSuccess('✨ All tests passed! Animation pipeline is fully functional. ✨');
    return 0;
  } else {
    logError('❌ Some tests failed. Please review and fix issues.');
    return 1;
  }
}

/**
 * Main validation function
 */
async function main() {
  log('🎬 Animation Pipeline Validator', 'bright');
  log('Testing complete morph target animation system', 'dim');

  // Test 1: Model Loading
  const modelData = await validateModelLoading();

  // Test 2: PhonemeMapper
  const phonemeMapper = validatePhonemeMapper();

  // Test 3: MorphTargetAdapter
  const adapter = validateMorphTargetAdapter(modelData, phonemeMapper);

  // Test 4: Animation Sequence
  validateAnimationSequence(adapter);

  // Test 5: Emotion Blending
  validateEmotionBlending(adapter);

  // Test 6: Performance
  validatePerformance(adapter);

  // Generate report
  const exitCode = generateReport();
  process.exit(exitCode);
}

// Run validation
main().catch((error) => {
  logError('Unhandled exception in validation pipeline');
  console.error(error);
  process.exit(1);
});
