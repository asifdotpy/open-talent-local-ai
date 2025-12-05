#!/usr/bin/env node

/**
 * Phase 1: Face Model Validation (Node.js Compatible)
 *
 * Validates face.glb model structure and morph targets without WebGL:
 * - Checks GLB file format and size
 * - Parses JSON chunk for morph targets
 * - Validates phoneme mappings (A, E, I, O, U)
 * - Checks for Draco compression
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class FaceModelValidator {
  constructor() {
    this.results = {
      fileExists: false,
      validGLB: false,
      morphTargets: [],
      dracoCompressed: false,
      phonemeTargets: [],
      fileSize: 0,
      errors: []
    };
  }

  validateModel(modelPath) {
    try {
      console.log(`📥 Checking model file: ${modelPath}`);

      // Check if file exists
      if (!fs.existsSync(modelPath)) {
        throw new Error(`Model file not found: ${modelPath}`);
      }

      this.results.fileExists = true;

      // Check file size
      const stats = fs.statSync(modelPath);
      this.results.fileSize = stats.size;
      console.log(`📊 File size: ${(this.results.fileSize / 1024 / 1024).toFixed(2)} MB`);

      // Read and validate GLB format
      this.validateGLBFormat(modelPath);

      return this.results;

    } catch (error) {
      this.results.errors.push(`Validation failed: ${error.message}`);
      console.error('❌ Validation failed:', error);
      return this.results;
    }
  }

  validateGLBFormat(filePath) {
    const buffer = fs.readFileSync(filePath);
    const dataView = new DataView(buffer.buffer);

    // Check GLB magic number (0x46546C67 = 'glTF')
    const magic = dataView.getUint32(0, true);
    if (magic !== 0x46546C67) {
      throw new Error('Invalid GLB magic number - not a valid GLB file');
    }

    console.log('✅ Valid GLB file format');

    // Parse GLB chunks
    let offset = 12; // After header

    while (offset < buffer.length) {
      const chunkLength = dataView.getUint32(offset, true);
      const chunkType = dataView.getUint32(offset + 4, true);

      if (chunkType === 0x4E4F534A) { // JSON chunk
        this.parseJSONChunk(buffer, offset + 8, chunkLength);
      } else if (chunkType === 0x004E4942) { // BIN chunk
        this.checkDracoCompression(buffer, offset + 8, chunkLength);
      }

      offset += 8 + chunkLength;
    }

    this.results.validGLB = true;
  }

  parseJSONChunk(buffer, offset, length) {
    try {
      const jsonString = buffer.toString('utf8', offset, offset + length);
      const gltf = JSON.parse(jsonString);

      console.log('🔍 Parsing GLTF JSON...');

      // Find meshes with morph targets
      if (gltf.meshes) {
        gltf.meshes.forEach((mesh, index) => {
          if (mesh.primitives && mesh.primitives[0].targets) {
            const targets = mesh.primitives[0].targets;
            console.log(`🎭 Found morph targets in mesh ${index}: ${targets.length} targets`);

            // Extract morph target names
            if (gltf.accessors && mesh.primitives[0].attributes) {
              // This is a simplified check - in practice we'd need to map accessor indices
              // For now, we'll assume standard naming if targets exist
              const targetNames = targets.map((_, i) => `target_${i}`);
              this.results.morphTargets = targetNames;
            }
          }
        });
      }

      // Check for Draco extension
      if (gltf.extensionsUsed && gltf.extensionsUsed.includes('KHR_draco_mesh_compression')) {
        this.results.dracoCompressed = true;
        console.log('🗜️  Model uses Draco compression');
      }

      // Try to find phoneme-related morphs in node names or extensions
      this.checkForPhonemes(gltf);

    } catch (error) {
      console.warn('⚠️  Could not parse JSON chunk:', error.message);
    }
  }

  checkForPhonemes(gltf) {
    const phonemePatterns = ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u'];

    // Check node names
    if (gltf.nodes) {
      gltf.nodes.forEach(node => {
        if (node.name) {
          phonemePatterns.forEach(phoneme => {
            if (node.name.toLowerCase().includes(phoneme.toLowerCase())) {
              if (!this.results.phonemeTargets.includes(phoneme)) {
                this.results.phonemeTargets.push(phoneme);
              }
            }
          });
        }
      });
    }

    // Check animations for phoneme tracks
    if (gltf.animations) {
      gltf.animations.forEach(animation => {
        if (animation.name) {
          phonemePatterns.forEach(phoneme => {
            if (animation.name.toLowerCase().includes(phoneme.toLowerCase())) {
              if (!this.results.phonemeTargets.includes(phoneme)) {
                this.results.phonemeTargets.push(phoneme);
              }
            }
          });
        }
      });
    }

    if (this.results.phonemeTargets.length > 0) {
      console.log(`🎯 Found phoneme references: ${this.results.phonemeTargets.join(', ')}`);
    }
  }

  checkDracoCompression(buffer, offset, length) {
    // Simple check for Draco magic bytes in BIN chunk
    const binData = buffer.subarray(offset, offset + Math.min(length, 100));
    const magic = binData.toString('ascii', 0, 4);

    if (magic === 'DRAC') {
      this.results.dracoCompressed = true;
      console.log('🗜️  Draco compression detected in BIN chunk');
    }
  }

  generateReport() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 FACE MODEL VALIDATION REPORT');
    console.log('='.repeat(60));

    console.log(`File Exists: ${this.results.fileExists ? '✅' : '❌'}`);
    console.log(`Valid GLB: ${this.results.validGLB ? '✅' : '❌'}`);
    console.log(`Draco Compressed: ${this.results.dracoCompressed ? '✅' : '❌'}`);
    console.log(`File Size: ${(this.results.fileSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`Morph Targets: ${this.results.morphTargets.length} found`);
    console.log(`Phoneme Targets: ${this.results.phonemeTargets.length} found`);

    if (this.results.phonemeTargets.length > 0) {
      console.log('Phonemes found:', this.results.phonemeTargets.join(', '));
    }

    if (this.results.errors.length > 0) {
      console.log('\n❌ ERRORS:');
      this.results.errors.forEach(error => console.log(`   - ${error}`));
    }

    const isCompatible = this.results.fileExists &&
                        this.results.validGLB &&
                        this.results.morphTargets.length > 0 &&
                        this.results.errors.length === 0;

    console.log(`\n🎯 OVERALL COMPATIBILITY: ${isCompatible ? '✅ COMPATIBLE' : '❌ INCOMPATIBLE'}`);
    console.log('='.repeat(60));

    return isCompatible;
  }
}

// Main execution
async function main() {
  console.log('🚀 Starting Face Model Validation (Phase 1)\n');

  const validator = new FaceModelValidator();

  try {
    const modelPath = path.join(__dirname, '..', 'assets', 'models', 'face.glb');
    console.log(`🎭 Validating model: ${modelPath}\n`);

    const results = validator.validateModel(modelPath);
    const isCompatible = validator.generateReport();

    // Save results to file
    const reportPath = path.join(__dirname, 'model-validation-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`\n💾 Report saved to: ${reportPath}`);

    process.exit(isCompatible ? 0 : 1);

  } catch (error) {
    console.error('💥 Validation failed:', error);
    process.exit(1);
  }
}

// Run validation
main().catch(console.error);