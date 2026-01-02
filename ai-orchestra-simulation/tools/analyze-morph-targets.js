#!/usr/bin/env node
/**
 * Morph Target Analyzer for face.glb
 *
 * Analyzes the 52 morph targets in face.glb to identify which indices
 * correspond to which phoneme shapes by examining vertex displacement patterns.
 *
 * Strategy:
 * 1. Load face.glb with all morph target data
 * 2. For each morph target (0-51), analyze vertex displacements
 * 3. Identify patterns characteristic of jaw/mouth movements
 * 4. Generate mapping suggestions based on displacement analysis
 */

import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import * as fs from 'fs';
import { MeshoptDecoder } from 'meshoptimizer';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to face.glb
const MODEL_PATH = path.join(__dirname, '../assets/models/face.glb');

// ANSI colors
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * Analyze vertex displacement pattern for a morph target
 */
function analyzeMorphTargetDisplacement(originalPositions, morphPositions) {
  const vertexCount = originalPositions.length / 3;

  let totalDisplacement = 0;
  let maxDisplacement = 0;
  let verticalDisplacement = 0; // Y-axis
  let horizontalDisplacement = 0; // X-axis
  let depthDisplacement = 0; // Z-axis

  let mouthRegionDisplacement = 0;
  let jawRegionDisplacement = 0;
  let upperFaceDisplacement = 0;

  const displacements = [];

  for (let i = 0; i < vertexCount; i++) {
    const idx = i * 3;

    const origX = originalPositions[idx];
    const origY = originalPositions[idx + 1];
    const origZ = originalPositions[idx + 2];

    const morphX = morphPositions[idx];
    const morphY = morphPositions[idx + 1];
    const morphZ = morphPositions[idx + 2];

    const dx = morphX - origX;
    const dy = morphY - origY;
    const dz = morphZ - origZ;

    const displacement = Math.sqrt(dx * dx + dy * dy + dz * dz);

    totalDisplacement += displacement;
    maxDisplacement = Math.max(maxDisplacement, displacement);

    verticalDisplacement += Math.abs(dy);
    horizontalDisplacement += Math.abs(dx);
    depthDisplacement += Math.abs(dz);

    // Categorize by face region (approximate Y-coordinates)
    if (origY >= 8500 && origY <= 9500) {
      // Mouth region
      mouthRegionDisplacement += displacement;
    } else if (origY >= 8000 && origY < 8500) {
      // Jaw region
      jawRegionDisplacement += displacement;
    } else if (origY > 9500) {
      // Upper face (eyes, forehead)
      upperFaceDisplacement += displacement;
    }

    if (displacement > 10) { // Significant displacement
      displacements.push({
        vertexIndex: i,
        x: origX,
        y: origY,
        z: origZ,
        dx,
        dy,
        dz,
        magnitude: displacement,
      });
    }
  }

  const avgDisplacement = totalDisplacement / vertexCount;

  return {
    totalDisplacement,
    avgDisplacement,
    maxDisplacement,
    verticalDisplacement,
    horizontalDisplacement,
    depthDisplacement,
    mouthRegionDisplacement,
    jawRegionDisplacement,
    upperFaceDisplacement,
    significantVertices: displacements.length,
    topDisplacements: displacements.sort((a, b) => b.magnitude - a.magnitude).slice(0, 10),
  };
}

/**
 * Classify morph target based on displacement pattern
 */
function classifyMorphTarget(analysis) {
  const {
    avgDisplacement,
    verticalDisplacement,
    horizontalDisplacement,
    depthDisplacement,
    mouthRegionDisplacement,
    jawRegionDisplacement,
    upperFaceDisplacement,
  } = analysis;

  const totalRegionDisplacement = mouthRegionDisplacement + jawRegionDisplacement + upperFaceDisplacement;

  // Calculate region percentages
  const mouthPct = (mouthRegionDisplacement / totalRegionDisplacement) * 100;
  const jawPct = (jawRegionDisplacement / totalRegionDisplacement) * 100;
  const upperPct = (upperFaceDisplacement / totalRegionDisplacement) * 100;

  // Calculate axis percentages
  const totalAxisDisplacement = verticalDisplacement + horizontalDisplacement + depthDisplacement;
  const verticalPct = (verticalDisplacement / totalAxisDisplacement) * 100;
  const horizontalPct = (horizontalDisplacement / totalAxisDisplacement) * 100;
  const depthPct = (depthDisplacement / totalAxisDisplacement) * 100;

  let category = 'unknown';
  let suggestedPhoneme = null;
  let confidence = 0;

  // Classification logic based on displacement patterns
  if (avgDisplacement < 5) {
    category = 'minimal';
    confidence = 0.9;
  } else if (mouthPct > 60 && verticalPct > 50) {
    category = 'jaw-vertical';
    suggestedPhoneme = 'jawOpen';
    confidence = 0.8;
  } else if (mouthPct > 60 && horizontalPct > 50) {
    category = 'mouth-horizontal';
    suggestedPhoneme = 'mouthSmile';
    confidence = 0.7;
  } else if (mouthPct > 60 && depthPct > 50) {
    category = 'mouth-depth';
    suggestedPhoneme = 'mouthFunnel';
    confidence = 0.7;
  } else if (jawPct > 50) {
    category = 'jaw-movement';
    suggestedPhoneme = 'jawOpen';
    confidence = 0.6;
  } else if (upperPct > 50) {
    category = 'upper-face';
    confidence = 0.7;
  } else {
    category = 'mixed';
    confidence = 0.3;
  }

  return {
    category,
    suggestedPhoneme,
    confidence,
    regionDistribution: {
      mouth: mouthPct.toFixed(1),
      jaw: jawPct.toFixed(1),
      upper: upperPct.toFixed(1),
    },
    axisDistribution: {
      vertical: verticalPct.toFixed(1),
      horizontal: horizontalPct.toFixed(1),
      depth: depthPct.toFixed(1),
    },
  };
}

