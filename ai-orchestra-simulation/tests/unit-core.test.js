/**
 * Unit Tests for Core Components
 * TDD PRINCIPLE: Tests define architectural contracts - code must conform
 *
 * Tests: AppConfig static interface, Logger API, configuration validation,
 *        type safety, feature flag contracts
 *
 * Run: node tests/unit-core-tdd.test.js
 */

import assert from 'assert';
import { Logger } from '../src/utils/Logger.js';
import { AppConfig } from '../src/config/AppConfig.js';

console.log('\n📋 UNIT TESTS: Core Components (TDD Contracts)\n');

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
// ARCHITECTURAL CONTRACT: AppConfig Static Interface
// ============================================================================
console.log('🎯 APPCONFIG STATIC INTERFACE CONTRACT');

test('AppConfig MUST provide DEFAULT_CONFIG as static property', () => {
  assert.ok(typeof AppConfig.DEFAULT_CONFIG === 'object' && AppConfig.DEFAULT_CONFIG !== null,
    'CONTRACT VIOLATION: AppConfig must provide DEFAULT_CONFIG static property');
});

test('AppConfig MUST provide getEnvironment() static method', () => {
  assert.strictEqual(typeof AppConfig.getEnvironment, 'function',
    'CONTRACT VIOLATION: AppConfig must provide static getEnvironment() method');

  const env = AppConfig.getEnvironment();
  assert.ok(typeof env === 'string' && (env === 'development' || env === 'production'),
    'CONTRACT VIOLATION: getEnvironment() must return "development" or "production"');
});

test('AppConfig MUST provide validate() static method', () => {
  assert.strictEqual(typeof AppConfig.validate, 'function',
    'CONTRACT VIOLATION: AppConfig must provide static validate() method');
});

test('AppConfig MUST provide get() static method', () => {
  assert.strictEqual(typeof AppConfig.get, 'function',
    'CONTRACT VIOLATION: AppConfig must provide static get() method for config retrieval');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Required Configuration Sections
// ============================================================================
console.log('\n📦 REQUIRED CONFIGURATION SECTIONS CONTRACT');

test('DEFAULT_CONFIG MUST include features section', () => {
  assert.ok(AppConfig.DEFAULT_CONFIG.features && typeof AppConfig.DEFAULT_CONFIG.features === 'object',
    'CONTRACT VIOLATION: DEFAULT_CONFIG must include features section');
});

test('DEFAULT_CONFIG MUST include scene section', () => {
  assert.ok(AppConfig.DEFAULT_CONFIG.scene && typeof AppConfig.DEFAULT_CONFIG.scene === 'object',
    'CONTRACT VIOLATION: DEFAULT_CONFIG must include scene section');
});

test('DEFAULT_CONFIG MUST include camera section', () => {
  assert.ok(AppConfig.DEFAULT_CONFIG.camera && typeof AppConfig.DEFAULT_CONFIG.camera === 'object',
    'CONTRACT VIOLATION: DEFAULT_CONFIG must include camera section');
});

test('DEFAULT_CONFIG MUST include animation section', () => {
  assert.ok(AppConfig.DEFAULT_CONFIG.animation && typeof AppConfig.DEFAULT_CONFIG.animation === 'object',
    'CONTRACT VIOLATION: DEFAULT_CONFIG must include animation section');
});

test('DEFAULT_CONFIG MUST include performance section', () => {
  assert.ok(AppConfig.DEFAULT_CONFIG.performance && typeof AppConfig.DEFAULT_CONFIG.performance === 'object',
    'CONTRACT VIOLATION: DEFAULT_CONFIG must include performance section');
});

test('DEFAULT_CONFIG MUST include assets section', () => {
  assert.ok(AppConfig.DEFAULT_CONFIG.assets && typeof AppConfig.DEFAULT_CONFIG.assets === 'object',
    'CONTRACT VIOLATION: DEFAULT_CONFIG must include assets section');
});

test('DEFAULT_CONFIG MUST include models section', () => {
  assert.ok(AppConfig.DEFAULT_CONFIG.models && typeof AppConfig.DEFAULT_CONFIG.models === 'object',
    'CONTRACT VIOLATION: DEFAULT_CONFIG must include models section');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Type Safety
// ============================================================================
console.log('\n🔢 TYPE SAFETY CONTRACT');

test('scene.backgroundColor MUST be number (hex color)', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.scene.backgroundColor, 'number',
    'CONTRACT VIOLATION: scene.backgroundColor must be number (hex color code)');
});

test('scene.antialias MUST be boolean', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.scene.antialias, 'boolean',
    'CONTRACT VIOLATION: scene.antialias must be boolean');
});

test('camera.fov MUST be number', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.camera.fov, 'number',
    'CONTRACT VIOLATION: camera.fov must be number');
});

test('camera.position MUST have x,y,z number coordinates', () => {
  const pos = AppConfig.DEFAULT_CONFIG.camera.position;
  assert.ok(pos && typeof pos.x === 'number' && typeof pos.y === 'number' && typeof pos.z === 'number',
    'CONTRACT VIOLATION: camera.position must have {x, y, z} number coordinates');
});

test('animation.mouthDisplacement MUST be non-negative number', () => {
  const displacement = AppConfig.DEFAULT_CONFIG.animation.mouthDisplacement;
  assert.ok(typeof displacement === 'number' && displacement >= 0,
    'CONTRACT VIOLATION: animation.mouthDisplacement must be non-negative number');
});

