/**
 * Unit Tests for Animation System
 * TDD PRINCIPLE: Tests define architectural contracts - code must conform
 *
 * Tests: PhonemeMapper API, ARKit blendshape mappings, phoneme coverage,
 *        intensity validation, type safety
 *
 * Run: node tests/unit-animation-tdd.test.js
 */

import assert from 'assert';
import { PhonemeMapper } from '../src/animation/PhonemeMapper.js';

console.log('\n🎬 UNIT TESTS: Animation System (TDD Contracts)\n');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ✅ ${name}`);
    passed++;
  } catch (error) {
    console.error(`  ❌ ${name}`);
    console.error(`     ${error.message}`);
    failed++;
  }
}

// ============================================================================
// ARCHITECTURAL CONTRACT: PhonemeMapper Initialization
// ============================================================================
console.log('🎯 PHONEME MAPPER INITIALIZATION CONTRACT');

test('PhonemeMapper MUST instantiate without errors', () => {
  assert.doesNotThrow(() => {
    const mapper = new PhonemeMapper();
    assert.ok(mapper, 'CONTRACT VIOLATION: PhonemeMapper must instantiate successfully');
  }, 'CONTRACT VIOLATION: PhonemeMapper constructor must not throw');
});

test('PhonemeMapper MUST accept optional animationController parameter', () => {
  const mockController = { setMorphTarget: () => {}, resetMorphTargets: () => {} };
  assert.doesNotThrow(() => {
    const mapper = new PhonemeMapper(mockController);
    assert.ok(mapper, 'CONTRACT VIOLATION: PhonemeMapper must accept animationController');
  }, 'CONTRACT VIOLATION: PhonemeMapper(controller) must not throw');
});

test('PhonemeMapper MUST accept optional config parameter', () => {
  const config = { smoothingFactor: 0.2, transitionDuration: 100 };
  assert.doesNotThrow(() => {
    const mapper = new PhonemeMapper(null, config);
    assert.ok(mapper, 'CONTRACT VIOLATION: PhonemeMapper must accept config object');
  }, 'CONTRACT VIOLATION: PhonemeMapper(controller, config) must not throw');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Phoneme Coverage
// ============================================================================
console.log('\n📋 PHONEME COVERAGE CONTRACT');

test('PhonemeMapper MUST support minimum 39 phonemes (14 vowels + 23 consonants + 2 special)', () => {
  const mapper = new PhonemeMapper();
  const phonemeCount = Object.keys(mapper.phonemeMap).length;

  assert.ok(phonemeCount >= 39,
    `CONTRACT VIOLATION: Must support at least 39 phonemes, found ${phonemeCount}`);
});

test('PhonemeMapper MUST map all English vowels', () => {
  const mapper = new PhonemeMapper();
  const requiredVowels = ['aa', 'ae', 'ah', 'ao', 'ee', 'eh', 'er', 'ih', 'iy', 'oh', 'ow', 'oy', 'uh', 'uw'];

  requiredVowels.forEach(vowel => {
    assert.ok(mapper.phonemeMap[vowel],
      `CONTRACT VIOLATION: Must include vowel mapping for '${vowel}'`);
  });
});

test('PhonemeMapper MUST map all standard consonants', () => {
  const mapper = new PhonemeMapper();
  const requiredConsonants = ['b', 'ch', 'd', 'f', 'g', 'hh', 'jh', 'k', 'l', 'm', 'n', 'ng', 'p', 'r', 's', 'sh', 't', 'th', 'v', 'w', 'y', 'z', 'zh'];

  requiredConsonants.forEach(consonant => {
    assert.ok(mapper.phonemeMap[consonant],
      `CONTRACT VIOLATION: Must include consonant mapping for '${consonant}'`);
  });
});

test('PhonemeMapper MUST map special phonemes (silence, pause)', () => {
  const mapper = new PhonemeMapper();
  const requiredSpecial = ['sil', 'pau'];

  requiredSpecial.forEach(special => {
    assert.ok(mapper.phonemeMap[special],
      `CONTRACT VIOLATION: Must include special phoneme '${special}'`);
  });
});

// ============================================================================
// ARCHITECTURAL CONTRACT: ARKit Blendshape Mapping
// ============================================================================
console.log('\n🎭 ARKIT BLENDSHAPE MAPPING CONTRACT');

test('PhonemeMapper MUST provide arKitMorphTargets with minimum 52 targets', () => {
  const mapper = new PhonemeMapper();

  assert.ok(mapper.arKitMorphTargets,
    'CONTRACT VIOLATION: Must provide arKitMorphTargets property');

  const targetCount = Object.keys(mapper.arKitMorphTargets).length;
  assert.ok(targetCount >= 52,
    `CONTRACT VIOLATION: Must provide at least 52 ARKit targets (face.glb standard), found ${targetCount}`);
});

test('PhonemeMapper MUST include required mouth morph targets', () => {
  const mapper = new PhonemeMapper();
  const requiredMouthTargets = ['jawOpen', 'mouthClose', 'mouthFunnel', 'mouthPucker', 'mouthSmile'];

  requiredMouthTargets.forEach(target => {
    assert.ok(mapper.arKitMorphTargets[target] !== undefined,
      `CONTRACT VIOLATION: Must include ARKit morph target '${target}'`);
  });
});

test('PhonemeMapper MUST map morph target indices as non-negative integers', () => {
  const mapper = new PhonemeMapper();

  Object.entries(mapper.arKitMorphTargets).forEach(([name, index]) => {
    assert.ok(Number.isInteger(index) && index >= 0,
      `CONTRACT VIOLATION: Morph target '${name}' index must be non-negative integer, got ${index}`);
  });
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Phoneme Mapping Structure
// ============================================================================
console.log('\n🔧 PHONEME MAPPING STRUCTURE CONTRACT');

test('PhonemeMapper MUST provide primary morph target for all non-silence phonemes', () => {
  const mapper = new PhonemeMapper();

  Object.entries(mapper.phonemeMap).forEach(([phoneme, mapping]) => {
    if (phoneme !== 'sil') {
      assert.ok(mapping.primary !== undefined && mapping.primary !== null,
        `CONTRACT VIOLATION: Phoneme '${phoneme}' must have primary morph target (got ${mapping.primary})`);
    }
  });
});

test('PhonemeMapper MUST provide intensity values in range 0-1', () => {
  const mapper = new PhonemeMapper();

  Object.entries(mapper.phonemeMap).forEach(([phoneme, mapping]) => {
    if (mapping.primaryIntensity !== undefined) {
      assert.ok(mapping.primaryIntensity >= 0 && mapping.primaryIntensity <= 1,
        `CONTRACT VIOLATION: Phoneme '${phoneme}' primaryIntensity must be 0-1, got ${mapping.primaryIntensity}`);
    }

    if (mapping.secondaryIntensity !== undefined) {
      assert.ok(mapping.secondaryIntensity >= 0 && mapping.secondaryIntensity <= 1,
        `CONTRACT VIOLATION: Phoneme '${phoneme}' secondaryIntensity must be 0-1, got ${mapping.secondaryIntensity}`);
    }
  });
});

test('PhonemeMapper MUST provide consistent mapping structure (primary, secondary, intensities)', () => {
  const mapper = new PhonemeMapper();

  Object.entries(mapper.phonemeMap).forEach(([phoneme, mapping]) => {
    assert.ok('primary' in mapping,
      `CONTRACT VIOLATION: Phoneme '${phoneme}' mapping must include 'primary' key`);
    assert.ok('primaryIntensity' in mapping,
      `CONTRACT VIOLATION: Phoneme '${phoneme}' mapping must include 'primaryIntensity' key`);
    assert.ok('secondary' in mapping,
      `CONTRACT VIOLATION: Phoneme '${phoneme}' mapping must include 'secondary' key`);
    assert.ok('secondaryIntensity' in mapping,
      `CONTRACT VIOLATION: Phoneme '${phoneme}' mapping must include 'secondaryIntensity' key`);
  });
});

// ============================================================================
// ARCHITECTURAL CONTRACT: PhonemeMapper API
// ============================================================================
console.log('\n🔌 PHONEME MAPPER API CONTRACT');

test('PhonemeMapper MUST provide animatePhoneme(phoneme, duration) method', () => {
  const mapper = new PhonemeMapper();
  assert.strictEqual(typeof mapper.animatePhoneme, 'function',
    'CONTRACT VIOLATION: Must provide animatePhoneme() method');
});

test('PhonemeMapper MUST provide resetMorphTargets() method', () => {
  const mapper = new PhonemeMapper();
  assert.strictEqual(typeof mapper.resetMorphTargets, 'function',
    'CONTRACT VIOLATION: Must provide resetMorphTargets() method');
});

test('PhonemeMapper MUST provide getSupportedPhonemes() method', () => {
  const mapper = new PhonemeMapper();
  assert.strictEqual(typeof mapper.getSupportedPhonemes, 'function',
    'CONTRACT VIOLATION: Must provide getSupportedPhonemes() method');

  const supported = mapper.getSupportedPhonemes();
  assert.ok(Array.isArray(supported) && supported.length >= 39,
    'CONTRACT VIOLATION: getSupportedPhonemes() must return array of at least 39 phonemes');
});

test('PhonemeMapper MUST provide normalizePhonemeName() method', () => {
  const mapper = new PhonemeMapper();
  assert.strictEqual(typeof mapper.normalizePhonemeName, 'function',
    'CONTRACT VIOLATION: Must provide normalizePhonemeName() method');
});

test('PhonemeMapper MUST provide getMorphTargetIndex(phoneme) method', () => {
  const mapper = new PhonemeMapper();
  assert.strictEqual(typeof mapper.getMorphTargetIndex, 'function',
    'CONTRACT VIOLATION: Must provide getMorphTargetIndex() method');
});

// ============================================================================
// SUMMARY: TDD CONTRACT ENFORCEMENT
// ============================================================================
console.log(`\n${'='.repeat(70)}`);
console.log(`📊 TDD CONTRACT TEST RESULTS`);
console.log(`${'='.repeat(70)}`);
console.log(`✅ Passed: ${passed}`);
console.log(`❌ Failed: ${failed}`);
console.log(`📝 Total:  ${passed + failed}`);
if (failed > 0) {
  console.log(`\n⚠️  ARCHITECTURE VIOLATIONS DETECTED - FIX CODE, NOT TESTS`);
}
console.log(`${'='.repeat(70)}\n`);

process.exit(failed > 0 ? 1 : 0);
