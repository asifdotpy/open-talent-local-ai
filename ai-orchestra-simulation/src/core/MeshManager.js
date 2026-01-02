import * as THREE from 'three';
import { VertexDetectionEngine } from '../animation/VertexDetectionEngine.js';
import { Logger } from '../utils/Logger.js';

/**
 * Manages mesh operations and head mesh detection
 */
export class MeshManager {
  constructor() {
    this.logger = Logger.getInstance();
    this.headMesh = null;
    this.mouthVertexIndices = [];
    this.originalMouthPositions = [];
    this.mouthCenterY = 0;
  }

  findHeadMesh(scene) {
    this.headMesh = null;
    let meshesWithMorphTargets = [];

    // First pass: find all meshes and check for morph targets
    scene.traverse((child) => {
      if (child.isMesh) {
        const hasMorphTargets = child.morphTargetDictionary && Object.keys(child.morphTargetDictionary).length > 0;

        if (hasMorphTargets) {
          meshesWithMorphTargets.push({
            mesh: child,
            morphCount: Object.keys(child.morphTargetDictionary).length,
            name: child.name || child.material?.name || 'unnamed'
          });
        }
      }
    });

    // Prioritize meshes with morph targets
    if (meshesWithMorphTargets.length > 0) {
      // Sort by morph target count (descending)
      meshesWithMorphTargets.sort((a, b) => b.morphCount - a.morphCount);
      this.headMesh = meshesWithMorphTargets[0].mesh;
      this.logger.log('SUCCESS', `Found mesh with ${meshesWithMorphTargets[0].morphCount} morph targets:`, meshesWithMorphTargets[0].name);

      // Log all morph target names for debugging
      const morphNames = Object.keys(this.headMesh.morphTargetDictionary);
      this.logger.log('INFO', 'Available morph targets:', morphNames.join(', '));
    } else {
      // Fallback: use the first mesh found
      scene.traverse((child) => {
        if (child.isMesh && !this.headMesh) {
          this.headMesh = child;
          this.logger.log('INFO', 'Using first available mesh (no morph targets):', child.material?.name || child.name || 'unnamed');
        }
      });
    }

    if (this.headMesh) {
      this.logMeshInfo();
      this.initializeMouthTracking();
      return this.headMesh;
    }

    this.logger.log('ERROR', 'No suitable mesh found in scene');
    return null;
  }

  logMeshInfo() {
    if (!this.headMesh) return;

    const geometry = this.headMesh.geometry;
    const material = this.headMesh.material;

    // Check for morph targets in the mesh itself (newer Three.js approach)
    const hasMorphTargets = this.headMesh.morphTargetDictionary && Object.keys(this.headMesh.morphTargetDictionary).length > 0;
    const morphTargetCount = hasMorphTargets ? Object.keys(this.headMesh.morphTargetDictionary).length : 0;

    this.logger.log('INFO', 'Head mesh information', {
      name: this.headMesh.name || 'unnamed',
      vertexCount: geometry.attributes.position?.count || 0,
      materialName: material?.name || 'unnamed',
      hasNormals: !!geometry.attributes.normal,
      hasUVs: !!geometry.attributes.uv,
      hasMorphTargets: hasMorphTargets,
      morphTargetCount: morphTargetCount,
      boundingBox: geometry.boundingBox
        ? {
            min: geometry.boundingBox.min,
            max: geometry.boundingBox.max,
          }
        : 'not computed',
    });

    // Log morph target names if available
    if (hasMorphTargets) {
      const morphNames = Object.keys(this.headMesh.morphTargetDictionary);
      const mouthRelated = morphNames.filter(name =>
        name.toLowerCase().includes('mouth') ||
        name.toLowerCase().includes('jaw') ||
        name.toLowerCase().includes('lip')
      );

      this.logger.log('SUCCESS', `Found ${mouthRelated.length} mouth-related morph targets:`, mouthRelated.join(', '));
    }
  }

