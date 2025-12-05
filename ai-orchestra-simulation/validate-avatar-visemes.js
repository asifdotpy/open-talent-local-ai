#!/usr/bin/env node

/**
 * Avatar Viseme Validator
 * Downloads and checks if RPM avatars have Oculus visemes
 */

import { writeFileSync } from 'fs';

const REQUIRED_OCULUS_VISEMES = [
  'viseme_sil', 'viseme_PP', 'viseme_FF', 'viseme_TH', 'viseme_DD',
  'viseme_kk', 'viseme_CH', 'viseme_SS', 'viseme_nn', 'viseme_RR',
  'viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U'
];

const TEST_AVATARS = [
  '69189b39672cca15c200e6be', // Just created - halfbody female
  '69189b3b5f9f523e50143aba', // Just created - halfbody female
  '69189b3b7b7a88e1f6d7e3ea', // Just created - fullbody female
  '6916fff248062250a407130a', // Current working avatar
  '64bfa619f72e7b8e17f6b8c7', // Fallback Marcus
  '65a8dba831b23abb4f401bae', // Fallback Alex
];

// Color output helpers
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
};

function log(color, ...args) {
  console.log(color, ...args, colors.reset);
}

/**
 * Parse GLB binary and extract morph target names
 * GLB format: 12-byte header + JSON chunk + Binary chunk
 */
function parseGLBMorphTargets(buffer) {
  try {
    // Read GLB header
    const magic = buffer.readUInt32LE(0);
    if (magic !== 0x46546C67) { // 'glTF' in little-endian
      throw new Error('Not a valid GLB file');
    }

    // Read JSON chunk
    const jsonChunkLength = buffer.readUInt32LE(12);
    const jsonChunkStart = 20;
    const jsonChunk = buffer.slice(jsonChunkStart, jsonChunkStart + jsonChunkLength);
    const gltf = JSON.parse(jsonChunk.toString('utf8'));

    // Extract morph targets from all meshes
    const morphTargets = new Set();
    
    if (gltf.meshes) {
      for (const mesh of gltf.meshes) {
        if (mesh.primitives) {
          for (const primitive of mesh.primitives) {
            if (primitive.targets) {
              // Targets are in extras.targetNames
              if (mesh.extras && mesh.extras.targetNames) {
                mesh.extras.targetNames.forEach(name => morphTargets.add(name));
              }
            }
          }
        }
      }
    }

    return Array.from(morphTargets);
  } catch (error) {
    console.error('Error parsing GLB:', error.message);
    return [];
  }
}

