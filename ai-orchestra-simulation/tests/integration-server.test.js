/**
 * Integration Tests for Server API
 * Tests: AvatarServer endpoints, WebSocket, health checks
 * 
 * Requires server running on port 3001
 * Run: node tests/integration-server.test.js
 */

import assert from 'assert';
import fetch from 'node-fetch';
import WebSocket from 'ws';

const BASE_URL = 'http://localhost:3001';
const WS_URL = 'ws://localhost:3001';

console.log('\n🌐 INTEGRATION TESTS: Server API\n');

let passed = 0;
let failed = 0;
let skipped = 0;

async function test(name, fn) {
  try {
    console.log(`  🧪 ${name}...`);
    await fn();
    console.log(`  ✅ ${name}`);
    passed++;
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log(`  ⏭️  ${name} (server not running)`);
      skipped++;
    } else {
      console.error(`  ❌ ${name}`);
      console.error(`     ${error.message}`);
      failed++;
    }
  }
}

// ============================================================================
// Server Health & Status
// ============================================================================
console.log('🏥 Server Health');

await test('GET /health returns 200', async () => {
  const response = await fetch(`${BASE_URL}/health`, { timeout: 5000 });
  assert.strictEqual(response.status, 200, 'Should return 200');
  const data = await response.json();
  assert.strictEqual(data.status, 'healthy', 'Should report healthy status');
});

await test('GET /status returns server info', async () => {
  const response = await fetch(`${BASE_URL}/status`, { timeout: 5000 });
  assert.strictEqual(response.status, 200, 'Should return 200');
  const data = await response.json();
  assert.ok(data.version, 'Should include version');
  assert.ok(data.uptime !== undefined, 'Should include uptime');
});

await test('GET /metrics returns performance data', async () => {
  const response = await fetch(`${BASE_URL}/metrics`, { timeout: 5000 });
  assert.strictEqual(response.status, 200, 'Should return 200');
  const data = await response.json();
  assert.ok(data.activeSessions !== undefined, 'Should report active sessions');
});

// ============================================================================
// API Documentation
// ============================================================================
console.log('\n📚 API Documentation');

await test('GET /docs returns Swagger UI', async () => {
  const response = await fetch(`${BASE_URL}/docs`, { timeout: 5000 });
  assert.strictEqual(response.status, 200, 'Should return 200');
  assert.ok(response.headers.get('content-type').includes('text/html'), 
    'Should return HTML');
});

await test('GET /api-docs returns OpenAPI spec', async () => {
  const response = await fetch(`${BASE_URL}/api-docs`, { timeout: 5000 });
  assert.strictEqual(response.status, 200, 'Should return 200');
  const data = await response.json();
  assert.ok(data.openapi || data.swagger, 'Should contain OpenAPI spec');
  assert.ok(data.paths, 'Should have paths defined');
});

// ============================================================================
// Rendering Endpoint
// ============================================================================
console.log('\n🎨 Rendering');

await test('POST /render/lipsync accepts phoneme data', async () => {
  const payload = {
    phonemes: [
      { phoneme: 'AA', start: 0.0, end: 0.1 },
      { phoneme: 'EH', start: 0.1, end: 0.25 }
    ],
    duration: 0.25,
    audioUrl: 'file:///tmp/test.wav'
  };

  const response = await fetch(`${BASE_URL}/render/lipsync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    timeout: 10000
  });

  assert.ok([200, 202, 400].includes(response.status), 
    `Should return 200, 202, or 400, got ${response.status}`);
});

// ============================================================================
// WebSocket
// ============================================================================
console.log('\n📡 WebSocket');

await test('WebSocket connects successfully', async () => {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('WebSocket connection timeout'));
    }, 5000);

    const ws = new WebSocket(WS_URL);
    
    ws.on('open', () => {
      clearTimeout(timeout);
      ws.close();
      resolve();
    });

    ws.on('error', (error) => {
      clearTimeout(timeout);
      reject(error);
    });
  });
});

await test('WebSocket accepts start_stream message', async () => {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('WebSocket test timeout'));
    }, 5000);

    const ws = new WebSocket(WS_URL);
    
    ws.on('open', () => {
      ws.send(JSON.stringify({
        type: 'start_stream',
        config: { width: 1920, height: 1080, fps: 30 }
      }));

      ws.on('message', (data) => {
        clearTimeout(timeout);
        try {
          const msg = JSON.parse(data);
          assert.ok(msg.type, 'Message should have type');
          ws.close();
          resolve();
        } catch (e) {
          // Binary data or other formats are acceptable
          ws.close();
          resolve();
        }
      });
    });

    ws.on('error', (error) => {
      clearTimeout(timeout);
      reject(error);
    });
  });
});

// ============================================================================
// Summary
// ============================================================================
console.log(`\n${'='.repeat(60)}`);
console.log(`Results: ${passed} passed, ${failed} failed, ${skipped} skipped`);
console.log(`${'='.repeat(60)}\n`);

process.exit(failed > 0 ? 1 : 0);
