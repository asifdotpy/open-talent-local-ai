import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/**
 * Test script to inspect LeePerrySmith.glb model properties
 * Specifically checks for morph targets and blend shapes
 */

const output = document.getElementById('output');
let logBuffer = '';

function log(message) {
  logBuffer += message + '\n';
  if (output) {
    output.textContent = logBuffer;
  }
  console.log(message);
}

async function testModelProperties() {
  log('🔍 Testing LeePerrySmith.glb model properties...');

  const loader = new GLTFLoader();

  try {
    const gltf = await new Promise((resolve, reject) => {
      loader.load(
        './assets/models/LeePerrySmith.glb',
        resolve,
        undefined,
        reject
      );
    });

    log('✅ Model loaded successfully');
    log('📊 Model Analysis:');

    // Check scene structure
    log(`Scenes: ${gltf.scenes.length}`);
    log(`Scene children: ${gltf.scene.children.length}`);

    // Analyze all meshes in the scene
    let totalVertices = 0;
    let totalMeshes = 0;
    let meshesWithMorphTargets = 0;
    let morphTargetDetails = [];

    gltf.scene.traverse((child) => {
      if (child.isMesh) {
        totalMeshes++;
        const geometry = child.geometry;
        const material = child.material;

        log(`\n🧱 Mesh: ${child.name || 'unnamed'}`);
        log(`  - Vertices: ${geometry.attributes.position.count}`);
        log(`  - Material: ${material.name || 'unnamed'}`);
        log(`  - Has Normals: ${!!geometry.attributes.normal}`);
        log(`  - Has UVs: ${!!geometry.attributes.uv}`);
        log(`  - Has Morph Targets: ${!!geometry.morphTargets && geometry.morphTargets.length > 0}`);

        totalVertices += geometry.attributes.position.count;

        if (geometry.morphTargets && geometry.morphTargets.length > 0) {
          meshesWithMorphTargets++;
          log(`  - Morph Target Count: ${geometry.morphTargets.length}`);

          // Log morph target names
          const morphNames = geometry.morphTargets.map((target, index) => {
            const name = target.name || `morph_${index}`;
            log(`    ${index}: ${name}`);
            return name;
          });

          morphTargetDetails.push({
            mesh: child.name || 'unnamed',
            morphTargets: morphNames,
            vertexCount: geometry.attributes.position.count
          });
        }

        // Check for morph target influences
        if (child.morphTargetInfluences) {
          log(`  - Morph Target Influences: ${child.morphTargetInfluences.length}`);
        }
      }
    });

    log('\n📈 Summary:');
    log(`Total Meshes: ${totalMeshes}`);
    log(`Total Vertices: ${totalVertices.toLocaleString()}`);
    log(`Meshes with Morph Targets: ${meshesWithMorphTargets}`);

    if (morphTargetDetails.length > 0) {
      log('\n🎭 Morph Target Details:');
      morphTargetDetails.forEach(detail => {
        log(`  ${detail.mesh}: ${detail.morphTargets.length} morph targets`);
        log(`    Targets: ${detail.morphTargets.join(', ')}`);
      });
    }

    // Performance assessment
    log('\n⚡ Performance Assessment:');
    if (totalVertices < 10000) {
      log('  ✅ Low vertex count - excellent performance');
    } else if (totalVertices < 50000) {
      log('  ⚠️ Moderate vertex count - good performance');
    } else {
      log('  ❌ High vertex count - may impact performance');
    }

    if (meshesWithMorphTargets > 0) {
      log('  ✅ Has morph targets - GPU-accelerated lip-sync available');
    } else {
      log('  ⚠️ No morph targets - will use CPU vertex manipulation');
    }

    // Animation recommendations
    log('\n🎬 Animation Recommendations:');
    if (meshesWithMorphTargets > 0) {
      log('  - Use MorphTargetAnimationController (preferred)');
      log('  - GPU-accelerated, better performance');
    } else {
      log('  - Use AnimationController (fallback)');
      log('  - CPU vertex manipulation, monitor FPS');
    }

  } catch (error) {
    log('❌ Failed to load model: ' + error.message);
    console.error(error);
  }
}

// Run the test
testModelProperties();
