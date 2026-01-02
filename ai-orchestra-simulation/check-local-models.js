#!/usr/bin/env node

/**
 * Check local GLB models for Oculus viseme support
 */

import { readFileSync } from 'fs';
import { resolve } from 'path';

const MODELS = [
  'assets/models/LeePerrySmith.glb',
  'assets/models/metaHumanHead.glb',
  'assets/models/face.glb'
];

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
    console.error('Error parsing GLB:', error.message);
    return [];
  }
}

function checkModel(modelPath) {
  log(colors.cyan, `\n🔍 Checking: ${modelPath}`);

  try {
    const fullPath = resolve(modelPath);
    const buffer = readFileSync(fullPath);

    log(colors.green, `   ✅ Size: ${(buffer.length / 1024 / 1024).toFixed(2)} MB`);

    const morphTargets = parseGLBMorphTargets(buffer);

    if (morphTargets.length === 0) {
      log(colors.yellow, `   ⚠️  No morph targets found`);
      return null;
    }

    const oculusVisemes = morphTargets.filter(name =>
      name.toLowerCase().startsWith('viseme_')
    );

    const hasAllRequired = REQUIRED_OCULUS_VISEMES.every(viseme =>
      morphTargets.some(mt => mt.toLowerCase() === viseme.toLowerCase())
    );

    log(colors.yellow, `   📊 Total morph targets: ${morphTargets.length}`);

    if (oculusVisemes.length > 0) {
      log(colors.green, `   ✅ Oculus visemes: ${oculusVisemes.length}/15`);
    } else {
      log(colors.red, `   ❌ No Oculus visemes found`);
    }

    if (hasAllRequired) {
      log(colors.bright + colors.green, `   🎉 ALL 15 REQUIRED VISEMES PRESENT!`);
    }

    // Show all morph targets
    log(colors.cyan, `\n   📝 All morph targets:`);
    morphTargets.forEach((name, i) => {
      const isViseme = name.toLowerCase().startsWith('viseme_');
      const marker = isViseme ? '🗣️ ' : '   ';
      console.log(`      ${marker}${i + 1}. ${name}`);
    });

    return {
      path: modelPath,
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

log(colors.bright, '\n🎭 Local Model Viseme Checker\n');
log(colors.bright, '==============================\n');

const results = [];

for (const model of MODELS) {
  const result = checkModel(model);
  if (result) {
    results.push(result);
  }
}

// Summary
log(colors.bright, '\n\n📊 Summary');
log(colors.bright, '===========\n');

const fullyCompatible = results.filter(r => r.hasAllRequired);
const withVisemes = results.filter(r => r.oculusVisemes.length > 0);

console.log(`Models Checked: ${MODELS.length}`);
console.log(`Successfully Parsed: ${results.length}`);
console.log(`With Oculus Visemes: ${withVisemes.length}`);
console.log(`Fully Compatible: ${fullyCompatible.length}\n`);

if (fullyCompatible.length > 0) {
  log(colors.green, '🎉 MODELS WITH FULL VISEME SUPPORT:\n');
  fullyCompatible.forEach(r => {
    console.log(`✅ ${r.path}`);
    console.log(`   Size: ${(r.size / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   Morph Targets: ${r.morphTargets.length}`);
    console.log(`   Oculus Visemes: ${r.oculusVisemes.length}/15\n`);
  });

  log(colors.bright, '💡 RECOMMENDATION:');
  console.log('Use this model in Avatar.jsx for guaranteed lip-sync!\n');
  console.log('Update code:');
  console.log(`  url: '/${fullyCompatible[0].path}'\n`);

} else if (withVisemes.length > 0) {
  log(colors.yellow, '⚠️  MODELS WITH PARTIAL VISEME SUPPORT:\n');
  withVisemes.forEach(r => {
    console.log(`${r.path} - ${r.oculusVisemes.length}/15 visemes`);
  });
} else {
  log(colors.red, '❌ NO MODELS WITH VISEME SUPPORT FOUND\n');
}
