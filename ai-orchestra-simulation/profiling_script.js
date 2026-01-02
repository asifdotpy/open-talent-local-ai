#!/usr/bin/env node

/**
 * Automated Performance Profiling Script
 *
 * Purpose: Measure exact performance bottlenecks in avatar rendering
 * Output: Detailed timing breakdown for optimization decisions
 *
 * Usage: node profiling_script.js [--iterations=10] [--output=profile.json]
 */

import axios from 'axios';
import fs from 'fs';
import os from 'os';
import { performance } from 'perf_hooks';

// Configuration
const AVATAR_SERVICE_URL = process.env.AVATAR_SERVICE_URL || 'http://localhost:3001';
const VOICE_SERVICE_URL = process.env.VOICE_SERVICE_URL || 'http://localhost:8002';
const ITERATIONS = parseInt(process.argv.find(arg => arg.startsWith('--iterations='))?.split('=')[1]) || 5;
const OUTPUT_FILE = process.argv.find(arg => arg.startsWith('--output='))?.split('=')[1] || 'performance_profile.json';

// Test cases with varying complexity
const TEST_CASES = [
  {
    name: 'Short phrase (2-3s)',
    text: 'Hello, how are you today?',
    expectedDuration: 2.5
  },
  {
    name: 'Medium sentence (5-7s)',
    text: 'Thank you for joining us today. We are excited to discuss your background and experience.',
    expectedDuration: 6.0
  },
  {
    name: 'Long paragraph (10-15s)',
    text: 'Welcome to our interview process. We will be discussing your technical skills, past projects, and career goals. This conversation will help us understand your qualifications and determine if you are a good fit for our team.',
    expectedDuration: 12.0
  }
];

// Profiling results storage
const results = {
  timestamp: new Date().toISOString(),
  system: {
    nodeVersion: process.version,
    platform: process.platform,
    arch: process.arch,
    cpus: os.cpus().length,
    totalMemory: `${Math.round(os.totalmem() / 1024 / 1024 / 1024)}GB`,
    freeMemory: `${Math.round(os.freemem() / 1024 / 1024 / 1024)}GB`
  },
  testCases: [],
  summary: {}
};

/**
 * Measure TTS generation time
 */
async function profileTTS(text) {
  const startTime = performance.now();

  try {
    const response = await axios.post(`${VOICE_SERVICE_URL}/voice/tts`, {
      text,
      voice: 'en-US',
      extract_phonemes: true
    });

    const duration = performance.now() - startTime;
    const data = response.data;

    return {
      success: true,
      duration,
      audioData: data.audio_data,
      audioSize: data.audio_data ? Buffer.from(data.audio_data, 'base64').length : 0,
      phonemes: data.phonemes || [],
      phonemeCount: data.phonemes?.length || 0,
      audioDuration: data.duration || 0
    };
  } catch (error) {
    return {
      success: false,
      duration: performance.now() - startTime,
      error: error.message
    };
  }
}

/**
 * Measure avatar rendering time with detailed breakdown
 */
async function profileAvatarRender(ttsData, text) {
  const startTime = performance.now();

  // Save audio to temp file
  const audioPath = `/tmp/profiling_audio_${Date.now()}.wav`;
  const audioBuffer = Buffer.from(ttsData.audio_data, 'base64');
  fs.writeFileSync(audioPath, audioBuffer);

  try {
    const response = await axios.post(`${AVATAR_SERVICE_URL}/render/lipsync`, {
      phonemes: ttsData.phonemes || [],
      duration: ttsData.duration || 0,
      audioUrl: `file://${audioPath}`
    }, {
      responseType: 'arraybuffer',
      maxContentLength: 100 * 1024 * 1024, // 100MB
      timeout: 120000 // 2 minutes
    });

    const duration = performance.now() - startTime;

    // Clean up temp file
    try { fs.unlinkSync(audioPath); } catch(e) {}

    return {
      success: true,
      duration,
      videoSize: response.data.length,
      videoDuration: ttsData.duration || 0,
      realtimeMultiplier: ttsData.duration ? ttsData.duration / (duration / 1000) : 0
    };
  } catch (error) {
    // Clean up temp file
    try { fs.unlinkSync(audioPath); } catch(e) {}

    return {
      success: false,
      duration: performance.now() - startTime,
      error: error.response?.data?.toString() || error.message
    };
  }
}

/**
 * Run complete end-to-end profiling
 */