  initializeMouthTracking() {
    if (!this.headMesh) return;

    // Initialize mouth vertex tracking for lip-sync
    this.mouthVertexIndices = [];
    this.originalMouthPositions = [];
    this.mouthCenterY = 0;

    const geometry = this.headMesh.geometry;
    const positions = geometry.attributes.position.array;
    const vertexCount = geometry.attributes.position.count;

    // Performance check: if model is too complex, suggest simplification
    if (vertexCount > 10000) {
      this.logger.log('WARNING', `Model has ${vertexCount} vertices - this may cause performance issues`);
      this.logger.log('INFO', 'Consider using a lower-poly version of the model for better performance');
    }

    // Find mouth vertices (simple heuristic: vertices in lower face region)
    const bounds = this.getMeshBounds();

    for (let i = 0; i < vertexCount; i++) {
      const y = positions[i * 3 + 1];
      const z = positions[i * 3 + 2];

      // Mouth region: lower third of face, front-facing
      if (y < bounds.center.y && y > bounds.min.y + (bounds.max.y - bounds.min.y) * 0.3 && z > bounds.center.z) {
        this.mouthVertexIndices.push(i);
        this.originalMouthPositions.push(new THREE.Vector3(
          positions[i * 3],
          positions[i * 3 + 1],
          positions[i * 3 + 2]
        ));

        this.mouthCenterY = Math.max(this.mouthCenterY, y);
      }
    }

    this.logger.log('SUCCESS', `Initialized mouth tracking with ${this.mouthVertexIndices.length} vertices`);
  }

  /**
   * Advanced mouth vertex identification using multiple detection strategies
   * @param {Object} boundingBoxConfig - Optional bounding box configuration
   */
  identifyMouthVertices(boundingBoxConfig = null) {
    if (!this.headMesh || !this.headMesh.geometry || !this.headMesh.geometry.attributes.position) {
      this.logger.log('ERROR', 'Invalid mesh or missing position attribute');
      return;
    }

    this.logger.log('INFO', 'Identifying mouth vertices using comprehensive detection engine...');

    // Create and use the comprehensive vertex detection engine
    const detectionEngine = new VertexDetectionEngine(this.headMesh);
    const detectionResult = detectionEngine.detectMouthVertices();

    if (detectionResult.error) {
      this.logger.log('ERROR', `Vertex detection failed: ${detectionResult.error}`, detectionResult.diagnostics);
      return;
    }

    if (detectionResult.vertices.length === 0) {
      this.logger.log('ERROR', 'No mouth vertices found with any detection strategy', {
        strategy: detectionResult.strategy,
        diagnostics: detectionResult.diagnostics,
      });
      return;
    }

    // Validate the detection result
    const validation = detectionEngine.validateDetection(detectionResult.vertices);
    this.logger.log('ANALYSIS', 'Detection validation', {
      strategy: detectionResult.strategy,
      confidence: detectionResult.confidence.toFixed(2),
      validation: {
        valid: validation.valid,
        confidence: validation.confidence.toFixed(2),
        issues: validation.issues,
        suggestions: validation.suggestions,
        vertexCount: validation.vertexCount,
        aspectRatio: validation.aspectRatio,
      },
    });

    // Update global arrays
    this.mouthVertexIndices = detectionResult.vertices.map((v) => v.index);
    this.originalMouthPositions = detectionResult.vertices.map((v) => v.position);

    // Calculate mouth center Y
    if (this.originalMouthPositions.length > 0) {
      this.mouthCenterY = this.originalMouthPositions.reduce((sum, pos) => sum + pos.y, 0) / this.originalMouthPositions.length;
      this.logger.log('ANALYSIS', `Calculated mouth center Y: ${this.mouthCenterY.toFixed(3)}`);
    }

    this.logger.log('SUCCESS', `Found ${this.mouthVertexIndices.length} mouth vertices using ${detectionResult.strategy} strategy`);

    // Cluster vertices for better organization
    const clusters = this.clusterVertices(detectionResult.vertices);
    this.logger.log('ANALYSIS', `Organized vertices into ${clusters.length} clusters`);

    return {
      vertexCount: this.mouthVertexIndices.length,
      strategy: detectionResult.strategy,
      confidence: detectionResult.confidence,
      validation: validation,
    };
  }

