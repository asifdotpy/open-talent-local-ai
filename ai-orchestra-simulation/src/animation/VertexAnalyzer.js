import * as THREE from 'three';
import { Logger } from '../utils/Logger.js';

/**
 * Analyzes mesh vertex distribution and provides utilities for vertex operations
 */
export class VertexAnalyzer {
  constructor() {
    this.logger = Logger.getInstance();
  }

  analyzeVertexDistribution(mesh) {
    if (!mesh || !mesh.geometry || !mesh.geometry.attributes.position) {
      return null;
    }

    const positionAttribute = mesh.geometry.attributes.position;
    const vertex = new THREE.Vector3();
    const stats = {
      min: new THREE.Vector3(Infinity, Infinity, Infinity),
      max: new THREE.Vector3(-Infinity, -Infinity, -Infinity),
      center: new THREE.Vector3(),
      count: positionAttribute.count,
    };

    // Calculate bounds and center
    for (let i = 0; i < positionAttribute.count; i++) {
      vertex.fromBufferAttribute(positionAttribute, i);
      stats.min.min(vertex);
      stats.max.max(vertex);
    }

    stats.center.addVectors(stats.min, stats.max).multiplyScalar(0.5);

    // DEBUG: Dump all vertex positions to understand model layout
    this.dumpAllVertexPositions(mesh, stats);

    this.logger.log('ANALYSIS', 'Vertex distribution analysis', {
      totalVertices: stats.count,
      bounds: {
        min: {
          x: stats.min.x.toFixed(3),
          y: stats.min.y.toFixed(3),
          z: stats.min.z.toFixed(3),
        },
        max: {
          x: stats.max.x.toFixed(3),
          y: stats.max.y.toFixed(3),
          z: stats.max.z.toFixed(3),
        },
        center: {
          x: stats.center.x.toFixed(3),
          y: stats.center.y.toFixed(3),
          z: stats.center.z.toFixed(3),
        },
      },
    });

    return stats;
  }

  dumpAllVertexPositions(mesh, stats) {
    if (!mesh || !mesh.geometry || !mesh.geometry.attributes.position) {
      return;
    }

    const positionAttribute = mesh.geometry.attributes.position;
    const vertex = new THREE.Vector3();
    const allPositions = [];

    // Sample first 100 vertices for detailed logging
    const sampleSize = Math.min(100, positionAttribute.count);
    this.logger.log('DEBUG', `Dumping first ${sampleSize} vertex positions from ${positionAttribute.count} total vertices`);

    for (let i = 0; i < sampleSize; i++) {
      vertex.fromBufferAttribute(positionAttribute, i);
      allPositions.push({
        index: i,
        x: vertex.x.toFixed(4),
        y: vertex.y.toFixed(4),
        z: vertex.z.toFixed(4),
      });
    }

    // Group vertices by Y position ranges to identify facial regions
    const yRanges = {
      upperFace: [],
      midFace: [],
      lowerFace: [],
      neck: [],
    };

    const faceHeight = stats.max.y - stats.min.y;
    const upperThreshold = stats.min.y + faceHeight * 0.7;
    const midThreshold = stats.min.y + faceHeight * 0.4;

    for (let i = 0; i < positionAttribute.count; i++) {
      vertex.fromBufferAttribute(positionAttribute, i);
      if (vertex.y >= upperThreshold) {
        yRanges.upperFace.push({ index: i, y: vertex.y.toFixed(4) });
      } else if (vertex.y >= midThreshold) {
        yRanges.midFace.push({ index: i, y: vertex.y.toFixed(4) });
      } else if (vertex.y >= stats.min.y + faceHeight * 0.1) {
        yRanges.lowerFace.push({ index: i, y: vertex.y.toFixed(4) });
      } else {
        yRanges.neck.push({ index: i, y: vertex.y.toFixed(4) });
      }
    }

    this.logger.log('DEBUG', 'Vertex distribution by Y position ranges', {
      faceHeight: faceHeight.toFixed(4),
      upperThreshold: upperThreshold.toFixed(4),
      midThreshold: midThreshold.toFixed(4),
      ranges: {
        upperFace: {
          count: yRanges.upperFace.length,
          sampleY: yRanges.upperFace.slice(0, 5).map(v => v.y),
        },
        midFace: {
          count: yRanges.midFace.length,
          sampleY: yRanges.midFace.slice(0, 5).map(v => v.y),
        },
        lowerFace: {
          count: yRanges.lowerFace.length,
          sampleY: yRanges.lowerFace.slice(0, 5).map(v => v.y),
        },
        neck: {
          count: yRanges.neck.length,
          sampleY: yRanges.neck.slice(0, 5).map(v => v.y),
        },
      },
    });

    // Look for potential mouth vertices (lowest Y positions in lower face)
    const lowerFaceVertices = [];
    for (let i = 0; i < positionAttribute.count; i++) {
      vertex.fromBufferAttribute(positionAttribute, i);
      if (vertex.y >= stats.min.y + faceHeight * 0.1 && vertex.y <= stats.min.y + faceHeight * 0.35) {
        lowerFaceVertices.push({
          index: i,
          x: vertex.x.toFixed(4),
          y: vertex.y.toFixed(4),
          z: vertex.z.toFixed(4),
        });
      }
    }

    // Sort by Y position (lowest first) to find mouth candidates
    lowerFaceVertices.sort((a, b) => parseFloat(a.y) - parseFloat(b.y));

    this.logger.log('DEBUG', 'Potential mouth vertices (lowest Y positions in lower face)', {
      totalLowerFace: lowerFaceVertices.length,
      lowest10: lowerFaceVertices.slice(0, 10),
      mouthRegion: {
        yMin: (stats.min.y + faceHeight * 0.1).toFixed(4),
        yMax: (stats.min.y + faceHeight * 0.35).toFixed(4),
      },
    });

    // Log sample positions for manual inspection
    // Removed excessive vertex position logging
  }

