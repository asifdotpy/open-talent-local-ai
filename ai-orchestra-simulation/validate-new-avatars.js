#!/usr/bin/env node

/**
 * Validate Newly Created Avatars with Morph Target Specifications
 */


const TEST_AVATARS = {
  'ARKit': '69189bc248062250a422e0f4',
  'Oculus': '69189bc448062250a422e128',
  'OVR': '69189bc61aa3af821aad1c51',
  'mouthShapes': '69189bc91aa3af821aad1c80',
  'visemes': '69189bcb28f4be8b0cdb7582',
  'ARKit,Oculus': '69189bcd672cca15c200f24d',
  'OVR,ARKit': '69189bcf672cca15c200f27b'
};

const REQUIRED_OCULUS_VISEMES = [
  'viseme_sil', 'viseme_PP', 'viseme_FF', 'viseme_TH', 'viseme_DD',
  'viseme_kk', 'viseme_CH', 'viseme_SS', 'viseme_nn', 'viseme_RR',
  'viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U'
];

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

function parseGLBMorphTargets(buffer) {
  try {
    const magic = buffer.readUInt32LE(0);
    if (magic !== 0x46546C67) {
      throw new Error('Not a valid GLB file');
    }

    const jsonChunkLength = buffer.readUInt32LE(12);
    const jsonChunkStart = 20;
    const jsonChunk = buffer.slice(jsonChunkStart, jsonChunkStart + jsonChunkLength);
    const gltf = JSON.parse(jsonChunk.toString('utf8'));

    const morphTargets = new Set();

    if (gltf.meshes) {
      for (const mesh of gltf.meshes) {
        if (mesh.primitives) {
          for (const primitive of mesh.primitives) {
            if (primitive.targets) {
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
    return [];
  }
}

async function validateAvatar(config, avatarId) {
  const url = `https://models.readyplayer.me/${avatarId}.glb`;

  log(colors.cyan, `\n🔍 Testing: ${config}`);
  log(colors.yellow, `   Avatar ID: ${avatarId}`);

  try {
    const response = await fetch(url);

    if (!response.ok) {
      log(colors.red, `   ❌ Failed: ${response.status}`);
      return null;
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const morphTargets = parseGLBMorphTargets(buffer);

    const oculusVisemes = morphTargets.filter(name =>
      name.toLowerCase().startsWith('viseme_')
    );

    const hasAllRequired = REQUIRED_OCULUS_VISEMES.every(viseme =>
      morphTargets.some(mt => mt.toLowerCase() === viseme.toLowerCase())
    );

    log(colors.green, `   ✅ Size: ${(buffer.length / 1024).toFixed(2)} KB`);
    log(colors.yellow, `   📊 Total morph targets: ${morphTargets.length}`);

    if (oculusVisemes.length > 0) {
      log(colors.green, `   ✅ Oculus visemes: ${oculusVisemes.length}/15`);
      console.log(`      ${oculusVisemes.join(', ')}`);
    } else {
      log(colors.red, `   ❌ No Oculus visemes found`);
    }

    if (hasAllRequired) {
      log(colors.bright + colors.green, `   🎉 ALL 15 REQUIRED VISEMES PRESENT!`);
    }

    // Show all morph targets
    if (morphTargets.length > 0 && morphTargets.length <= 20) {
      log(colors.cyan, `   📝 All morph targets:`);
      morphTargets.forEach((name, i) => {
        console.log(`      ${i + 1}. ${name}`);
      });
    }

    return {
      config,
      avatarId,
      morphTargets,
      oculusVisemes,
      hasAllRequired,
      size: buffer.length
    };

  } catch (error) {
    log(colors.red, `   ❌ Error: ${error.message}`);
    return null;
  }
}

async function main() {
  log(colors.bright, '\n🎭 Validating RPM Avatars with Morph Target Configs\n');
  log(colors.bright, '===================================================\n');

  const results = [];

  for (const [config, avatarId] of Object.entries(TEST_AVATARS)) {
    const result = await validateAvatar(config, avatarId);
    if (result) {
      results.push(result);
    }
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  // Summary
  log(colors.bright, '\n\n📊 Final Summary');
  log(colors.bright, '=================\n');

  const withVisemes = results.filter(r => r.oculusVisemes.length > 0);
  const fullyCompatible = results.filter(r => r.hasAllRequired);

  console.log(`Total Tested: ${results.length}`);
  console.log(`With Oculus Visemes: ${withVisemes.length}`);
  console.log(`Fully Compatible: ${fullyCompatible.length}\n`);

  if (fullyCompatible.length > 0) {
    log(colors.green, '🎉 FULLY COMPATIBLE AVATARS FOUND!\n');
    fullyCompatible.forEach(r => {
      console.log(`✅ Config: "${r.config}"`);
      console.log(`   ID: ${r.avatarId}`);
      console.log(`   URL: https://models.readyplayer.me/${r.avatarId}.glb`);
      console.log(`   Visemes: ${r.oculusVisemes.length}/15\n`);
    });

    log(colors.bright, '\n💡 NEXT STEPS:');
    console.log('1. Update rpmService.js with compatible avatar ID');
    console.log('2. Test lip-sync in browser');
    console.log('3. Create multiple avatars with this configuration');
    console.log('4. Remove fallback detection (no longer needed)\n');

  } else if (withVisemes.length > 0) {
    log(colors.yellow, '⚠️  PARTIAL VISEME SUPPORT:\n');
    withVisemes.forEach(r => {
      console.log(`Config: "${r.config}" - ${r.oculusVisemes.length}/15 visemes`);
      console.log(`   Missing: ${REQUIRED_OCULUS_VISEMES.filter(v =>
        !r.oculusVisemes.some(ov => ov.toLowerCase() === v.toLowerCase())
      ).join(', ')}\n`);
    });
  } else {
    log(colors.red, '❌ NO VISEME SUPPORT FOUND\n');
    console.log('All tested avatars only have basic morph targets:');
    results.forEach(r => {
      console.log(`  "${r.config}": ${r.morphTargets.join(', ')}`);
    });

    log(colors.yellow, '\n💡 RECOMMENDATIONS:');
    console.log('1. Continue using enhanced fallback avatar');
    console.log('2. Contact RPM support about Oculus viseme enablement');
    console.log('3. Request enterprise plan with custom morph targets');
    console.log('4. Current fallback detection works perfectly\n');
  }
}

main().catch(error => {
  log(colors.red, '\n❌ Fatal error:', error.message);
  process.exit(1);
});
