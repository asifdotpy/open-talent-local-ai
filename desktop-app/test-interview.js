#!/usr/bin/env node

/**
 * Test script for Interview Service
 * This tests the Ollama integration without needing the full Electron app
 */

const { InterviewService } = require('./dist/services/interview-service');

async function testInterviewService() {
  console.log('🔍 Testing OpenTalent Interview Service\n');

  const service = new InterviewService('http://localhost:11434');

  // Test 1: Check Ollama status
  console.log('Test 1: Checking Ollama status...');
  const status = await service.checkStatus();
  console.log(`✅ Ollama status: ${status ? 'ONLINE' : 'OFFLINE'}\n`);

  if (!status) {
    console.error('❌ Ollama is not running. Please start Ollama first.');
    process.exit(1);
  }

  // Test 2: List available models
  console.log('Test 2: Listing available models...');
  const models = await service.listModels();
  console.log(`✅ Found ${models.length} model(s):`);
  models.forEach((model) => console.log(`   - ${model.name}`));
  console.log('');

  if (models.length === 0) {
    console.error('❌ No models found. Please pull a model first (e.g., ollama pull llama3.2:1b)');
    process.exit(1);
  }

  // Test 3: Start an interview
  console.log('Test 3: Starting a Software Engineer interview...');
  // Try custom 2B model first, fall back to 1B if not available
  const modelToUse = models.some(m => m.name === 'vetta-granite-2b-gguf-v4')
    ? 'vetta-granite-2b-gguf-v4'
    : 'llama3.2:1b';

  console.log(`   Using model: ${modelToUse}`);
  const session = await service.startInterview('Software Engineer', modelToUse, 5);
  console.log(`✅ Interview started successfully!`);
  console.log(`   Role: ${session.config.role}`);
  console.log(`   Model: ${session.config.model}`);
  console.log(`   Total Questions: ${session.config.totalQuestions}`);
  console.log(`   Current Question: ${session.currentQuestion}\n`);

  // Display first question
  const firstQuestion = session.messages[session.messages.length - 1];
  console.log('📋 First Question from AI Interviewer:');
  console.log('═══════════════════════════════════════════════════════════');
  console.log(firstQuestion.content);
  console.log('═══════════════════════════════════════════════════════════\n');

  // Test 4: Send a response
  console.log('Test 4: Sending a sample response...');
  const sampleResponse = 'I have experience with arrays, linked lists, trees, and hash tables. I recently used a hash table to optimize a search algorithm from O(n) to O(1) lookup time.';
  console.log(`💬 Candidate Response: "${sampleResponse}"\n`);

  const updatedSession = await service.sendResponse(session, sampleResponse);
  console.log(`✅ Response processed successfully!`);
  console.log(`   Current Question: ${updatedSession.currentQuestion}/${updatedSession.config.totalQuestions}`);
  console.log(`   Interview Complete: ${updatedSession.isComplete ? 'Yes' : 'No'}\n`);

  // Display AI's response
  const aiResponse = updatedSession.messages[updatedSession.messages.length - 1];
  console.log('🤖 AI Interviewer Response:');
  console.log('═══════════════════════════════════════════════════════════');
  console.log(aiResponse.content);
  console.log('═══════════════════════════════════════════════════════════\n');

  // Test 5: Get interview summary
  console.log('Test 5: Getting interview summary...');
  const summary = service.getInterviewSummary(updatedSession);
  console.log('📊 Interview Summary:');
  console.log('═══════════════════════════════════════════════════════════');
  console.log(summary);
  console.log('═══════════════════════════════════════════════════════════\n');

  console.log('✅ All tests passed! Interview service is working correctly.\n');
  console.log('🎉 You can now run the full Electron app with: npm run dev');
}

// Run the tests
testInterviewService().catch((error) => {
  console.error('\n❌ Error during testing:', error.message);
  process.exit(1);
});
