/**
 * Voice Integration Test
 * Tests the end-to-end voice service integration
 */

const testVoiceIntegration = async () => {
  console.log('🧪 Testing voice service integration...');

  try {
    const response = await fetch('http://localhost:8002/voice/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Hello, welcome to your interview!',
        voice: 'lessac',
        extract_phonemes: true
      })
    });

    if (!response.ok) {
      throw new Error('HTTP ' + response.status);
    }

    const data = await response.json();
    console.log('✅ Voice service response:');
    console.log('   Audio data length:', data.audio_data?.length || 0);
    console.log('   Phonemes count:', data.phonemes?.length || 0);
    console.log('   Duration:', data.duration);
    console.log('   Sample rate:', data.sample_rate);

    if (data.phonemes && data.phonemes.length > 0) {
      console.log('   First phoneme:', data.phonemes[0]);
    }

    console.log('🎉 Voice integration test PASSED!');
  } catch (error) {
    console.error('❌ Voice integration test FAILED:', error.message);
  }
};

testVoiceIntegration();