/**
 * Main analysis function
 */
async function main() {
  log('🔍 Face.glb Morph Target Analyzer', 'bright');
  log('Analyzing 52 morph targets to identify phoneme mappings\n', 'cyan');

  // Initialize meshopt decoder
  await MeshoptDecoder.ready;

  // Initialize gltf-transform with all extensions
  const io = new NodeIO()
    .registerExtensions(ALL_EXTENSIONS)
    .registerDependencies({
      'meshopt.decoder': MeshoptDecoder,
    });

  log('📂 Loading face.glb...', 'blue');
  const document = await io.read(MODEL_PATH);

  const root = document.getRoot();
  const meshes = root.listMeshes();

  log(`✅ Loaded ${meshes.length} meshes\n`, 'green');

  // Find mesh with morph targets (should be mesh index 2)
  let targetMesh = null;
  let targetPrimitive = null;

  for (const mesh of meshes) {
    const primitives = mesh.listPrimitives();
    for (const primitive of primitives) {
      const targets = primitive.listTargets();
      if (targets.length > 0) {
        targetMesh = mesh;
        targetPrimitive = primitive;
        log(`✅ Found morph target mesh with ${targets.length} targets\n`, 'green');
        break;
      }
    }
    if (targetMesh) break;
  }

  if (!targetMesh || !targetPrimitive) {
    log('❌ No morph targets found!', 'red');
    process.exit(1);
  }

  // Get original vertex positions
  const positionAccessor = targetPrimitive.getAttribute('POSITION');
  const originalPositions = positionAccessor.getArray();
  const vertexCount = originalPositions.length / 3;

  log(`📊 Analyzing ${vertexCount} vertices across 52 morph targets...\n`, 'cyan');

  // Analyze each morph target
  const targets = targetPrimitive.listTargets();
  const results = [];

  for (let i = 0; i < targets.length; i++) {
    const target = targets[i];
    const morphPositionAccessor = target.getAttribute('POSITION');

    if (!morphPositionAccessor) {
      log(`⚠️  Target ${i}: No position data`, 'yellow');
      continue;
    }

    const morphPositions = morphPositionAccessor.getArray();

    // Analyze displacement
    const analysis = analyzeMorphTargetDisplacement(originalPositions, morphPositions);
    const classification = classifyMorphTarget(analysis);

    results.push({
      index: i,
      name: target.getName() || `target_${i}`,
      analysis,
      classification,
    });

    // Log summary
    const { category, suggestedPhoneme, confidence } = classification;
    const confidenceStr = `${(confidence * 100).toFixed(0)}%`;

    if (suggestedPhoneme) {
      log(`[${i.toString().padStart(2)}] ${category.padEnd(20)} → ${suggestedPhoneme.padEnd(15)} (${confidenceStr})`, 'green');
    } else {
      log(`[${i.toString().padStart(2)}] ${category.padEnd(20)} (avg disp: ${analysis.avgDisplacement.toFixed(1)})`, 'blue');
    }
  }

  // Generate mapping suggestions
  log('\n' + '='.repeat(80), 'cyan');
  log('📋 SUGGESTED PHONEME MAPPINGS', 'bright');
  log('='.repeat(80) + '\n', 'cyan');

  const phonemeCandidates = {
    jawOpen: [],
    mouthFunnel: [],
    mouthClose: [],
    mouthSmile: [],
  };

  for (const result of results) {
    const { suggestedPhoneme, confidence } = result.classification;
    if (suggestedPhoneme && confidence > 0.5) {
      phonemeCandidates[suggestedPhoneme].push({
        index: result.index,
        confidence,
        avgDisp: result.analysis.avgDisplacement,
      });
    }
  }

  for (const [phoneme, candidates] of Object.entries(phonemeCandidates)) {
    if (candidates.length === 0) {
      log(`${phoneme}: No clear candidates found`, 'yellow');
    } else {
      candidates.sort((a, b) => b.confidence - a.confidence);
      const best = candidates[0];
      log(`${phoneme}: target_${best.index} (confidence: ${(best.confidence * 100).toFixed(0)}%)`, 'green');

      if (candidates.length > 1) {
        log(`  Alternatives: ${candidates.slice(1, 3).map(c => `target_${c.index}`).join(', ')}`, 'blue');
      }
    }
  }

  // Save detailed report
  const reportPath = path.join(__dirname, '../reports/morph-target-analysis.json');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  log(`\n✅ Detailed report saved to: ${reportPath}`, 'green');

  // Generate mapping configuration
  const mapping = {};
  for (const [phoneme, candidates] of Object.entries(phonemeCandidates)) {
    if (candidates.length > 0) {
      mapping[phoneme] = candidates[0].index;
    }
  }

  const mappingPath = path.join(__dirname, '../config/morph-target-mapping.json');
  fs.writeFileSync(mappingPath, JSON.stringify(mapping, null, 2));
  log(`✅ Mapping configuration saved to: ${mappingPath}`, 'green');

  log('\n🎉 Analysis complete!', 'bright');
}

main().catch(error => {
  console.error('Error:', error);
  process.exit(1);
});