  /**
   * Simple vertex clustering for organization
   * @param {Array} vertices - Array of vertex objects with position property
   * @param {number} clusterRadius - Radius for clustering
   * @returns {Array} Array of vertex clusters
   */
  clusterVertices(vertices, clusterRadius = 0.02) {
    if (vertices.length === 0) return [];

    const clusters = [];
    const processed = new Set();

    for (let i = 0; i < vertices.length; i++) {
      if (processed.has(i)) continue;

      const cluster = [vertices[i]];
      processed.add(i);

      // Find nearby vertices
      for (let j = i + 1; j < vertices.length; j++) {
        if (processed.has(j)) continue;

        const distance = vertices[i].position.distanceTo(vertices[j].position);
        if (distance <= clusterRadius) {
          cluster.push(vertices[j]);
          processed.add(j);
        }
      }

      clusters.push(cluster);
    }

    return clusters;
  }

  getMeshBounds() {
    if (!this.headMesh) return null;

    const geometry = this.headMesh.geometry;
    geometry.computeBoundingBox();

    return {
      min: geometry.boundingBox.min,
      max: geometry.boundingBox.max,
      center: geometry.boundingBox.getCenter(new THREE.Vector3())
    };
  }

  getMouthData() {
    return {
      vertexIndices: this.mouthVertexIndices,
      originalPositions: this.originalMouthPositions,
      centerY: this.mouthCenterY
    };
  }

  /**
   * Simplifies mesh geometry by reducing vertex count for better performance
   * @param {THREE.Mesh} mesh - The mesh to simplify
   * @param {number} targetRatio - Target ratio of vertices to keep (0.1 = 10%)
   * @returns {THREE.Mesh} - New simplified mesh
   */
  simplifyGeometry(mesh, targetRatio = 0.1) {
    if (!mesh || !mesh.geometry) {
      this.logger.log('WARNING', 'Cannot simplify: invalid mesh');
      return mesh;
    }

    const originalCount = mesh.geometry.attributes.position.count;
    const targetCount = Math.max(100, Math.floor(originalCount * targetRatio));

    this.logger.log('INFO', `Simplifying geometry from ${originalCount} to ~${targetCount} vertices`);

    // Create simplified geometry using vertex clustering
    const simplifiedGeometry = this.createSimplifiedGeometry(mesh.geometry, targetRatio);

    // Create new mesh with simplified geometry
    const simplifiedMesh = new THREE.Mesh(simplifiedGeometry, mesh.material.clone());
    simplifiedMesh.name = mesh.name + '_simplified';
    simplifiedMesh.position.copy(mesh.position);
    simplifiedMesh.rotation.copy(mesh.rotation);
    simplifiedMesh.scale.copy(mesh.scale);

    this.logger.log('SUCCESS', `Geometry simplified to ${simplifiedGeometry.attributes.position.count} vertices`);
    return simplifiedMesh;
  }

  /**
   * Creates a simplified version of the geometry
   * @param {THREE.BufferGeometry} geometry - Original geometry
   * @param {number} targetRatio - Target ratio of vertices to keep
   * @returns {THREE.BufferGeometry} - Simplified geometry
   */
  createSimplifiedGeometry(geometry, targetRatio) {
    const positions = geometry.attributes.position.array;
    const vertexCount = geometry.attributes.position.count;

    // Simple vertex decimation: keep every Nth vertex
    const keepRatio = Math.max(0.05, Math.min(1.0, targetRatio));
    const step = Math.max(1, Math.floor(1 / keepRatio));

    const newPositions = [];
    const newIndices = [];

    // Create vertex map for index remapping
    const vertexMap = new Map();
    let newVertexIndex = 0;

    // Process indices if they exist
    if (geometry.index) {
      const indices = geometry.index.array;
      for (let i = 0; i < indices.length; i += 3) {
        const a = indices[i];
        const b = indices[i + 1];
        const c = indices[i + 2];

        // Check if we should keep this triangle
        if (a % step === 0 || b % step === 0 || c % step === 0) {
          // Remap vertex indices
          const newA = this.getOrCreateVertexIndex(a, vertexMap, positions, newPositions, step);
          const newB = this.getOrCreateVertexIndex(b, vertexMap, positions, newPositions, step);
          const newC = this.getOrCreateVertexIndex(c, vertexMap, positions, newPositions, step);

          newIndices.push(newA, newB, newC);
        }
      }
    } else {
      // Non-indexed geometry: just decimate vertices
      for (let i = 0; i < vertexCount; i += step) {
        newPositions.push(
          positions[i * 3],
          positions[i * 3 + 1],
          positions[i * 3 + 2]
        );
      }
    }

    // Create new geometry
    const newGeometry = new THREE.BufferGeometry();

    if (newIndices.length > 0) {
      newGeometry.setIndex(newIndices);
    }

    newGeometry.setAttribute('position', new THREE.Float32BufferAttribute(newPositions, 3));

    // Copy other attributes if they exist (scaled down)
    if (geometry.attributes.normal) {
      const normals = geometry.attributes.normal.array;
      const newNormals = [];
      for (let i = 0; i < newPositions.length; i += 3) {
        const originalIndex = Math.floor((i / 3) * step) * 3;
        if (originalIndex < normals.length) {
          newNormals.push(normals[originalIndex], normals[originalIndex + 1], normals[originalIndex + 2]);
        }
      }
      newGeometry.setAttribute('normal', new THREE.Float32BufferAttribute(newNormals, 3));
    }

    if (geometry.attributes.uv) {
      const uvs = geometry.attributes.uv.array;
      const newUVs = [];
      for (let i = 0; i < newPositions.length; i += 3) {
        const originalIndex = Math.floor((i / 3) * step) * 2;
        if (originalIndex < uvs.length) {
          newUVs.push(uvs[originalIndex], uvs[originalIndex + 1]);
        }
      }
      newGeometry.setAttribute('uv', new THREE.Float32BufferAttribute(newUVs, 2));
    }

    return newGeometry;
  }