test('performance.minFPS MUST be positive number', () => {
  const minFPS = AppConfig.DEFAULT_CONFIG.performance.minFPS;
  assert.ok(typeof minFPS === 'number' && minFPS > 0,
    'CONTRACT VIOLATION: performance.minFPS must be positive number');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Feature Flags
// ============================================================================
console.log('\n🚩 FEATURE FLAGS CONTRACT');

test('features.enableAvatar MUST be boolean', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.features.enableAvatar, 'boolean',
    'CONTRACT VIOLATION: features.enableAvatar must be boolean');
});

test('features.enableAudioVisualization MUST be boolean', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.features.enableAudioVisualization, 'boolean',
    'CONTRACT VIOLATION: features.enableAudioVisualization must be boolean');
});

test('features.enableWebRTCStreaming MUST be boolean', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.features.enableWebRTCStreaming, 'boolean',
    'CONTRACT VIOLATION: features.enableWebRTCStreaming must be boolean');
});

test('features.enableVideoRecording MUST be boolean', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.features.enableVideoRecording, 'boolean',
    'CONTRACT VIOLATION: features.enableVideoRecording must be boolean');
});

test('features.enablePhonemeAnimation MUST be boolean', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.features.enablePhonemeAnimation, 'boolean',
    'CONTRACT VIOLATION: features.enablePhonemeAnimation must be boolean');
});

test('features.enableRealTimeSync MUST be boolean', () => {
  assert.strictEqual(typeof AppConfig.DEFAULT_CONFIG.features.enableRealTimeSync, 'boolean',
    'CONTRACT VIOLATION: features.enableRealTimeSync must be boolean');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Logger API
// ============================================================================
console.log('\n📝 LOGGER API CONTRACT');

test('Logger MUST instantiate without errors', () => {
  assert.doesNotThrow(() => {
    const log = new Logger();
    assert.ok(log, 'CONTRACT VIOLATION: Logger must instantiate successfully');
  }, 'CONTRACT VIOLATION: Logger constructor must not throw');
});

test('Logger MUST accept optional namespace parameter', () => {
  assert.doesNotThrow(() => {
    const log = new Logger('TestNamespace');
    assert.ok(log, 'CONTRACT VIOLATION: Logger must accept namespace parameter');
  }, 'CONTRACT VIOLATION: Logger(namespace) must not throw');
});

test('Logger MUST provide log() method', () => {
  const log = new Logger();
  assert.strictEqual(typeof log.log, 'function',
    'CONTRACT VIOLATION: Logger must provide log() method');
});

test('Logger MUST handle all standard log levels without throwing', () => {
  const log = new Logger();
  const levels = ['debug', 'info', 'warn', 'error'];

  levels.forEach(level => {
    assert.doesNotThrow(() => {
      log.log(`Test ${level} message`, level);
    }, `CONTRACT VIOLATION: Logger must handle ${level} level without errors`);
  });
});

test('Logger MUST not throw on invalid log level (graceful degradation)', () => {
  const log = new Logger();
  assert.doesNotThrow(() => {
    log.log('message', 'invalid_level');
  }, 'CONTRACT VIOLATION: Logger must gracefully handle invalid log levels');
});

test('Logger MUST handle object/array payloads', () => {
  const log = new Logger();
  assert.doesNotThrow(() => {
    log.log({ key: 'value', nested: { data: 123 } }, 'info');
    log.log([1, 2, 3], 'debug');
  }, 'CONTRACT VIOLATION: Logger must handle complex data types');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Configuration Validation
// ============================================================================
console.log('\n✅ CONFIGURATION VALIDATION CONTRACT');

test('AppConfig.validate() MUST throw on missing required sections', () => {
  const invalidConfig = { features: {}, scene: {} }; // Missing camera, animation, etc.

  assert.throws(() => {
    AppConfig.validate(invalidConfig);
  }, 'CONTRACT VIOLATION: validate() must reject config missing required sections');
});

test('AppConfig.validate() MUST throw on invalid scene.backgroundColor type', () => {
  const invalidConfig = {
    ...AppConfig.DEFAULT_CONFIG,
    scene: { ...AppConfig.DEFAULT_CONFIG.scene, backgroundColor: 'invalid' }
  };

  assert.throws(() => {
    AppConfig.validate(invalidConfig);
  }, 'CONTRACT VIOLATION: validate() must reject non-number backgroundColor');
});

test('AppConfig.validate() MUST throw on invalid camera coordinates', () => {
  const invalidConfig = {
    ...AppConfig.DEFAULT_CONFIG,
    camera: { ...AppConfig.DEFAULT_CONFIG.camera, position: { x: 'invalid', y: 0, z: 0 } }
  };

  assert.throws(() => {
    AppConfig.validate(invalidConfig);
  }, 'CONTRACT VIOLATION: validate() must reject non-number camera coordinates');
});

test('AppConfig.validate() MUST accept valid DEFAULT_CONFIG', () => {
  assert.doesNotThrow(() => {
    AppConfig.validate(AppConfig.DEFAULT_CONFIG);
  }, 'CONTRACT VIOLATION: validate() must accept valid DEFAULT_CONFIG');
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