async function validateAvatar(avatarId) {
  const url = `https://models.readyplayer.me/${avatarId}.glb`;
  
  log(colors.cyan, `\n🔍 Testing Avatar: ${avatarId}`);
  log(colors.yellow, `   URL: ${url}`);

  try {
    // Download GLB file
    const response = await fetch(url);
    
    if (!response.ok) {
      log(colors.red, `   ❌ Download failed: ${response.status} ${response.statusText}`);
      return { avatarId, success: false, error: `HTTP ${response.status}` };
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    
    log(colors.green, `   ✅ Downloaded: ${(buffer.length / 1024).toFixed(2)} KB`);

    // Parse morph targets
    const morphTargets = parseGLBMorphTargets(buffer);
    
    if (morphTargets.length === 0) {
      log(colors.yellow, `   ⚠️  No morph targets found (might need different parsing)`);
      
      // Try alternative: save and inspect manually
      const filename = `/tmp/avatar_${avatarId}.glb`;
      writeFileSync(filename, buffer);
      log(colors.yellow, `   💾 Saved to: ${filename}`);
      log(colors.yellow, `   ℹ️  Use Blender or GLB viewer to inspect morph targets`);
      
      return { 
        avatarId, 
        success: false, 
        morphTargets: [],
        savedPath: filename,
        note: 'Manual inspection needed'
      };
    }

    // Check for Oculus visemes
    const foundOculusVisemes = morphTargets.filter(name => 
      name.toLowerCase().includes('viseme_')
    );

    const hasAllRequiredVisemes = REQUIRED_OCULUS_VISEMES.every(viseme =>
      morphTargets.some(mt => mt.toLowerCase() === viseme.toLowerCase())
    );

    log(colors.bright, `\n   📊 Morph Target Analysis:`);
    log(colors.yellow, `      Total morph targets: ${morphTargets.length}`);
    log(colors.yellow, `      Oculus visemes found: ${foundOculusVisemes.length}/15`);
    
    if (foundOculusVisemes.length > 0) {
      log(colors.green, `      ✅ Has visemes: ${foundOculusVisemes.join(', ')}`);
    }

    if (hasAllRequiredVisemes) {
      log(colors.green, `      ✅ ALL REQUIRED VISEMES PRESENT!`);
    } else {
      const missing = REQUIRED_OCULUS_VISEMES.filter(viseme =>
        !morphTargets.some(mt => mt.toLowerCase() === viseme.toLowerCase())
      );
      log(colors.red, `      ❌ Missing visemes: ${missing.join(', ')}`);
    }

    // Show some example morph targets
    log(colors.cyan, `\n   📝 Sample morph targets (first 10):`);
    morphTargets.slice(0, 10).forEach((name, i) => {
      console.log(`      ${i + 1}. ${name}`);
    });
    if (morphTargets.length > 10) {
      console.log(`      ... and ${morphTargets.length - 10} more`);
    }

    return {
      avatarId,
      success: true,
      morphTargets,
      oculusVisemes: foundOculusVisemes,
      hasAllRequired: hasAllRequiredVisemes,
      coverage: (foundOculusVisemes.length / REQUIRED_OCULUS_VISEMES.length * 100).toFixed(1)
    };

  } catch (error) {
    log(colors.red, `   ❌ Error: ${error.message}`);
    return { avatarId, success: false, error: error.message };
  }
}

async function main() {
  log(colors.bright, '\n🎭 Avatar Viseme Validator\n');
  log(colors.bright, '==========================\n');
  
  log(colors.cyan, `Testing ${TEST_AVATARS.length} avatars...\n`);

  const results = [];
  
  for (const avatarId of TEST_AVATARS) {
    const result = await validateAvatar(avatarId);
    results.push(result);
    
    // Small delay between requests
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  // Summary
  log(colors.bright, '\n\n📊 Validation Summary');
  log(colors.bright, '=====================\n');

  const successful = results.filter(r => r.success);
  const withVisemes = results.filter(r => r.success && r.oculusVisemes && r.oculusVisemes.length > 0);
  const fullyCompatible = results.filter(r => r.success && r.hasAllRequired);

  console.log(`Total Avatars Tested: ${results.length}`);
  console.log(`Successfully Downloaded: ${successful.length}/${results.length}`);
  console.log(`With Oculus Visemes: ${withVisemes.length}/${successful.length}`);
  console.log(`Fully Compatible (All 15 visemes): ${fullyCompatible.length}/${successful.length}\n`);

  if (fullyCompatible.length > 0) {
    log(colors.green, '✅ Avatars with FULL viseme support:');
    fullyCompatible.forEach(r => {
      console.log(`   • ${r.avatarId} (${r.coverage}% coverage)`);
      console.log(`     URL: https://models.readyplayer.me/${r.avatarId}.glb`);
    });
  } else {
    log(colors.yellow, '\n⚠️  No avatars found with complete Oculus viseme support');
  }

  if (withVisemes.length > 0 && fullyCompatible.length === 0) {
    log(colors.yellow, '\n⚠️  Avatars with partial viseme support:');
    withVisemes.forEach(r => {
      console.log(`   • ${r.avatarId} (${r.coverage}% coverage - ${r.oculusVisemes.length}/15 visemes)`);
    });
  }

  // Recommendations
  log(colors.bright, '\n\n💡 Recommendations:');
  if (fullyCompatible.length > 0) {
    console.log('  ✅ Use one of the fully compatible avatars in your app');
    console.log('  ✅ Update rpmService.js with the compatible avatar ID');
  } else if (withVisemes.length > 0) {
    console.log('  ⚠️  Current avatars have partial viseme support');
    console.log('  💡 Consider using fallback avatar for guaranteed lip-sync');
    console.log('  💡 Or create custom RPM avatars with viseme requirements');
  } else {
    console.log('  ❌ No avatars found with viseme support');
    console.log('  ✅ Use enhanced fallback avatar (guaranteed 15 visemes)');
    console.log('  💡 Request RPM support to enable morph targets on templates');
  }

  console.log('\n');
}

main().catch(error => {
  log(colors.red, '\n❌ Fatal error:', error.message);
  process.exit(1);
});