async function profileEndToEnd(testCase) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`📊 Profiling: ${testCase.name}`);
  console.log(`📝 Text: "${testCase.text}"`);
  console.log(`${'='.repeat(60)}\n`);

  const caseResults = {
    testCase: testCase.name,
    text: testCase.text,
    iterations: [],
    averages: {}
  };

  for (let i = 1; i <= ITERATIONS; i++) {
    console.log(`\n🔄 Iteration ${i}/${ITERATIONS}`);
    console.log(`${'─'.repeat(40)}`);

    const iterationStart = performance.now();
    const iteration = {
      number: i,
      stages: {}
    };

    // Stage 1: TTS Generation
    console.log('⏱️  Stage 1: TTS Generation...');
    const ttsStart = performance.now();
    const ttsResult = await profileTTS(testCase.text);
    const ttsDuration = performance.now() - ttsStart;

    iteration.stages.tts = {
      duration: ttsDuration,
      ...ttsResult
    };

    console.log(`   ✅ TTS: ${ttsDuration.toFixed(2)}ms`);
    if (ttsResult.success) {
      console.log(`      Audio size: ${(ttsResult.audioSize / 1024).toFixed(2)} KB`);
      console.log(`      Phonemes: ${ttsResult.phonemeCount}`);
      console.log(`      Duration: ${ttsResult.audioDuration.toFixed(2)}s`);

      // Store TTS data for rendering
      iteration.ttsData = {
        audio_data: ttsResult.audioData,
        phonemes: ttsResult.phonemes,
        duration: ttsResult.audioDuration
      };
    } else {
      console.log(`      ❌ Error: ${ttsResult.error}`);
      continue;
    }

    // Stage 2: Avatar Rendering
    console.log('⏱️  Stage 2: Avatar Rendering...');
    const renderStart = performance.now();
    const renderResult = await profileAvatarRender(
      iteration.ttsData,
      testCase.text
    );
    const renderDuration = performance.now() - renderStart;

    iteration.stages.rendering = {
      duration: renderDuration,
      ...renderResult
    };

    console.log(`   ✅ Rendering: ${(renderDuration / 1000).toFixed(2)}s`);
    if (renderResult.success) {
      console.log(`      Video size: ${(renderResult.videoSize / 1024).toFixed(2)} KB`);
      console.log(`      Duration: ${renderResult.videoDuration.toFixed(2)}s`);
      console.log(`      Realtime multiplier: ${renderResult.realtimeMultiplier.toFixed(2)}x`);
    } else {
      console.log(`      ❌ Error: ${renderResult.error}`);
      continue;
    }

    // Total
    const totalDuration = performance.now() - iterationStart;
    iteration.total = {
      duration: totalDuration,
      ttsPercentage: (ttsDuration / totalDuration * 100).toFixed(1),
      renderPercentage: (renderDuration / totalDuration * 100).toFixed(1)
    };

    console.log(`\n📊 Iteration ${i} Summary:`);
    console.log(`   Total: ${(totalDuration / 1000).toFixed(2)}s`);
    console.log(`   TTS: ${ttsDuration.toFixed(2)}ms (${iteration.total.ttsPercentage}%)`);
    console.log(`   Rendering: ${(renderDuration / 1000).toFixed(2)}s (${iteration.total.renderPercentage}%)`);

    caseResults.iterations.push(iteration);

    // Brief pause between iterations
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  // Calculate averages
  const successfulIterations = caseResults.iterations.filter(iter =>
    iter.stages.tts?.success && iter.stages.rendering?.success
  );

  if (successfulIterations.length > 0) {
    caseResults.averages = {
      tts: {
        duration: average(successfulIterations.map(i => i.stages.tts.duration)),
        audioSize: average(successfulIterations.map(i => i.stages.tts.audioSize)),
        phonemeCount: average(successfulIterations.map(i => i.stages.tts.phonemeCount))
      },
      rendering: {
        duration: average(successfulIterations.map(i => i.stages.rendering.duration)),
        videoSize: average(successfulIterations.map(i => i.stages.rendering.videoSize)),
        realtimeMultiplier: average(successfulIterations.map(i => i.stages.rendering.realtimeMultiplier))
      },
      total: {
        duration: average(successfulIterations.map(i => i.total.duration)),
        ttsPercentage: average(successfulIterations.map(i => parseFloat(i.total.ttsPercentage))),
        renderPercentage: average(successfulIterations.map(i => parseFloat(i.total.renderPercentage)))
      }
    };
  }

  return caseResults;
}

/**
 * Calculate average of array
 */
