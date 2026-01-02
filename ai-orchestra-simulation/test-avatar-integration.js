/**
 * Integration Tests for Avatar Interview System
 * Tests end-to-end functionality of R3F frontend with backend services
 */

const { expect } = require('chai');
const axios = require('axios');
const WebSocket = require('ws');

// Test configuration
const CONFIG = {
  VOICE_SERVICE_URL: 'http://localhost:8002',
  INTERVIEW_SERVICE_URL: 'http://localhost:8004',
  AVATAR_RENDERER_URL: 'http://localhost:3001',
  R3F_FRONTEND_URL: 'http://localhost:3000',
  WEBSOCKET_URL: 'ws://localhost:3001'
};

// Test utilities
class AvatarIntegrationTester {
  constructor() {
    this.axios = axios.create({
      timeout: 10000,
      validateStatus: () => true // Don't throw on non-2xx status codes
    });
  }

  async waitForService(url, serviceName, maxRetries = 30) {
    console.log(`⏳ Waiting for ${serviceName} at ${url}...`);
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await this.axios.get(`${url}/health`);
        if (response.status === 200) {
          console.log(`✅ ${serviceName} is ready!`);
          return true;
        }
      } catch (error) {
        // Service not ready yet
      }
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    throw new Error(`${serviceName} failed to start within ${maxRetries * 2} seconds`);
  }

  async testVoiceService() {
    console.log('\n🎤 Testing Voice Service...');

    // Test health check
    const healthResponse = await this.axios.get(`${CONFIG.VOICE_SERVICE_URL}/health`);
    expect(healthResponse.status).to.equal(200);
    expect(healthResponse.data.status).to.equal('healthy');

    // Test TTS with phoneme extraction
    const ttsResponse = await this.axios.post(`${CONFIG.VOICE_SERVICE_URL}/voice/tts`, {
      text: 'Hello, I am an AI interviewer.',
      voice: 'lessac',
      extract_phonemes: true
    });
    expect(ttsResponse.status).to.equal(200);
    expect(ttsResponse.data).to.have.property('audio_base64');
    expect(ttsResponse.data).to.have.property('phonemes');
    expect(ttsResponse.data.phonemes).to.be.an('array');
    expect(ttsResponse.data.phonemes.length).to.be.greaterThan(0);

    console.log('✅ Voice Service tests passed');
    return ttsResponse.data;
  }

  async testAvatarRenderer() {
    console.log('\n🎭 Testing Avatar Renderer...');

    // Test health check
    const healthResponse = await this.axios.get(`${CONFIG.AVATAR_RENDERER_URL}/health`);
    expect(healthResponse.status).to.equal(200);

    // Test status endpoint
    const statusResponse = await this.axios.get(`${CONFIG.AVATAR_RENDERER_URL}/status`);
    expect(statusResponse.status).to.equal(200);
    expect(statusResponse.data).to.have.property('status');
    expect(statusResponse.data).to.have.property('uptime');

    console.log('✅ Avatar Renderer tests passed');
    return statusResponse.data;
  }

  async testInterviewService() {
    console.log('\n💼 Testing Interview Service...');

    // Test health check
    const healthResponse = await this.axios.get(`${CONFIG.INTERVIEW_SERVICE_URL}/health`);
    expect(healthResponse.status).to.equal(200);

    // Test interview session creation
    const sessionResponse = await this.axios.post(`${CONFIG.INTERVIEW_SERVICE_URL}/interview/start`, {
      candidate_name: 'Test Candidate',
      job_title: 'Software Engineer',
      experience_level: 'mid'
    });
    expect(sessionResponse.status).to.equal(200);
    expect(sessionResponse.data).to.have.property('session_id');
    expect(sessionResponse.data).to.have.property('questions');

    console.log('✅ Interview Service tests passed');
    return sessionResponse.data;
  }

  async testWebSocketConnection() {
    console.log('\n🔌 Testing WebSocket Connection...');

    return new Promise((resolve, reject) => {
      const ws = new WebSocket(CONFIG.WEBSOCKET_URL);

      ws.on('open', () => {
        console.log('✅ WebSocket connection established');
        ws.close();
        resolve();
      });

      ws.on('error', (error) => {
        reject(new Error(`WebSocket connection failed: ${error.message}`));
      });

      // Timeout after 10 seconds
      setTimeout(() => {
        ws.close();
        reject(new Error('WebSocket connection timeout'));
      }, 10000);
    });
  }

  async testEndToEndInterviewFlow() {
    console.log('\n🚀 Testing End-to-End Interview Flow...');

    // 1. Start interview session
    const sessionData = await this.axios.post(`${CONFIG.INTERVIEW_SERVICE_URL}/interview/start`, {
      candidate_name: 'John Doe',
      job_title: 'Frontend Developer',
      experience_level: 'senior'
    });
    expect(sessionData.status).to.equal(200);
    const sessionId = sessionData.data.session_id;

    // 2. Get first question
    const questionResponse = await this.axios.get(`${CONFIG.INTERVIEW_SERVICE_URL}/interview/${sessionId}/question`);
    expect(questionResponse.status).to.equal(200);
    expect(questionResponse.data).to.have.property('question');
    expect(questionResponse.data).to.have.property('question_id');

    const question = questionResponse.data.question;
    console.log(`📝 Interview question: "${question}"`);

    // 3. Generate voice for the question
    const voiceData = await this.axios.post(`${CONFIG.VOICE_SERVICE_URL}/voice/tts`, {
      text: question,
      voice: 'lessac',
      extract_phonemes: true
    });
    expect(voiceData.status).to.equal(200);

    // 4. Test avatar renderer can handle the phonemes
    const avatarResponse = await this.axios.post(`${CONFIG.AVATAR_RENDERER_URL}/render`, {
      text: question,
      phonemes: voiceData.data.phonemes,
      avatar_url: 'https://models.readyplayer.me/64a0c6d1c3b6a8b4c8f0e0f0.glb'
    });
    expect(avatarResponse.status).to.equal(200);

    console.log('✅ End-to-end interview flow test passed');
    return { sessionId, question, voiceData: voiceData.data };
  }

  async testR3FFrontend() {
    console.log('\n🌐 Testing R3F Frontend...');

    // Test health check
    const healthResponse = await this.axios.get(`${CONFIG.R3F_FRONTEND_URL}/health`);
    expect(healthResponse.status).to.equal(200);

    // Test that the main page loads
    const pageResponse = await this.axios.get(CONFIG.R3F_FRONTEND_URL);
    expect(pageResponse.status).to.equal(200);
    expect(pageResponse.headers['content-type']).to.include('text/html');

    console.log('✅ R3F Frontend tests passed');
  }

  async runAllTests() {
    console.log('🧪 Starting Avatar Integration Tests...\n');

    try {
      // Wait for all services to be ready
      await this.waitForService(CONFIG.VOICE_SERVICE_URL, 'Voice Service');
      await this.waitForService(CONFIG.AVATAR_RENDERER_URL, 'Avatar Renderer');
      await this.waitForService(CONFIG.INTERVIEW_SERVICE_URL, 'Interview Service');
      await this.waitForService(CONFIG.R3F_FRONTEND_URL, 'R3F Frontend');

      // Run individual service tests
      await this.testVoiceService();
      await this.testAvatarRenderer();
      await this.testInterviewService();
      await this.testWebSocketConnection();
      await this.testR3FFrontend();

      // Run end-to-end flow test
      await this.testEndToEndInterviewFlow();

      console.log('\n🎉 All integration tests passed! Avatar system is fully functional.');
      return true;

    } catch (error) {
      console.error('\n❌ Integration tests failed:', error.message);
      throw error;
    }
  }
}

// Export for use in other test files
module.exports = { AvatarIntegrationTester };

// Run tests if this file is executed directly
if (require.main === module) {
  const tester = new AvatarIntegrationTester();
  tester.runAllTests()
    .then(() => {
      console.log('\n✅ All tests completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Tests failed:', error);
      process.exit(1);
    });
}