  calculateOptimalMouthBoundingBox(mesh, debug = false) {
    const stats = this.analyzeVertexDistribution(mesh);
    if (!stats) return null;

    // Calculate mouth region based on actual model anatomy (corrected for conductor.gltf)
    const faceHeight = stats.max.y - stats.min.y;
    const faceWidth = stats.max.x - stats.min.x;
    const faceDepth = stats.max.z - stats.min.z;

    // Corrected anatomical parameters based on vertex analysis
    // Mouth is lower on the face, around 25-35% from bottom of face height
    const mouthY = stats.min.y + faceHeight * 0.3; // Mouth at 30% from bottom
    const mouthHeight = faceHeight * 0.12; // Slightly taller mouth region
    const mouthWidth = faceWidth * 0.3; // Wider mouth region
    const mouthDepth = faceDepth * 0.3; // Less deep, more centered

    const optimalBox = {
      minX: stats.center.x - mouthWidth,
      maxX: stats.center.x + mouthWidth,
      minY: mouthY - mouthHeight,
      maxY: mouthY + mouthHeight,
      minZ: stats.center.z - mouthDepth,
      maxZ: stats.center.z + mouthDepth, // Centered on Z axis
    };

    if (debug) {
      this.logger.log('DEBUG', 'Corrected Optimal Bounding Box Calculation', {
        stats,
        faceHeight,
        faceWidth,
        faceDepth,
        mouthY,
        mouthHeight,
        mouthWidth,
        mouthDepth,
        optimalBox,
      });
    }

    this.logger.log('ANALYSIS', 'Calculated corrected optimal mouth bounding box', {
      corrected: {
        minX: optimalBox.minX.toFixed(3),
        maxX: optimalBox.maxX.toFixed(3),
        minY: optimalBox.minY.toFixed(3),
        maxY: optimalBox.maxY.toFixed(3),
        minZ: optimalBox.minZ.toFixed(3),
        maxZ: optimalBox.maxZ.toFixed(3),
      },
    });

    return optimalBox;
  }

  generateFallbackBoundingBoxes(mesh) {
    const stats = this.analyzeVertexDistribution(mesh);
    if (!stats) return [];

    const faceHeight = stats.max.y - stats.min.y;
    const faceWidth = stats.max.x - stats.min.x;
    const faceDepth = stats.max.z - stats.min.z;

    const fallbackBoxes = [
      {
        name: 'Lower Face Region',
        minX: stats.center.x - faceWidth * 0.35,
        maxX: stats.center.x + faceWidth * 0.35,
        minY: stats.center.y - faceHeight * 0.25,
        maxY: stats.center.y - faceHeight * 0.05,
        minZ: stats.max.z - faceDepth * 0.2,
        maxZ: stats.max.z + faceDepth * 0.1,
      },
      {
        name: 'Center Face Region',
        minX: stats.center.x - faceWidth * 0.2,
        maxX: stats.center.x + faceWidth * 0.2,
        minY: stats.center.y - faceHeight * 0.1,
        maxY: stats.center.y + faceHeight * 0.1,
        minZ: stats.max.z - faceDepth * 0.15,
        maxZ: stats.max.z + faceDepth * 0.05,
      },
      {
        name: 'Wide Search Area',
        minX: stats.center.x - faceWidth * 0.4,
        maxX: stats.center.x + faceWidth * 0.4,
        minY: stats.min.y + faceHeight * 0.3,
        maxY: stats.max.y - faceHeight * 0.2,
        minZ: stats.center.z - faceDepth * 0.3,
        maxZ: stats.center.z + faceDepth * 0.3,
      },
      {
        name: 'Front Face Focus',
        minX: stats.center.x - faceWidth * 0.3,
        maxX: stats.center.x + faceWidth * 0.3,
        minY: stats.center.y - faceHeight * 0.2,
        maxY: stats.center.y + faceHeight * 0.05,
        minZ: stats.max.z - faceDepth * 0.05,
        maxZ: stats.max.z + faceDepth * 0.05,
      },
    ];

    this.logger.log(
      'ANALYSIS',
      `Generated ${fallbackBoxes.length} fallback bounding box strategies`
    );
    return fallbackBoxes;
  }

