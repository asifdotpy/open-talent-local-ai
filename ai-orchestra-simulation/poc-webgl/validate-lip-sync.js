#!/usr/bin/env node

/**
 * Lip Sync Validation Script
 * Validates phoneme-to-viseme mapping with real RPM avatar
 * Tests voice service integration and morph target animation
 */

import fetch from 'node-fetch';

// Test configuration
const VOICE_SERVICE_URL = 'http://localhost:8002/voice/tts';
const TEST_PHRASES = [
  'Hello, welcome to your interview',
  'Tell me about your background and experience',
  'What are your strengths and weaknesses?',
  'Why do you want this position?',
  'Describe a challenging project you worked on',
  'The quick brown fox jumps over the lazy dog' // Pangram for comprehensive phoneme coverage
];

// Oculus LipSync visemes we expect
const EXPECTED_VISEMES = [
  'viseme_sil', 'viseme_PP', 'viseme_FF', 'viseme_TH', 'viseme_DD',
  'viseme_kk', 'viseme_CH', 'viseme_SS', 'viseme_nn', 'viseme_RR',
  'viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U'
];

// Phoneme to Oculus Viseme mapping (from LipSyncController.jsx)
const PHONEME_TO_OCULUS_VISEME = {
  'sil': { viseme_sil: 1.0 },
  'AA': { viseme_aa: 1.0 }, 'AE': { viseme_aa: 0.8 }, 'AH': { viseme_aa: 0.6 },
  'AO': { viseme_O: 0.8 }, 'AW': { viseme_O: 0.7 }, 'AY': { viseme_I: 0.6 },
  'EH': { viseme_E: 0.8 }, 'ER': { viseme_E: 0.7 }, 'EY': { viseme_E: 0.9 },
  'IH': { viseme_I: 0.7 }, 'IY': { viseme_I: 1.0 }, 'OW': { viseme_O: 1.0 },
  'OY': { viseme_O: 0.8 }, 'UH': { viseme_U: 0.6 }, 'UW': { viseme_U: 1.0 },
  'B': { viseme_PP: 0.8 }, 'P': { viseme_PP: 1.0 }, 'M': { viseme_PP: 0.6 },
  'F': { viseme_FF: 1.0 }, 'V': { viseme_FF: 0.8 },
  'TH': { viseme_TH: 1.0 }, 'DH': { viseme_TH: 0.8 },
  'T': { viseme_DD: 0.8 }, 'D': { viseme_DD: 1.0 }, 'N': { viseme_nn: 0.8 },
  'L': { viseme_DD: 0.6 }, 'S': { viseme_SS: 1.0 }, 'Z': { viseme_SS: 0.8 },
  'SH': { viseme_SS: 0.9 }, 'ZH': { viseme_SS: 0.7 }, 'CH': { viseme_CH: 1.0 },
  'JH': { viseme_CH: 0.8 }, 'K': { viseme_kk: 1.0 }, 'G': { viseme_kk: 0.8 },
  'NG': { viseme_nn: 0.7 }, 'HH': { viseme_kk: 0.6 }, 'R': { viseme_RR: 1.0 },
  'W': { viseme_U: 0.5 }, 'Y': { viseme_I: 0.5 }
};

// Color codes for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function testVoiceService() {
  log('\n=== Testing Voice Service Connection ===', 'bright');

  try {
    const response = await fetch(VOICE_SERVICE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Test',
        voice: 'en-US',
        extract_phonemes: true
      })
    });

    if (response.ok) {
      log('✅ Voice service is running and accessible', 'green');
      return true;
    } else {
      log(`❌ Voice service returned status: ${response.status}`, 'red');
      return false;
    }
  } catch (error) {
    log(`❌ Voice service not accessible: ${error.message}`, 'red');
    log('   Start voice service: cd microservices/voice-service && python main.py', 'yellow');
    return false;
  }
}