  /**
   * Helper method for vertex index remapping during simplification
   */
  getOrCreateVertexIndex(originalIndex, vertexMap, positions, newPositions, step) {
    if (vertexMap.has(originalIndex)) {
      return vertexMap.get(originalIndex);
    }

    // Check if we should keep this vertex
    if (originalIndex % step === 0) {
      const newIndex = newPositions.length / 3;
      vertexMap.set(originalIndex, newIndex);

      newPositions.push(
        positions[originalIndex * 3],
        positions[originalIndex * 3 + 1],
        positions[originalIndex * 3 + 2]
      );

      return newIndex;
    }

    // Find nearest kept vertex
    const nearestIndex = Math.round(originalIndex / step) * step;
    if (vertexMap.has(nearestIndex)) {
      return vertexMap.get(nearestIndex);
    }

    // Create new vertex
    const newIndex = newPositions.length / 3;
    vertexMap.set(originalIndex, newIndex);

    const posIndex = Math.min(nearestIndex * 3, positions.length - 3);
    newPositions.push(
      positions[posIndex],
      positions[posIndex + 1],
      positions[posIndex + 2]
    );

    return newIndex;
  }

  async initialize(assets) {
    if (!assets || !assets.model) {
      throw new Error('No model asset provided to MeshManager');
    }

    // The model is a GLTF scene, find the head mesh within it
    const headMesh = this.findHeadMesh(assets.model.scene);

    if (!headMesh) {
      throw new Error('Could not find head mesh in the loaded model');
    }

    return headMesh;
  }

  validateMesh(mesh = this.headMesh) {
    if (!mesh) {
      return {
        valid: false,
        issues: ['No mesh provided'],
        suggestions: ['Load a 3D model first'],
      };
    }

    const issues = [];
    const suggestions = [];

    if (!mesh.geometry) {
      issues.push('Mesh has no geometry');
      suggestions.push('Ensure the mesh is properly loaded');
    } else {
      if (!mesh.geometry.attributes.position) {
        issues.push('Mesh geometry has no position attribute');
        suggestions.push('Check if the mesh data is corrupted');
      }

      if (mesh.geometry.attributes.position?.count === 0) {
        issues.push('Mesh has no vertices');
        suggestions.push('Verify the 3D model contains vertex data');
      }
    }

    if (!mesh.material) {
      issues.push('Mesh has no material');
      suggestions.push('Assign a material to the mesh');
    }

    return {
      valid: issues.length === 0,
      issues,
      suggestions,
      vertexCount: mesh.geometry?.attributes.position?.count || 0,
    };
  }

  dispose() {
    if (this.headMesh) {
      if (this.headMesh.geometry) {
        this.headMesh.geometry.dispose();
      }

      if (this.headMesh.material) {
        if (Array.isArray(this.headMesh.material)) {
          this.headMesh.material.forEach((material) => material.dispose());
        } else {
          this.headMesh.material.dispose();
        }
      }
    }

    this.headMesh = null;
    this.logger.log('SUCCESS', 'Mesh manager disposed');
  }
}
