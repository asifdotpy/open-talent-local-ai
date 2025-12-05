/**
 * Integration Tests for Configuration System
 * TDD PRINCIPLE: Tests define architectural contracts - code must conform
 * 
 * Tests: ConfigManager singleton pattern, AppConfig static interface,
 *        environment isolation, configuration validation, immutability
 * 
 * Run: node tests/integration-config-tdd.test.js
 */

import assert from 'assert';
import { ConfigManager, getConfig } from '../src/config/ConfigManager.js';
import { AppConfig } from '../src/config/AppConfig.js';

console.log('\n⚙️  INTEGRATION TESTS: Configuration System (TDD Contracts)\n');

let passed = 0;
let failed = 0;

async function test(name, fn) {
  try {
    console.log(`  🧪 ${name}...`);
    await fn();
    console.log(`  ✅ ${name}`);
    passed++;
  } catch (error) {
    console.error(`  ❌ ${name}`);
    console.error(`     ${error.message}`);
    failed++;
  }
}

// ============================================================================
// ARCHITECTURAL CONTRACT: Singleton Pattern
// ============================================================================
console.log('🎯 SINGLETON PATTERN CONTRACT');

await test('getConfig MUST return singleton instance (same reference)', async () => {
  const config1 = getConfig();
  const config2 = getConfig();
  
  assert.strictEqual(config1, config2, 
    'CONTRACT VIOLATION: getConfig() must return same singleton instance, not create new objects');
});