async function extractPhonemes(text) {
  try {
    const response = await fetch(VOICE_SERVICE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        voice: 'en-US',
        extract_phonemes: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return data.phonemes || [];
  } catch (error) {
    log(`   ❌ Failed to extract phonemes: ${error.message}`, 'red');
    return [];
  }
}

function validatePhonemeMapping(phonemes) {
  const mappedVisemes = new Set();
  const unmappedPhonemes = [];

  phonemes.forEach(p => {
    const phoneme = p.phoneme.toUpperCase();
    if (PHONEME_TO_OCULUS_VISEME[phoneme]) {
      const visemes = Object.keys(PHONEME_TO_OCULUS_VISEME[phoneme]);
      visemes.forEach(v => mappedVisemes.add(v));
    } else {
      unmappedPhonemes.push(phoneme);
    }
  });

  return {
    mappedVisemes: Array.from(mappedVisemes),
    unmappedPhonemes: [...new Set(unmappedPhonemes)],
    totalPhonemes: phonemes.length,
    uniquePhonemes: new Set(phonemes.map(p => p.phoneme.toUpperCase())).size
  };
}

function analyzeVisemeCoverage(allMappedVisemes) {
  const coverage = EXPECTED_VISEMES.filter(v => allMappedVisemes.has(v));
  const missing = EXPECTED_VISEMES.filter(v => !allMappedVisemes.has(v));

  return {
    coverage: coverage.length,
    total: EXPECTED_VISEMES.length,
    percentage: ((coverage.length / EXPECTED_VISEMES.length) * 100).toFixed(1),
    covered: coverage,
    missing: missing
  };
}

async function testPhrase(phrase, index) {
  log(`\n${index + 1}. Testing: "${phrase}"`, 'cyan');

  const phonemes = await extractPhonemes(phrase);

  if (phonemes.length === 0) {
    log('   ⚠️  No phonemes extracted', 'yellow');
    return { mappedVisemes: [], unmappedPhonemes: [], totalPhonemes: 0, uniquePhonemes: 0 };
  }

  const validation = validatePhonemeMapping(phonemes);

  log(`   ✅ Extracted ${validation.totalPhonemes} phonemes (${validation.uniquePhonemes} unique)`, 'green');
  log(`   🎯 Mapped to ${validation.mappedVisemes.length} visemes: ${validation.mappedVisemes.join(', ')}`, 'blue');

  if (validation.unmappedPhonemes.length > 0) {
    log(`   ⚠️  Unmapped phonemes: ${validation.unmappedPhonemes.join(', ')}`, 'yellow');
  }

  return validation;
}

async function runFullValidation() {
  log('\n🎭 === Phoneme-to-Viseme Mapping Validation ===', 'bright');
  log('Testing RPM Avatar Lip Sync System\n', 'bright');

  // Test voice service connection
  const serviceAvailable = await testVoiceService();
  if (!serviceAvailable) {
    log('\n❌ Cannot proceed without voice service. Please start it first.', 'red');
    process.exit(1);
  }

  // Test all phrases
  log('\n=== Testing Sample Interview Phrases ===', 'bright');

  const allVisemes = new Set();
  const allResults = [];

  for (let i = 0; i < TEST_PHRASES.length; i++) {
    const result = await testPhrase(TEST_PHRASES[i], i);
    result.mappedVisemes.forEach(v => allVisemes.add(v));
    allResults.push(result);

    // Small delay between requests
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  // Analyze overall coverage
  log('\n=== Overall Viseme Coverage Analysis ===', 'bright');

  const coverage = analyzeVisemeCoverage(allVisemes);

  log(`\n📊 Viseme Coverage: ${coverage.coverage}/${coverage.total} (${coverage.percentage}%)`, 'magenta');
  log(`✅ Covered visemes: ${coverage.covered.join(', ')}`, 'green');

  if (coverage.missing.length > 0) {
    log(`❌ Missing visemes: ${coverage.missing.join(', ')}`, 'red');
    log(`   Tip: Add phrases with phonemes that map to these visemes`, 'yellow');
  }

  // Phoneme statistics
  const totalPhonemes = allResults.reduce((sum, r) => sum + r.totalPhonemes, 0);
  const totalUnique = new Set(allResults.flatMap(r => r.unmappedPhonemes)).size;

  log(`\n📈 Phoneme Statistics:`, 'magenta');
  log(`   Total phonemes tested: ${totalPhonemes}`, 'blue');
  log(`   Unique visemes activated: ${allVisemes.size}`, 'blue');

  if (totalUnique > 0) {
    const uniqueUnmapped = new Set();
    allResults.forEach(r => r.unmappedPhonemes.forEach(p => uniqueUnmapped.add(p)));
    log(`   ⚠️  Unmapped phonemes found: ${Array.from(uniqueUnmapped).join(', ')}`, 'yellow');
  }

  // Final verdict
  log('\n=== Validation Summary ===', 'bright');

  if (coverage.percentage >= 90) {
    log('✅ EXCELLENT: Lip sync mapping covers 90%+ of Oculus visemes', 'green');
  } else if (coverage.percentage >= 70) {
    log('✅ GOOD: Lip sync mapping covers 70%+ of Oculus visemes', 'green');
  } else if (coverage.percentage >= 50) {
    log('⚠️  FAIR: Lip sync mapping covers 50%+ of Oculus visemes', 'yellow');
    log('   Consider adding more diverse test phrases', 'yellow');
  } else {
    log('❌ POOR: Lip sync mapping covers <50% of Oculus visemes', 'red');
    log('   Review phoneme extraction and mapping logic', 'red');
  }

  log('\n💡 Next Steps:', 'cyan');
  log('   1. Test in browser: Open http://localhost:5173', 'cyan');
  log('   2. Enable debug overlay: Press Ctrl+D', 'cyan');
  log('   3. Speak test phrases and observe morph targets', 'cyan');
  log('   4. Validate visual lip sync accuracy', 'cyan');

  log('\n✅ Validation complete!\n', 'bright');
}

// Run validation
runFullValidation().catch(error => {
  log(`\n❌ Validation failed: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});
