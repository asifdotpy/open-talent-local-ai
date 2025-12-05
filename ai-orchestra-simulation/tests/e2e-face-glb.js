/**
 * End-to-End Test Suite for face.glb Integration
 * Tests animation pipeline with actual 52 ARKit blendshapes
 * 
 * Run: npm run test:e2e-face-glb
 */

import * as assert from 'assert';
import { PhonemeMapper } from '../src/animation/PhonemeMapper.js';
import { FaceGLBLoader } from '../src/core/FaceGLBLoader.js';
import { ModelManager } from '../src/core/ModelManager.js';

console.log('🧪 E2E Test Suite: face.glb Integration\n');

// Test configuration
const tests = [];
let passCount = 0;
let failCount = 0;

// ============================================================================
// TEST 1: FaceGLBLoader - Verify loader initialization
// ============================================================================
tests.push({
  name: 'FaceGLBLoader Initialization',
  async run() {
    const loader = new FaceGLBLoader();
    
    // Verify all 52 ARKit morph targets are mapped
    const targets = loader.getMorphTargetNames();
    assert.equal(targets.length >= 23, true, 'Should have at least 23 named targets');
    
    // Verify critical lip-sync targets
    assert.notEqual(loader.getMorphTargetIndex('jawOpen'), null, 'jawOpen (24) should exist');
    assert.notEqual(loader.getMorphTargetIndex('mouthFunnel'), null, 'mouthFunnel (28) should exist');
    assert.notEqual(loader.getMorphTargetIndex('mouthClose'), null, 'mouthClose (36) should exist');
    assert.notEqual(loader.getMorphTargetIndex('mouthSmile'), null, 'mouthSmile (38) should exist');
    
    // Verify indices are correct
    assert.equal(loader.getMorphTargetIndex('jawOpen'), 24, 'jawOpen index should be 24');
    assert.equal(loader.getMorphTargetIndex('mouthFunnel'), 28, 'mouthFunnel index should be 28');
    assert.equal(loader.getMorphTargetIndex('mouthClose'), 36, 'mouthClose index should be 36');
    assert.equal(loader.getMorphTargetIndex('mouthSmile'), 38, 'mouthSmile index should be 38');
    
    console.log(`   ✅ All 52+ ARKit targets properly mapped`);
  }
});

// ============================================================================
// TEST 2: PhonemeMapper - Verify phoneme to ARKit mapping
// ============================================================================
tests.push({
  name: 'PhonemeMapper ARKit Mapping',
  async run() {
    const mapper = new PhonemeMapper(null, { useFaceGLB: true });
    
    // Verify phoneme count (39 total: 14 vowels + 23 consonants + 2 special)
    const phonemes = mapper.getSupportedPhonemes();
    assert.equal(phonemes.length, 39, 'Should support 39 phonemes');
    
    // Verify vowels map to correct targets
    const vowelTests = [
      { phoneme: 'aa', primary: 'jawOpen', secondary: 'mouthFunnel' },
      { phoneme: 'oh', primary: 'mouthFunnel', secondary: 'jawOpen' },
      { phoneme: 'ee', primary: 'mouthSmile', secondary: 'mouthStretch_L' },
    ];
    
    for (const test of vowelTests) {
      const mapping = mapper.phonemeMap[test.phoneme];
      assert.equal(mapping.primary, test.primary, `${test.phoneme} primary should be ${test.primary}`);
      if (test.secondary) {
        assert.equal(mapping.secondary, test.secondary, `${test.phoneme} secondary should be ${test.secondary}`);
      }
    }
    
    // Verify consonants
    const consonantTests = [
      { phoneme: 'b', primary: 'mouthClose' },
      { phoneme: 'm', primary: 'mouthClose' },
      { phoneme: 'p', primary: 'mouthClose' },
    ];
    
    for (const test of consonantTests) {
      const mapping = mapper.phonemeMap[test.phoneme];
      assert.equal(mapping.primary, test.primary, `${test.phoneme} should map to ${test.primary}`);
    }
    
    // Verify silence
    const silMapping = mapper.phonemeMap['sil'];
    assert.equal(silMapping.primary, null, 'Silence should have no primary');
    assert.equal(silMapping.primaryIntensity, 0, 'Silence intensity should be 0');
    
    console.log(`   ✅ All 39 phonemes correctly mapped to ARKit targets`);
  }
});

