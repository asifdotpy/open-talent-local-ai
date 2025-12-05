#!/usr/bin/env node
/**
 * WebSocket Streaming Test for Avatar Renderer
 * Tests real-time avatar streaming capabilities
 */

import WebSocket from 'ws';

const WS_URL = 'ws://localhost:3001';

console.log('🔌 Connecting to Avatar Renderer WebSocket...');
console.log(`📍 URL: ${WS_URL}\n`);

const ws = new WebSocket(WS_URL);

let framesReceived = 0;
let sessionId = null;
const startTime = Date.now();

ws.on('open', () => {
  console.log('✅ WebSocket connection established');
  
  // Send start_stream message
  const startMessage = {
    type: 'start_stream',
    config: {
      width: 1920,
      height: 1080,
      fps: 30
    }
  };
  
  console.log('📤 Sending start_stream message:', JSON.stringify(startMessage, null, 2));
  ws.send(JSON.stringify(startMessage));
});

ws.on('message', (data) => {
  try {
    const message = JSON.parse(data.toString());
    
    switch (message.type) {
      case 'connected':
        sessionId = message.sessionId;
        console.log(`✅ Session established: ${sessionId}`);
        console.log(`📊 Capabilities:`, message.capabilities);
        
        // Send sample phoneme data
        setTimeout(() => {
          const phonemeMessage = {
            type: 'phoneme_data',
            phonemes: [
              { phoneme: 'HH', start: 0.0, end: 0.1 },
              { phoneme: 'EH', start: 0.1, end: 0.25 },
              { phoneme: 'L', start: 0.25, end: 0.35 },
              { phoneme: 'OW', start: 0.35, end: 0.5 }
            ],
            audioTimestamp: 0
          };
          console.log('\n📤 Sending phoneme data...');
          ws.send(JSON.stringify(phonemeMessage));
        }, 500);
        break;
        
      case 'stream_started':
        console.log('✅ Stream started successfully');
        console.log(`📊 Config:`, message.config);
        break;
        
      case 'frame':
        framesReceived++;
        const frameSize = message.frameData ? message.frameData.length : 0;
        console.log(`📺 Frame ${framesReceived} received (${(frameSize / 1024).toFixed(2)} KB) at ${message.timestamp.toFixed(3)}s`);
        
        // Stop after receiving 5 frames
        if (framesReceived >= 5) {
          console.log('\n✅ Test successful! Received 5 frames.');
          ws.close();
        }
        break;
        
      case 'error':
        console.error('❌ Server error:', message.message);
        break;
        
      default:
        console.log('📨 Received:', message.type, message);
    }
  } catch (error) {
    console.error('❌ Parse error:', error.message);
  }
});

ws.on('close', (code, reason) => {
  const duration = (Date.now() - startTime) / 1000;
  console.log(`\n🔌 WebSocket closed (code: ${code}, reason: ${reason || 'none'})`);
  console.log(`⏱️  Duration: ${duration.toFixed(2)}s`);
  console.log(`📊 Total frames received: ${framesReceived}`);
  
  if (framesReceived > 0) {
    console.log('\n✅ WebSocket streaming test PASSED');
    process.exit(0);
  } else {
    console.log('\n⚠️  WebSocket streaming test INCOMPLETE (no frames received)');
    process.exit(1);
  }
});

ws.on('error', (error) => {
  console.error('❌ WebSocket error:', error.message);
  process.exit(1);
});

// Timeout after 15 seconds
setTimeout(() => {
  console.log('\n⏱️  Test timeout reached');
  ws.close();
}, 15000);
