/**
 * Test R3F Renderer Integration
 *
 * Tests the R3FRenderer initialization and WebSocket communication
 * with the avatar rendering backend system.
 */

import WebSocket from 'ws';
import { R3FRenderer } from './src/renderer/R3FRenderer.js';

async function testR3FRenderer() {
  console.log('🧪 Testing R3F Renderer Integration...\n');

  const renderer = new R3FRenderer({
    websocketPort: 3003, // Use different port for testing
    websocketHost: 'localhost',
    maxConnections: 10,
    logger: console
  });

  try {
    // Test 1: Initialize renderer
    console.log('1️⃣ Testing renderer initialization...');
    const initSuccess = await renderer.initialize();
    if (!initSuccess) {
      throw new Error('Renderer initialization failed');
    }
    console.log('✅ Renderer initialized successfully');

    // Test 2: Check capabilities
    console.log('\n2️⃣ Testing renderer capabilities...');
    const capabilities = renderer.getCapabilities();
    console.log('Capabilities:', JSON.stringify(capabilities, null, 2));

    if (capabilities.type !== 'r3f') {
      throw new Error('Incorrect renderer type in capabilities');
    }
    console.log('✅ Capabilities correct');

    // Test 3: Test WebSocket connection
    console.log('\n3️⃣ Testing WebSocket connection...');
    const ws = new WebSocket('ws://localhost:3003');

    // Message queue for handling WebSocket messages
    const messageQueue = [];
    let messageResolver;

    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        messageQueue.push(message);
        if (messageResolver) {
          messageResolver();
          messageResolver = null;
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });

    await new Promise((resolve, reject) => {
      ws.on('open', () => {
        console.log('✅ WebSocket connection established');
        resolve();
      });

      ws.on('error', (error) => {
        reject(new Error(`WebSocket connection failed: ${error.message}`));
      });

      // Timeout after 5 seconds
      setTimeout(() => {
        reject(new Error('WebSocket connection timeout'));
      }, 5000);
    });

    // Helper function to wait for next message
    const waitForMessage = (expectedType, timeout = 2000) => {
      return new Promise((resolve, reject) => {
        const checkQueue = () => {
          const message = messageQueue.shift();
          if (message && message.type === expectedType) {
            resolve(message);
            return;
          } else if (message) {
            // Put back if not the expected type
            messageQueue.unshift(message);
          }

          messageResolver = () => {
            const nextMessage = messageQueue.shift();
            if (nextMessage && nextMessage.type === expectedType) {
              resolve(nextMessage);
            } else {
              reject(new Error(`Expected ${expectedType}, got ${nextMessage?.type}`));
            }
          };

          setTimeout(() => {
            reject(new Error(`${expectedType} message timeout`));
          }, timeout);
        };

        checkQueue();
      });
    };

    // Test 4: Test receiving welcome message
    console.log('\n4️⃣ Testing welcome message...');
    const welcomeMessage = await waitForMessage('connected');

    console.log('Welcome message received:', JSON.stringify(welcomeMessage, null, 2));
    console.log('✅ Welcome message correct');

    // Test 5: Test sending ready message
    console.log('\n5️⃣ Testing ready handshake...');
    ws.send(JSON.stringify({ type: 'ready' }));

    const readyAck = await waitForMessage('ready_ack');
    console.log('Ready ack received:', JSON.stringify(readyAck, null, 2));
    console.log('✅ Ready handshake successful');

    // Test 6: Test renderFrame (phoneme data sending)
    console.log('\n6️⃣ Testing phoneme frame sending...');
    const testPhonemeData = {
      phoneme: 'AA',
      start: 0,
      end: 0.5
    };

    await renderer.renderFrame(0, 0.8, testPhonemeData);

    const frameMessage = await waitForMessage('phoneme_frame');
    console.log('Frame message received:', JSON.stringify(frameMessage, null, 2));
    console.log('✅ Phoneme frame sending works');

    // Test 7: Test connection stats
    console.log('\n7️⃣ Testing connection statistics...');
    const stats = renderer.getConnectionStats();
    console.log('Connection stats:', JSON.stringify(stats, null, 2));
    console.log('✅ Connection stats available');

    // Clean up
    ws.close();
    await renderer.dispose();

    console.log('\n🎉 All R3F Renderer tests passed!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await renderer.dispose();
    process.exit(1);
  }
}

// Run the test
testR3FRenderer().catch((error) => {
  console.error('💥 Fatal test error:', error);
  process.exit(1);
});