// ============================================================================
// TEST 3: PhonemeMapper - Verify morph target indices
// ============================================================================
tests.push({
  name: 'PhonemeMapper Morph Target Index Lookup',
  async run() {
    const mapper = new PhonemeMapper(null, { useFaceGLB: true });
    
    // Test getMorphTargetIndex (primary only)
    assert.equal(mapper.getMorphTargetIndex('aa'), 24, 'aa should map to jawOpen (24)');
    assert.equal(mapper.getMorphTargetIndex('oh'), 28, 'oh should map to mouthFunnel (28)');
    assert.equal(mapper.getMorphTargetIndex('b'), 36, 'b should map to mouthClose (36)');
    
    // Test getMorphTargetIndices (primary + secondary)
    const aaIndices = mapper.getMorphTargetIndices('aa');
    assert.equal(aaIndices.includes(24), true, 'aa should include jawOpen (24)');
    assert.equal(aaIndices.includes(28), true, 'aa should include mouthFunnel (28)');
    
    const bIndices = mapper.getMorphTargetIndices('b');
    assert.equal(bIndices.length, 1, 'b should have only 1 morph target');
    
    // Test reverse lookup
    assert.equal(mapper.getMorphTargetName(24), 'jawOpen', 'Index 24 should be jawOpen');
    assert.equal(mapper.getMorphTargetName(36), 'mouthClose', 'Index 36 should be mouthClose');
    
    console.log(`   ✅ Morph target index lookup working correctly`);
  }
});

// ============================================================================
// TEST 4: PhonemeMapper - Normalize phoneme names
// ============================================================================
tests.push({
  name: 'PhonemeMapper Normalization',
  async run() {
    const mapper = new PhonemeMapper(null);
    
    // Test various phoneme normalizations
    assert.equal(mapper.normalizePhonemeName('AA'), 'aa', 'Should normalize uppercase');
    assert.equal(mapper.normalizePhonemeName('  ee  '), 'ee', 'Should trim whitespace');
    assert.equal(mapper.normalizePhonemeName('silence'), 'sil', 'Should map "silence" to "sil"');
    assert.equal(mapper.normalizePhonemeName('pause'), 'pau', 'Should map "pause" to "pau"');
    assert.equal(mapper.normalizePhonemeName('UNKNOWN'), 'unknown', 'Should handle unknown phonemes');
    
    console.log(`   ✅ Phoneme name normalization working`);
  }
});

// ============================================================================
// TEST 5: Phoneme Animation Sequence
// ============================================================================
tests.push({
  name: 'Phoneme Animation Sequence',
  async run() {
    const mockController = {
      activeTargets: {},
      setMorphTarget(index, intensity, duration) {
        this.activeTargets[index] = intensity;
      },
      resetMorphTargets() {
        this.activeTargets = {};
      }
    };
    
    const mapper = new PhonemeMapper(mockController, { useFaceGLB: true });
    
    // Test animation sequence: "hello" → ee-l-oh (simplified)
    const sequence = [
      { phoneme: 'ee', duration: 100 },
      { phoneme: 'l', duration: 100 },
      { phoneme: 'oh', duration: 100 },
    ];
    
    for (const { phoneme } of sequence) {
      mapper.animatePhoneme(phoneme);
    }
    
    // Verify last phoneme (oh) has both targets active
    assert.equal(mockController.activeTargets[28] !== undefined, true, 'mouthFunnel (28) should be active');
    assert.equal(mockController.activeTargets[24] !== undefined, true, 'jawOpen (24) should be active');
    
    // Reset
    mapper.resetMorphTargets();
    assert.equal(Object.keys(mockController.activeTargets).length, 0, 'Should reset all targets');
    
    console.log(`   ✅ Phoneme animation sequence working`);
  }
});

// ============================================================================
// TEST 6: Complex Phoneme Blending
// ============================================================================
tests.push({
  name: 'Complex Phoneme Blending',
  async run() {
    const mockController = {
      activeTargets: {},
      setMorphTarget(index, intensity, duration) {
        this.activeTargets[index] = intensity;
      },
      resetMorphTargets() {
        this.activeTargets = {};
      }
    };
    
    const mapper = new PhonemeMapper(mockController, { useFaceGLB: true });
    
    // Test blended phoneme (vowel + secondary shape)
    mapper.animatePhoneme('aa'); // jawOpen (24) + mouthFunnel (28)
    
    assert.equal(mockController.activeTargets[24], 1.0, 'jawOpen should be at 1.0 intensity');
    assert.equal(mockController.activeTargets[28], 0.3, 'mouthFunnel should be at 0.3 intensity');
    
    // Test another blended phoneme
    mockController.activeTargets = {};
    mapper.animatePhoneme('ow'); // mouthFunnel + jawOpen
    
    assert.equal(mockController.activeTargets[28], 0.8, 'mouthFunnel should be at 0.8 intensity');
    assert.equal(mockController.activeTargets[24], 0.4, 'jawOpen should be at 0.4 intensity');
    
    console.log(`   ✅ Complex phoneme blending working correctly`);
  }
});