await test('Singleton MUST maintain state across calls', async () => {
  const config = getConfig();
  const originalPort = config.get('server.port');
  
  config.set('server.port', 9999);
  
  const sameConfig = getConfig();
  const newPort = sameConfig.get('server.port');
  
  assert.strictEqual(newPort, 9999, 
    'CONTRACT VIOLATION: Singleton must preserve state modifications');
  
  // Restore
  config.set('server.port', originalPort);
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Required Configuration Sections
// ============================================================================
console.log('\n📋 REQUIRED CONFIGURATION SECTIONS CONTRACT');

await test('ConfigManager MUST provide renderer section with output dimensions', async () => {
  const config = getConfig();
  const appConfig = config.getAll();
  
  assert.ok(appConfig.renderer, 
    'CONTRACT VIOLATION: Configuration must include renderer section');
  assert.ok(typeof appConfig.renderer.width === 'number' && appConfig.renderer.width > 0,
    'CONTRACT VIOLATION: renderer.width must be positive number');
  assert.ok(typeof appConfig.renderer.height === 'number' && appConfig.renderer.height > 0,
    'CONTRACT VIOLATION: renderer.height must be positive number');
  assert.ok(typeof appConfig.renderer.fps === 'number' && appConfig.renderer.fps >= 1 && appConfig.renderer.fps <= 120,
    'CONTRACT VIOLATION: renderer.fps must be number between 1-120');
});

await test('ConfigManager MUST provide server section with network config', async () => {
  const config = getConfig();
  const appConfig = config.getAll();
  
  assert.ok(appConfig.server, 
    'CONTRACT VIOLATION: Configuration must include server section');
  assert.ok(typeof appConfig.server.port === 'number' && appConfig.server.port >= 1 && appConfig.server.port <= 65535,
    'CONTRACT VIOLATION: server.port must be valid port number (1-65535)');
  assert.ok(typeof appConfig.server.host === 'string' && appConfig.server.host.length > 0,
    'CONTRACT VIOLATION: server.host must be non-empty string');
});

await test('ConfigManager MUST provide session management section', async () => {
  const config = getConfig();
  const appConfig = config.getAll();
  
  assert.ok(appConfig.session, 
    'CONTRACT VIOLATION: Configuration must include session section');
  assert.ok(typeof appConfig.session.maxSessions === 'number' && appConfig.session.maxSessions >= 1,
    'CONTRACT VIOLATION: session.maxSessions must be positive number');
});

await test('ConfigManager MUST provide logging configuration', async () => {
  const config = getConfig();
  const appConfig = config.getAll();
  
  assert.ok(appConfig.logging, 
    'CONTRACT VIOLATION: Configuration must include logging section');
  
  const validLevels = ['debug', 'info', 'warn', 'error'];
  assert.ok(validLevels.includes(appConfig.logging.level),
    `CONTRACT VIOLATION: logging.level must be one of: ${validLevels.join(', ')}`);
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Fail-Fast Validation
// ============================================================================
console.log('\n⚠️  FAIL-FAST VALIDATION CONTRACT');

await test('ConfigManager MUST throw on invalid port (< 1)', async () => {
  const config = new ConfigManager();
  
  assert.throws(() => {
    config.set('server.port', 0);
    config.validateConfig(config.getAll());
  }, 'CONTRACT VIOLATION: Must reject invalid port numbers (< 1)');
});

await test('ConfigManager MUST throw on invalid port (> 65535)', async () => {
  const config = new ConfigManager();
  
  assert.throws(() => {
    config.set('server.port', 70000);
    config.validateConfig(config.getAll());
  }, 'CONTRACT VIOLATION: Must reject invalid port numbers (> 65535)');
});

await test('ConfigManager MUST throw on dimensions below minimum (100x100)', async () => {
  const config = new ConfigManager();
  
  assert.throws(() => {
    config.set('renderer.width', 50);
    config.validateConfig(config.getAll());
  }, 'CONTRACT VIOLATION: Must reject renderer dimensions below 100x100');
});

await test('ConfigManager MUST throw on invalid FPS range', async () => {
  const config = new ConfigManager();
  
  assert.throws(() => {
    config.set('renderer.fps', 0);
    config.validateConfig(config.getAll());
  }, 'CONTRACT VIOLATION: Must reject FPS < 1');
  
  assert.throws(() => {
    config.set('renderer.fps', 150);
    config.validateConfig(config.getAll());
  }, 'CONTRACT VIOLATION: Must reject FPS > 120');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Environment Isolation
// ============================================================================
console.log('\n🌍 ENVIRONMENT ISOLATION CONTRACT');

await test('ConfigManager MUST respect NODE_ENV=production', async () => {
  const currentEnv = process.env.NODE_ENV;
  
  try {
    process.env.NODE_ENV = 'production';
    const config = new ConfigManager();
    
    assert.strictEqual(config.getEnvironment(), 'production',
      'CONTRACT VIOLATION: Must detect and use production environment');
  } finally {
    process.env.NODE_ENV = currentEnv;
  }
});

await test('ConfigManager MUST default to development when NODE_ENV unset', async () => {
  const currentEnv = process.env.NODE_ENV;
  
  try {
    delete process.env.NODE_ENV;
    const config = new ConfigManager();
    
    assert.strictEqual(config.getEnvironment(), 'development',
      'CONTRACT VIOLATION: Must default to development environment');
  } finally {
    process.env.NODE_ENV = currentEnv;
  }
});

// ============================================================================
// ARCHITECTURAL CONTRACT: AppConfig Static Interface
// ============================================================================
console.log('\n📦 APPCONFIG STATIC INTERFACE CONTRACT');

await test('AppConfig MUST provide DEFAULT_CONFIG with all required sections', async () => {
  const requiredSections = ['features', 'scene', 'camera', 'animation', 'performance', 'assets', 'models'];
  
  requiredSections.forEach(section => {
    assert.ok(AppConfig.DEFAULT_CONFIG[section],
      `CONTRACT VIOLATION: AppConfig.DEFAULT_CONFIG must include ${section} section`);
  });
});

await test('AppConfig MUST provide static getEnvironment() method', async () => {
  assert.ok(typeof AppConfig.getEnvironment === 'function',
    'CONTRACT VIOLATION: AppConfig must provide static getEnvironment() method');
  
  const env = AppConfig.getEnvironment();
  assert.ok(typeof env === 'string' && env.length > 0,
    'CONTRACT VIOLATION: getEnvironment() must return non-empty string');
});

await test('AppConfig MUST provide static validate() method', async () => {
  assert.ok(typeof AppConfig.validate === 'function',
    'CONTRACT VIOLATION: AppConfig must provide static validate() method');
  
  // Should not throw for valid default config
  assert.doesNotThrow(() => {
    AppConfig.validate(AppConfig.DEFAULT_CONFIG);
  }, 'CONTRACT VIOLATION: validate() must accept valid DEFAULT_CONFIG');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Deep Configuration Access
// ============================================================================
console.log('\n🔍 DEEP CONFIGURATION ACCESS CONTRACT');

await test('ConfigManager MUST support dot notation for deep access', async () => {
  const config = getConfig();
  
  const port = config.get('server.port');
  assert.ok(typeof port === 'number',
    'CONTRACT VIOLATION: get() with dot notation must retrieve nested values');
  
  const width = config.get('renderer.width');
  assert.ok(typeof width === 'number',
    'CONTRACT VIOLATION: get() must work for all nested paths');
});

await test('ConfigManager MUST return default value for non-existent paths', async () => {
  const config = getConfig();
  
  const nonExistent = config.get('nonexistent.deep.path', 'DEFAULT');
  assert.strictEqual(nonExistent, 'DEFAULT',
    'CONTRACT VIOLATION: get() must return default value for non-existent paths');
});

// ============================================================================
// ARCHITECTURAL CONTRACT: Immutability Protection
// ============================================================================
console.log('\n🔒 IMMUTABILITY PROTECTION CONTRACT');

await test('ConfigManager.getAll() MUST return defensive copy', async () => {
  const config = getConfig();
  const config1 = config.getAll();
  const config2 = config.getAll();
  
  // Modify first copy
  config1.renderer.width = 99999;
  
  // Second copy should not be affected
  assert.notStrictEqual(config2.renderer.width, 99999,
    'CONTRACT VIOLATION: getAll() must return defensive copies to prevent external mutations');
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