  findVerticesInRegion(mesh, boundingBox) {
    if (!mesh || !mesh.geometry || !mesh.geometry.attributes.position) {
      return [];
    }

    const positionAttribute = mesh.geometry.attributes.position;
    const vertex = new THREE.Vector3();
    const foundVertices = [];

    const box = new THREE.Box3(
      new THREE.Vector3(boundingBox.minX, boundingBox.minY, boundingBox.minZ),
      new THREE.Vector3(boundingBox.maxX, boundingBox.maxY, boundingBox.maxZ)
    );

    for (let i = 0; i < positionAttribute.count; i++) {
      vertex.fromBufferAttribute(positionAttribute, i);
      if (box.containsPoint(vertex)) {
        foundVertices.push({
          index: i,
          position: vertex.clone(),
          confidence: this.calculateVertexConfidence(vertex, box),
        });
      }
    }

    this.logger.log(
      'ANALYSIS',
      `Found ${foundVertices.length} vertices in region`,
      {
        boundingBox,
        samplePositions: foundVertices.slice(0, 5).map((v) => ({
          index: v.index,
          pos: {
            x: v.position.x.toFixed(3),
            y: v.position.y.toFixed(3),
            z: v.position.z.toFixed(3),
          },
        })),
      }
    );

    return foundVertices;
  }

  calculateVertexConfidence(vertex, boundingBox) {
    const center = boundingBox.getCenter(new THREE.Vector3());
    const size = boundingBox.getSize(new THREE.Vector3());
    const distance = vertex.distanceTo(center);
    const maxDistance = size.length() * 0.5;

    return Math.max(0, 1 - distance / maxDistance);
  }

  clusterVertices(vertices, clusterRadius = 0.02) {
    if (vertices.length === 0) return [];

    const clusters = [];
    const processed = new Set();

    for (let i = 0; i < vertices.length; i++) {
      if (processed.has(i)) continue;

      const cluster = [vertices[i]];
      processed.add(i);

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

    this.logger.log(
      'ANALYSIS',
      `Clustered ${vertices.length} vertices into ${clusters.length} groups`,
      {
        clusterSizes: clusters.map((c) => c.length),
        clusterRadius,
      }
    );

    return clusters;
  }

  validateBoundingBox(boundingBox, meshStats) {
    const issues = [];
    const suggestions = [];

    // Check if bounding box is within mesh bounds
    if (
      boundingBox.minX < meshStats.min.x ||
      boundingBox.maxX > meshStats.max.x
    ) {
      issues.push('X bounds exceed mesh dimensions');
      suggestions.push('Adjust X parameters to fit within mesh bounds');
    }

    if (
      boundingBox.minY < meshStats.min.y ||
      boundingBox.maxY > meshStats.max.y
    ) {
      issues.push('Y bounds exceed mesh dimensions');
      suggestions.push('Adjust Y parameters to fit within mesh bounds');
    }

    if (
      boundingBox.minZ < meshStats.min.z ||
      boundingBox.maxZ > meshStats.max.z
    ) {
      issues.push('Z bounds exceed mesh dimensions');
      suggestions.push('Adjust Z parameters to fit within mesh bounds');
    }

    // Check for reasonable proportions
    const boxWidth = boundingBox.maxX - boundingBox.minX;
    const boxHeight = boundingBox.maxY - boundingBox.minY;
    const faceWidth = meshStats.max.x - meshStats.min.x;
    const faceHeight = meshStats.max.y - meshStats.min.y;

    if (boxWidth > faceWidth * 0.8) {
      issues.push('Bounding box too wide for realistic mouth region');
      suggestions.push('Reduce X range to focus on mouth area');
    }

    if (boxHeight > faceHeight * 0.3) {
      issues.push('Bounding box too tall for realistic mouth region');
      suggestions.push('Reduce Y range to focus on mouth area');
    }

    if (boxWidth < faceWidth * 0.05) {
      issues.push('Bounding box too narrow - may miss mouth vertices');
      suggestions.push('Increase X range to capture full mouth width');
    }

    const isValid = issues.length === 0;
    const confidence = isValid ? 1.0 : Math.max(0, 1 - issues.length * 0.2);

    return {
      valid: isValid,
      confidence,
      issues,
      suggestions,
      dimensions: {
        width: boxWidth,
        height: boxHeight,
        depth: boundingBox.maxZ - boundingBox.minZ,
      },
    };
  }
}
