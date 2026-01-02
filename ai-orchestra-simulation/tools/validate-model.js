/**
 * Model Validation Script
 * Validates 3D models for lip sync compatibility
 *
 * Usage:
 *   node tools/validate-model.js <model-path>
 *
 * Example:
 *   node tools/validate-model.js ./assets/models/face.glb
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Required mouth morph target patterns
const MOUTH_PATTERNS = {
  jawOpen: ['jawopen', 'jaw_open', 'mouth_open', 'mouthopen'],
  mouthFunnel: ['mouthfunnel', 'mouth_funnel', 'pucker'],
  mouthSmile: ['mouthsmile', 'mouth_smile', 'smile'],
  mouthClose: ['mouthclose', 'mouth_close', 'closed'],
};

// Performance thresholds
const MAX_VERTICES = 5000;
const MAX_MESHES = 10;
const MIN_MORPH_TARGETS = 4;

class ModelValidator {
  constructor(modelPath) {
    this.modelPath = modelPath;
    this.results = {
      valid: false,
      errors: [],
      warnings: [],
      info: {},
    };
  }

  async validate() {
    console.log(`\n🔍 Validating model: ${this.modelPath}\n`);

    try {
      // Check file exists
      if (!this.fileExists()) {
        this.addError('Model file does not exist');
        return this.results;
      }

      // Determine file type
      const fileType = this.getFileType();
      console.log(`📁 File type: ${fileType}`);

      // Load model based on type
      if (fileType === 'glb' || fileType === 'gltf') {
        await this.validateGLTF();
      } else if (fileType === 'fbx') {
        this.addWarning('FBX files require conversion to GLTF/GLB for web use');
        // FBX validation would require FBXLoader in Node.js environment
        // For now, just note that conversion is needed
        this.addInfo('fbxConversionRequired', true);
      } else {
        this.addError(`Unsupported file type: ${fileType}`);
        return this.results;
      }

      // Validate requirements
      this.validateRequirements();

      // Print results
      this.printResults();

      return this.results;
    } catch (error) {
      this.addError(`Validation failed: ${error.message}`);
      console.error(error);
      return this.results;
    }
  }

  fileExists() {
    try {
      const fs = require('fs');
      return fs.existsSync(this.modelPath);
    } catch (error) {
      return false;
    }
  }

  getFileType() {
    const ext = this.modelPath.split('.').pop().toLowerCase();
    return ext;
  }

  async validateGLTF() {
    // Note: This is a simplified validation
    // Full GLTF validation would require loading in Three.js context
    // For Node.js, we can check file structure and basic properties

    console.log('📦 GLTF/GLB file detected');
    console.log('⚠️  Full validation requires browser/Three.js environment');
    console.log('💡 Use tests/test-model-properties.js for detailed validation');

    this.addInfo('fileType', 'gltf');
    this.addInfo('validationMethod', 'basic');
    this.addWarning('Full validation requires browser environment');
  }

  validateRequirements() {
    const info = this.results.info;

    // Check vertex count
    if (info.vertexCount && info.vertexCount > MAX_VERTICES) {
      this.addError(`Vertex count (${info.vertexCount}) exceeds maximum (${MAX_VERTICES})`);
    } else if (info.vertexCount) {
      console.log(`✅ Vertex count: ${info.vertexCount} (within limit)`);
    }

    // Check mesh count
    if (info.meshCount && info.meshCount > MAX_MESHES) {
      this.addWarning(`Mesh count (${info.meshCount}) is high (max recommended: ${MAX_MESHES})`);
    }

    // Check morph targets
    if (info.morphTargetCount !== undefined) {
      if (info.morphTargetCount < MIN_MORPH_TARGETS) {
        this.addError(`Morph target count (${info.morphTargetCount}) is below minimum (${MIN_MORPH_TARGETS})`);
      } else {
        console.log(`✅ Morph targets: ${info.morphTargetCount} (meets requirement)`);
      }
    }

    // Check mouth morph targets
    if (info.mouthMorphTargets) {
      const mouthCount = Object.keys(info.mouthMorphTargets).length;
      if (mouthCount < MIN_MORPH_TARGETS) {
        this.addError(`Mouth morph targets (${mouthCount}) is below minimum (${MIN_MORPH_TARGETS})`);
      } else {
        console.log(`✅ Mouth morph targets: ${mouthCount} (${Object.keys(info.mouthMorphTargets).join(', ')})`);
      }
    }
  }

  addError(message) {
    this.results.errors.push(message);
    console.error(`❌ ${message}`);
  }

  addWarning(message) {
    this.results.warnings.push(message);
    console.warn(`⚠️  ${message}`);
  }

  addInfo(key, value) {
    this.results.info[key] = value;
  }

  printResults() {
    console.log('\n📊 Validation Results:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    if (this.results.errors.length === 0 && this.results.warnings.length === 0) {
      console.log('✅ Model is valid for lip sync');
      this.results.valid = true;
    } else {
      console.log('⚠️  Model has issues:');
      if (this.results.errors.length > 0) {
        console.log('\n❌ Errors:');
        this.results.errors.forEach(error => console.log(`   - ${error}`));
      }
      if (this.results.warnings.length > 0) {
        console.log('\n⚠️  Warnings:');
        this.results.warnings.forEach(warning => console.log(`   - ${warning}`));
      }
    }

    console.log('\n📋 Model Info:');
    Object.entries(this.results.info).forEach(([key, value]) => {
      console.log(`   ${key}: ${value}`);
    });

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  }
}

// Browser-based validation function
export function validateModelInBrowser(modelPath, gltf) {
  const results = {
    valid: false,
    errors: [],
    warnings: [],
    info: {},
  };

  try {
    // Analyze scene
    let totalVertices = 0;
    let totalMeshes = 0;
    let meshesWithMorphTargets = 0;
    const mouthMorphTargets = {};
    let morphTargetDictionary = null;

    gltf.scene.traverse((child) => {
      if (child.isMesh) {
        totalMeshes++;
        const geometry = child.geometry;
        totalVertices += geometry.attributes.position.count;

        // Check for morph targets
        if (geometry.morphTargets && geometry.morphTargets.length > 0) {
          meshesWithMorphTargets++;

          // Build morph target dictionary
          if (child.morphTargetDictionary) {
            morphTargetDictionary = child.morphTargetDictionary;
          }

          // Find mouth morph targets
          geometry.morphTargets.forEach((target, index) => {
            const name = target.name || `morph_${index}`;
            const lowerName = name.toLowerCase();

            for (const [targetType, patterns] of Object.entries(MOUTH_PATTERNS)) {
              if (patterns.some(pattern => lowerName.includes(pattern))) {
                mouthMorphTargets[targetType] = name;
                break;
              }
            }
          });
        }
      }
    });

    // Store results
    results.info.vertexCount = totalVertices;
    results.info.meshCount = totalMeshes;
    results.info.morphTargetCount = morphTargetDictionary ? Object.keys(morphTargetDictionary).length : 0;
    results.info.mouthMorphTargets = mouthMorphTargets;
    results.info.meshesWithMorphTargets = meshesWithMorphTargets;

    // Validate requirements
    if (totalVertices > MAX_VERTICES) {
      results.errors.push(`Vertex count (${totalVertices}) exceeds maximum (${MAX_VERTICES})`);
    }

    if (totalMeshes > MAX_MESHES) {
      results.warnings.push(`Mesh count (${totalMeshes}) is high (max recommended: ${MAX_MESHES})`);
    }

    if (results.info.morphTargetCount < MIN_MORPH_TARGETS) {
      results.errors.push(`Morph target count (${results.info.morphTargetCount}) is below minimum (${MIN_MORPH_TARGETS})`);
    }

    const mouthCount = Object.keys(mouthMorphTargets).length;
    if (mouthCount < MIN_MORPH_TARGETS) {
      results.errors.push(`Mouth morph targets (${mouthCount}) is below minimum (${MIN_MORPH_TARGETS})`);
    }

    // Determine validity
    results.valid = results.errors.length === 0;

    return results;
  } catch (error) {
    results.errors.push(`Validation failed: ${error.message}`);
    return results;
  }
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const modelPath = process.argv[2];

  if (!modelPath) {
    console.error('Usage: node tools/validate-model.js <model-path>');
    console.error('Example: node tools/validate-model.js ./assets/models/face.glb');
    process.exit(1);
  }

  const validator = new ModelValidator(modelPath);
  validator.validate().then(results => {
    process.exit(results.valid ? 0 : 1);
  });
}

export default ModelValidator;
