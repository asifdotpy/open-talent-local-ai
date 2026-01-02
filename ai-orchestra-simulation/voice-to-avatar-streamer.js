/**
 * Voice-to-Avatar Streaming Client
 *
 * Connects to Voice Service for real-time phoneme extraction
 * and streams data to Avatar Renderer for lip-sync animation
 */

import fetch from 'node-fetch';
import WebSocket from 'ws';

class VoiceToAvatarStreamer {
  constructor(options = {}) {
    this.voiceServiceUrl = options.voiceServiceUrl || 'http://localhost:8002';
    this.avatarServiceUrl = options.avatarServiceUrl || 'ws://localhost:3001';
    this.logger = options.logger || console;

    this.voiceWs = null;
    this.avatarWs = null;
    this.isStreaming = false;
    this.currentSessionId = null;
  }

  async startStreaming(text, voice = 'lessac') {
    try {
      this.logger.log('Starting voice-to-avatar streaming...');

      // Step 1: Get phoneme data from voice service
      const phonemeData = await this.getPhonemeData(text, voice);

      // Step 2: Connect to avatar renderer WebSocket
      await this.connectToAvatarRenderer();

      // Step 3: Start streaming phonemes in real-time
      await this.streamPhonemesToAvatar(phonemeData);

      this.logger.log('Voice-to-avatar streaming started successfully');
      return { success: true, sessionId: this.currentSessionId };

    } catch (error) {
      this.logger.error('Failed to start streaming:', error);
      this.cleanup();
      throw error;
    }
  }

  async getPhonemeData(text, voice) {
    this.logger.log(`Getting phoneme data for text: "${text}" with voice: ${voice}`);

    const response = await fetch(`${this.voiceServiceUrl}/voice/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        voice: voice
      })
    });

    if (!response.ok) {
      throw new Error(`Voice service error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Validate that we have the required phoneme data
    if (!data.phonemes || !Array.isArray(data.phonemes)) {
      throw new Error('Voice service TTS response missing phoneme data');
    }

    this.logger.log(`Received phoneme data: ${data.phonemes?.length || 0} phonemes, duration: ${data.duration}s`);
    return data;
  }

  async connectToAvatarRenderer() {
    return new Promise((resolve, reject) => {
      this.logger.log(`Connecting to avatar renderer at ${this.avatarServiceUrl}`);

      this.avatarWs = new WebSocket(this.avatarServiceUrl);

      this.avatarWs.on('open', () => {
        this.logger.log('Connected to avatar renderer WebSocket');
        resolve();
      });

      this.avatarWs.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          this.handleAvatarMessage(message);
        } catch (error) {
          this.logger.error('Error parsing avatar message:', error);
        }
      });

      this.avatarWs.on('error', (error) => {
        this.logger.error('Avatar WebSocket error:', error);
        reject(error);
      });

      this.avatarWs.on('close', () => {
        this.logger.log('Avatar WebSocket connection closed');
        this.cleanup();
      });

      // Timeout after 10 seconds
      setTimeout(() => {
        reject(new Error('Connection timeout'));
      }, 10000);
    });
  }

  handleAvatarMessage(message) {
    switch (message.type) {
      case 'connected':
        this.currentSessionId = message.sessionId;
        this.logger.log(`Avatar session established: ${this.currentSessionId}`);
        break;
      case 'stream_started':
        this.logger.log(`Avatar streaming started: ${message.width}x${message.height}@${message.fps}fps`);
        break;
      case 'error':
        this.logger.error('Avatar renderer error:', message.message);
        break;
      default:
        // Ignore other messages (like frame data)
        break;
    }
  }

  async streamPhonemesToAvatar(phonemeData) {
    const { phonemes, duration } = phonemeData;

    // Start avatar streaming session
    this.avatarWs.send(JSON.stringify({
      type: 'start_stream',
      width: 1920,
      height: 1080,
      fps: 30
    }));

    // Wait for stream to start
    await new Promise(resolve => setTimeout(resolve, 100));

    // Send phoneme data
    this.avatarWs.send(JSON.stringify({
      type: 'phoneme_data',
      phonemes: phonemes,
      audioTimestamp: 0
    }));

    this.isStreaming = true;
    this.logger.log(`Streaming ${phonemes.length} phonemes for ${duration}s`);

    // Keep connection alive for the duration
    return new Promise((resolve) => {
      setTimeout(() => {
        this.stopStreaming();
        resolve();
      }, (duration + 1) * 1000); // Add 1 second buffer
    });
  }

  stopStreaming() {
    if (this.isStreaming) {
      this.logger.log('Stopping voice-to-avatar streaming...');

      if (this.avatarWs && this.avatarWs.readyState === WebSocket.OPEN) {
        this.avatarWs.send(JSON.stringify({
          type: 'stop_stream'
        }));
      }

      this.isStreaming = false;
    }
  }

  cleanup() {
    this.isStreaming = false;

    if (this.avatarWs) {
      this.avatarWs.close();
      this.avatarWs = null;
    }

    if (this.voiceWs) {
      this.voiceWs.close();
      this.voiceWs = null;
    }
  }

  // Test method to verify voice service connectivity
  async testVoiceService() {
    try {
      const response = await fetch(`${this.voiceServiceUrl}/health`);
      const data = await response.json();
      this.logger.log('Voice service health:', data);
      return data;
    } catch (error) {
      this.logger.error('Voice service test failed:', error);
      throw error;
    }
  }

  // Test method to verify avatar renderer connectivity
  async testAvatarRenderer() {
    try {
      const response = await fetch('http://localhost:3001/health');
      const data = await response.json();
      this.logger.log('Avatar renderer health:', data);
      return data;
    } catch (error) {
      this.logger.error('Avatar renderer test failed:', error);
      throw error;
    }
  }
}

// CLI interface for testing
async function main() {
  const streamer = new VoiceToAvatarStreamer();

  // Parse command line arguments
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    switch (command) {
      case 'test':
        console.log('Testing services...');
        await streamer.testVoiceService();
        await streamer.testAvatarRenderer();
        console.log('✅ All services are healthy');
        break;

      case 'stream':
        const text = args.slice(1).join(' ') || 'Hello world, this is a test of real-time lip-sync animation.';
        const voice = process.env.VOICE || 'lessac';

        console.log(`🎤 Streaming text: "${text}"`);
        console.log(`🎭 Using voice: ${voice}`);

        const result = await streamer.startStreaming(text, voice);
        console.log('✅ Streaming completed successfully');
        break;

      default:
        console.log('Usage:');
        console.log('  node voice-to-avatar-streamer.js test');
        console.log('  node voice-to-avatar-streamer.js stream [text]');
        console.log('');
        console.log('Environment variables:');
        console.log('  VOICE=lessac|amy|ryan|hfc_female (default: lessac)');
        break;
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Export for use as module
export default VoiceToAvatarStreamer;

// Run CLI if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