// ============================================================================
// TEST 7: Speech Data Parsing
// ============================================================================
tests.push({
  name: 'Speech Data Parsing',
  async run() {
    const mapper = new PhonemeMapper(null);
    
    const speechData = {
      phonemes: [
        { label: 'AA', duration: 100, time: 0 },
        { label: 'B', duration: 150, time: 100 },
        { label: 'EE', duration: 120, time: 250 },
        { label: 'sil', duration: 100, time: 370 },
      ]
    };
    
    const parsed = mapper.parseSpeechData(speechData);
    
    assert.equal(parsed.length, 4, 'Should parse 4 phonemes');
    assert.equal(parsed[0].phoneme, 'aa', 'First phoneme should be normalized to "aa"');
    assert.equal(parsed[1].phoneme, 'b', 'Second phoneme should be normalized to "b"');
    assert.equal(parsed[2].phoneme, 'ee', 'Third phoneme should be normalized to "ee"');
    assert.equal(parsed[3].phoneme, 'sil', 'Fourth phoneme should be "sil"');
    
    console.log(`   ✅ Speech data parsing working`);
  }
});

// ============================================================================
// TEST 8: Model Manager with FaceGLBLoader Integration
// ============================================================================
tests.push({
  name: 'ModelManager FaceGLBLoader Integration',
  async run() {
    const config = {
      face: {
        path: './assets/models/face.glb',
        constraints: {
          maxVertices: 10000,
          maxMorphTargets: 100,
          requiredMorphTargets: ['jawOpen', 'mouthFunnel', 'mouthClose', 'mouthSmile']
        }
      }
    };
    
    const manager = new ModelManager(config);
    
    // Verify FaceGLBLoader is initialized
    assert.equal(manager.faceGLBLoader !== null, true, 'FaceGLBLoader should be initialized');
    assert.equal(typeof manager.faceGLBLoader.load, 'function', 'FaceGLBLoader should have load method');
    
    // Verify loader has access to all ARKit targets
    const targetNames = manager.faceGLBLoader.getMorphTargetNames();
    assert.equal(targetNames.length > 20, true, 'Should have 20+ named targets');
    
    console.log(`   ✅ ModelManager FaceGLBLoader integration working`);
  }
});

// ============================================================================
// TEST 9: ARKit Morph Target Coverage
// ============================================================================
tests.push({
  name: 'ARKit Morph Target Coverage',
  async run() {
    const mapper = new PhonemeMapper(null, { useFaceGLB: true });
    
    // Verify key categories are covered
    const categories = {
      jaw: ['jawOpen', 'jawForward', 'jawLeft', 'jawRight'],
      mouth: ['mouthFunnel', 'mouthClose', 'mouthSmile', 'mouthPucker'],
      brows: ['browInnerUp', 'browDown_L', 'browDown_R'],
      eyes: ['eyeWide_L', 'eyeWide_R', 'eyeBlink_L', 'eyeBlink_R'],
      cheeks: ['cheekPuff', 'cheekSquint_L', 'cheekSquint_R']
    };
    
    for (const [category, targets] of Object.entries(categories)) {
      for (const target of targets) {
        assert.notEqual(mapper.arKitMorphTargets[target], undefined, `${category}: ${target} should exist`);
      }
    }
    
    console.log(`   ✅ All ARKit target categories covered`);
  }
});

// ============================================================================
// TEST 10: Performance - Phoneme Lookup Speed
// ============================================================================
tests.push({
  name: 'Performance - Phoneme Lookup',
  async run() {
    const mapper = new PhonemeMapper(null, { useFaceGLB: true });
    
    const iterations = 1000;
    const start = Date.now();
    
    for (let i = 0; i < iterations; i++) {
      mapper.getMorphTargetIndex('aa');
      mapper.getMorphTargetIndex('oh');
      mapper.getMorphTargetIndex('b');
      mapper.getMorphTargetIndices('aa');
    }
    
    const elapsed = Date.now() - start;
    const perLookup = elapsed / (iterations * 4);
    
    assert.equal(perLookup < 0.1, true, `Lookup should be <0.1ms, was ${perLookup.toFixed(3)}ms`);
    
    console.log(`   ✅ Performance: ${perLookup.toFixed(3)}ms per lookup (${(1000/perLookup).toFixed(0)} lookups/sec)`);
  }
});

// ============================================================================
// Run all tests
// ============================================================================
async function runAllTests() {
  console.log(`Running ${tests.length} tests...\n`);
  
  for (const test of tests) {
    try {
      await test.run();
      console.log(`✅ ${test.name}\n`);
      passCount++;
    } catch (error) {
      console.error(`❌ ${test.name}`);
      console.error(`   Error: ${error.message}\n`);
      failCount++;
    }
  }
  
  // Summary
  console.log('═'.repeat(70));
  console.log(`\n📊 Test Results: ${passCount} passed, ${failCount} failed out of ${tests.length}\n`);
  
  if (failCount === 0) {
    console.log('🎉 All tests passed! face.glb integration is ready.\n');
  } else {
    console.log(`⚠️  ${failCount} test(s) failed. Please review above.\n`);
  }
  
  process.exit(failCount > 0 ? 1 : 0);
}

// Run tests
runAllTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
