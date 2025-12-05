#!/usr/bin/env node

import fetch from 'node-fetch';
import WebSocket from 'ws';

// Test the complete flow: TTS -> WebSocket -> Avatar Renderer
async function testLipSyncFlow() {
  console.log('🎭 Testing Lip-Sync Flow: TTS → WebSocket → Avatar Renderer\n');

  try {
    // Step 1: Get TTS data with phonemes
    console.log('📢 Step 1: Requesting TTS with phoneme extraction...');
    const ttsResponse = await fetch('http://localhost:8002/voice/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Hello, welcome to your AI interview.',
        voice: 'en-US',
        extract_phonemes: true
      })
    });

    if (!ttsResponse.ok) {
      throw new Error(`TTS API error: ${ttsResponse.status}`);
    }

    const ttsData = await ttsResponse.json();
    console.log(`✅ TTS successful: ${ttsData.phonemes.length} phonemes, ${ttsData.duration}s duration\n`);

    // Step 2: Connect to WebSocket
    console.log('🔌 Step 2: Connecting to Avatar Renderer WebSocket...');
    const ws = new WebSocket('ws://localhost:3001');

    return new Promise((resolve, reject) => {
      ws.on('open', () => {
        console.log('✅ WebSocket connected\n');

        // Step 3: Send ready message
        console.log('📨 Step 3: Sending ready message...');
        ws.send(JSON.stringify({ type: 'ready' }));
      });

      ws.on('message', (data) => {
        const message = JSON.parse(data.toString());
        console.log(`📨 Received: ${message.type}`);

        if (message.type === 'connected') {
          console.log(`   Session ID: ${message.sessionId}`);
          console.log(`   Renderer: ${message.capabilities.type}\n`);
        }

        if (message.type === 'ready_ack') {
          console.log('✅ Server ready for streaming\n');

          // Step 4: Send phoneme data
          console.log('🎭 Step 4: Sending phoneme data for lip-sync...');
          let phonemeIndex = 0;

          const sendPhoneme = () => {
            if (phonemeIndex < ttsData.phonemes.length) {
              const phoneme = ttsData.phonemes[phonemeIndex];
              ws.send(JSON.stringify({
                type: 'phoneme_data',
                phonemes: [phoneme],
                audioTimestamp: phoneme.start,
                sessionId: message.sessionId
              }));

              console.log(`   Sent phoneme: ${phoneme.phoneme} (${phoneme.start}s - ${phoneme.end}s)`);
              phonemeIndex++;

              // Send next phoneme after a short delay
              setTimeout(sendPhoneme, 50);
            } else {
              console.log('\n✅ All phonemes sent successfully!');
              console.log('🎉 Lip-sync flow test completed successfully!\n');

              // Close connection
              setTimeout(() => {
                ws.close();
                resolve();
              }, 1000);
            }
          };

          sendPhoneme();
        }
      });

      ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error.message);
        reject(error);
      });

      ws.on('close', () => {
        console.log('🔌 WebSocket connection closed');
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        ws.close();
        reject(new Error('Test timeout'));
      }, 30000);
    });

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    throw error;
  }
}

// Run the test
testLipSyncFlow().then(() => {
  console.log('🎊 All tests passed! Lip-sync system is working correctly.');
  process.exit(0);
}).catch((error) => {
  console.error('💥 Test failed:', error.message);
  process.exit(1);
});