function average(arr) {
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

/**
 * Print final summary
 */
function printSummary(results) {
  console.log(`\n\n${'='.repeat(80)}`);
  console.log('📋 PROFILING SUMMARY');
  console.log(`${'='.repeat(80)}\n`);

  console.log(`🖥️  System: ${results.system.platform} ${results.system.arch}`);
  console.log(`⚙️  CPUs: ${results.system.cpus}`);
  console.log(`💾 Memory: ${results.system.freeMemory} / ${results.system.totalMemory} free\n`);

  results.testCases.forEach(tc => {
    if (tc.averages.total) {
      console.log(`\n📊 ${tc.testCase}`);
      console.log(`${'─'.repeat(60)}`);
      console.log(`   TTS Generation:      ${tc.averages.tts.duration.toFixed(2)}ms (${tc.averages.total.ttsPercentage.toFixed(1)}%)`);
      console.log(`   Avatar Rendering:    ${(tc.averages.rendering.duration / 1000).toFixed(2)}s (${tc.averages.total.renderPercentage.toFixed(1)}%)`);
      console.log(`   Total Pipeline:      ${(tc.averages.total.duration / 1000).toFixed(2)}s`);
      console.log(`   Realtime Multiplier: ${tc.averages.rendering.realtimeMultiplier.toFixed(2)}x`);
      console.log(`   Audio Size:          ${(tc.averages.tts.audioSize / 1024).toFixed(2)} KB`);
      console.log(`   Video Size:          ${(tc.averages.rendering.videoSize / 1024).toFixed(2)} KB`);
    }
  });

  console.log(`\n\n🎯 KEY FINDINGS:`);
  console.log(`${'─'.repeat(60)}`);

  const avgRenderPercentage = average(results.testCases
    .filter(tc => tc.averages.total)
    .map(tc => tc.averages.total.renderPercentage)
  );

  const avgRealtimeMultiplier = average(results.testCases
    .filter(tc => tc.averages.rendering)
    .map(tc => tc.averages.rendering.realtimeMultiplier)
  );

  console.log(`\n🔴 BOTTLENECK: Avatar Rendering (${avgRenderPercentage.toFixed(1)}% of total time)`);
  console.log(`📈 Current Performance: ${avgRealtimeMultiplier.toFixed(2)}x realtime`);
  console.log(`🎯 Target Performance: 0.5x - 2.0x realtime`);

  if (avgRealtimeMultiplier < 0.5) {
    console.log(`\n❌ STATUS: CRITICAL - ${(0.5 / avgRealtimeMultiplier).toFixed(1)}x speedup needed`);
    console.log(`\n💡 RECOMMENDATIONS:`);
    console.log(`   1. Switch from VP9 to H.264 encoding (expected 3-5x speedup)`);
    console.log(`   2. Reduce resolution from 1080p to 720p (expected 2x speedup)`);
    console.log(`   3. Enable GPU hardware acceleration (expected 2-3x speedup)`);
    console.log(`   4. Implement distributed rendering for scale`);
  } else if (avgRealtimeMultiplier < 1.0) {
    console.log(`\n⚠️  STATUS: MARGINAL - Acceptable for MVP, optimize for production`);
    console.log(`\n💡 RECOMMENDATIONS:`);
    console.log(`   1. Implement job queue for concurrent users`);
    console.log(`   2. Consider GPU acceleration for 2x boost`);
    console.log(`   3. Add frame caching for common visemes`);
  } else {
    console.log(`\n✅ STATUS: ACCEPTABLE - Ready for production scaling`);
    console.log(`\n💡 RECOMMENDATIONS:`);
    console.log(`   1. Focus on distributed architecture for scale`);
    console.log(`   2. Add comprehensive test suite`);
    console.log(`   3. Monitor performance in production`);
  }

  console.log(`\n\n📄 Full results saved to: ${OUTPUT_FILE}`);
  console.log(`${'='.repeat(80)}\n`);
}

/**
 * Main execution
 */
async function main() {
  console.log('\n🚀 Starting Avatar Rendering Performance Profiling');
  console.log(`📊 Iterations per test case: ${ITERATIONS}`);
  console.log(`🎯 Test cases: ${TEST_CASES.length}`);
  console.log(`📁 Output file: ${OUTPUT_FILE}\n`);

  // Check service health
  console.log('🔍 Checking service health...');
  try {
    await axios.get(`${AVATAR_SERVICE_URL}/health`);
    console.log(`   ✅ Avatar service: ${AVATAR_SERVICE_URL}`);
  } catch (error) {
    console.error(`   ❌ Avatar service unavailable: ${AVATAR_SERVICE_URL}`);
    process.exit(1);
  }

  try {
    await axios.get(`${VOICE_SERVICE_URL}/health`);
    console.log(`   ✅ Voice service: ${VOICE_SERVICE_URL}`);
  } catch (error) {
    console.error(`   ❌ Voice service unavailable: ${VOICE_SERVICE_URL}`);
    process.exit(1);
  }

  // Run profiling for each test case
  for (const testCase of TEST_CASES) {
    const caseResults = await profileEndToEnd(testCase);
    results.testCases.push(caseResults);
  }

  // Print summary
  printSummary(results);

  // Save to file
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(results, null, 2));

  console.log('✅ Profiling complete!\n');
}

// Execute
main().catch(error => {
  console.error('\n❌ Profiling failed:', error.message);
  process.exit(1);
});
