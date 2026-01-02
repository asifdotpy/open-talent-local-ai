import * as THREE from 'three';
import { VertexAnalyzer } from './VertexAnalyzer.js';
import { Logger } from '../utils/Logger.js';

/**
 * Comprehensive vertex detection engine with multiple strategies
 */
export class VertexDetectionEngine {
  // Detection confidence multipliers
  static OPTIMAL_CONFIDENCE_FACTOR = 0.9;
  static CURRENT_PARAMS_CONFIDENCE_FACTOR = 0.7;
  static FALLBACK_BASE_CONFIDENCE = 0.6;
  static FALLBACK_CONFIDENCE_DECAY = 0.1;
  static GEOMETRIC_CONFIDENCE_FACTOR = 0.8;

  // Geometric analysis constants
  static FRONT_Z_THRESHOLD = 0.1;
  static SEARCH_RADIUS_FACTOR = 0.3;
  static MOUTH_Y_OFFSET = 0.15;
  static MOUTH_Y_RANGE = 0.4;
  static CLUSTER_DISTANCE_THRESHOLD = 0.03;
  static MIN_CLUSTER_SIZE = 5;

  // Validation thresholds
  static MIN_VERTEX_COUNT = 10;
  static MAX_VERTEX_COUNT = 500;
  static MIN_ASPECT_RATIO = 1.5;
  static MAX_ASPECT_RATIO = 6;
  static CONFIDENCE_PENALTY_PER_ISSUE = 0.2;
  constructor(mesh) {
    this.mesh = mesh;
    this.meshStats = null;
    this.analyzer = new VertexAnalyzer();
    this.logger = Logger.getInstance();

    this.detectionStrategies = [
      {
        name: 'Optimal Anatomical',
        method: this.detectOptimalAnatomical.bind(this),
      },
      {
        name: 'Current Parameters',
        method: this.detectCurrentParameters.bind(this),
      },
      {
        name: 'Fallback Strategies',
        method: this.detectFallbackStrategies.bind(this),
      },
      {
        name: 'Geometric Analysis',
        method: this.detectGeometricAnalysis.bind(this),
      },
    ];
  }

  detectMouthVertices(currentConfig = null) {
    // Validate mesh and initialize
    const validationError = this.validateMeshAndInitialize(currentConfig);
    if (validationError) return validationError;

    let bestResult = null;

    // Try each detection strategy in order
    for (const strategy of this.detectionStrategies) {
      this.logger.log(
        'ANALYSIS',
        `Trying detection strategy: ${strategy.name}`
      );

      const result = strategy.method();
      const validation = this.validateDetection(result.vertices);

      if (validation.valid) {
        this.logger.log(
          'SUCCESS',
          `Strategy "${strategy.name}" found a valid result with ${result.vertices.length} vertices.`
        );
        result.validation = validation;
        return this.createDetectionResult(result.vertices, result.confidence, {
          strategy: strategy.name,
          meshStats: this.meshStats,
          boundingBox: result.boundingBox,
          validation: validation,
        });
      }

      if (!bestResult || result.vertices.length > bestResult.vertices.length) {
        bestResult = result;
        bestResult.validation = validation;
        bestResult.strategy = strategy.name;
      }
    }

    if (bestResult && bestResult.vertices.length > 0) {
      this.logger.log(
        'WARN',
        `No strategy found a valid result. Returning best invalid result from "${bestResult.strategy}" with ${bestResult.vertices.length} vertices.`
      );
      return this.createDetectionResult(
        bestResult.vertices,
        bestResult.confidence,
        {
          strategy: bestResult.strategy,
          meshStats: this.meshStats,
          boundingBox: bestResult.boundingBox,
          validation: bestResult.validation,
          error: 'No valid mouth region found, using best available fallback.',
        }
      );
    }

    return this.createDetectionResult([], 0, {
      strategy: 'All Failed',
      error: 'No detection strategy found mouth vertices',
      meshStats: this.meshStats,
      diagnostics: this.generateDiagnostics(),
    });
  }

  /**
   * Validates mesh and initializes analysis data
   */
  validateMeshAndInitialize(currentConfig) {
    if (
      !this.mesh ||
      !this.mesh.geometry ||
      !this.mesh.geometry.attributes.position
    ) {
      return this.createErrorResult(
        'Invalid mesh or missing position attribute'
      );
    }

    this.meshStats = this.analyzer.analyzeVertexDistribution(this.mesh);
    if (!this.meshStats) {
      return this.createErrorResult(
        'Failed to analyze mesh vertex distribution'
      );
    }

    this.currentConfig = currentConfig;
    return null; // No error
  }

  detectOptimalAnatomical() {
    const optimalBox = this.analyzer.calculateOptimalMouthBoundingBox(
      this.mesh
    );
    if (!optimalBox) return this.createDetectionResult();

    const vertices = this.analyzer.findVerticesInRegion(this.mesh, optimalBox);
    const validation = this.analyzer.validateBoundingBox(
      optimalBox,
      this.meshStats
    );

    return this.createDetectionResult(
      vertices,
      validation.confidence * VertexDetectionEngine.OPTIMAL_CONFIDENCE_FACTOR,
      {
        boundingBox: optimalBox,
        validation,
      }
    );
  }

  detectCurrentParameters() {
    if (!this.currentConfig) return this.createDetectionResult();

    const currentBox = this.createBoundingBoxFromConfig(this.currentConfig);
    const vertices = this.analyzer.findVerticesInRegion(this.mesh, currentBox);
    const validation = this.analyzer.validateBoundingBox(
      currentBox,
      this.meshStats
    );

    return this.createDetectionResult(
      vertices,
      validation.confidence *
        VertexDetectionEngine.CURRENT_PARAMS_CONFIDENCE_FACTOR,
      {
        boundingBox: currentBox,
        validation,
      }
    );
  }

  /**
   * Creates a bounding box from configuration parameters
   */
  createBoundingBoxFromConfig(config) {
    return {
      minX: config.minX,
      maxX: config.maxX,
      minY: config.minY,
      maxY: config.maxY,
      minZ: config.minZ,
      maxZ: config.maxZ,
    };
  }

  detectFallbackStrategies() {
    const fallbackBoxes = this.analyzer.generateFallbackBoundingBoxes(
      this.mesh
    );

    for (let i = 0; i < fallbackBoxes.length; i++) {
      const fallbackBox = fallbackBoxes[i];
      const vertices = this.analyzer.findVerticesInRegion(
        this.mesh,
        fallbackBox
      );

      if (vertices.length > 0) {
        const validation = this.analyzer.validateBoundingBox(
          fallbackBox,
          this.meshStats
        );
        const confidenceMultiplier =
          VertexDetectionEngine.FALLBACK_BASE_CONFIDENCE -
          i * VertexDetectionEngine.FALLBACK_CONFIDENCE_DECAY;

        return this.createDetectionResult(
          vertices,
          validation.confidence * confidenceMultiplier,
          {
            boundingBox: fallbackBox,
            validation,
            fallbackName: fallbackBox.name,
          }
        );
      }
    }

    return this.createDetectionResult();
  }

  detectGeometricAnalysis() {
    const candidateVertices = this.findCandidateVertices();

    if (candidateVertices.length === 0) {
      return this.createDetectionResult();
    }

    const bestCluster = this.findBestVertexCluster(candidateVertices);

    if (bestCluster) {
      return this.createDetectionResult(
        bestCluster.vertices,
        bestCluster.confidence,
        {
          clusterInfo: bestCluster.info,
        }
      );
    }

    return this.createDetectionResult();
  }

  /**
   * Finds candidate vertices using geometric analysis
   * Performance-optimized with pre-calculated bounds
   */
  findCandidateVertices() {
    const positionAttribute = this.mesh.geometry.attributes.position;
    const vertex = new THREE.Vector3();
    const candidateVertices = [];

    // Pre-calculate bounds for performance
    const bounds = this.calculateGeometricBounds();

    for (let i = 0; i < positionAttribute.count; i++) {
      vertex.fromBufferAttribute(positionAttribute, i);

      if (this.isVertexInMouthRegion(vertex, bounds)) {
        candidateVertices.push({
          index: i,
          position: vertex.clone(),
          confidence: this.calculateGeometricConfidence(vertex),
        });
      }
    }

    return candidateVertices;
  }

  /**
   * Pre-calculates geometric bounds for mouth region detection
   */
  calculateGeometricBounds() {
    const zRange = this.meshStats.max.z - this.meshStats.min.z;
    const xRange = this.meshStats.max.x - this.meshStats.min.x;
    const yRange = this.meshStats.max.y - this.meshStats.min.y;

    return {
      frontZ:
        this.meshStats.max.z - zRange * VertexDetectionEngine.FRONT_Z_THRESHOLD,
      centerY: this.meshStats.center.y,
      searchRadius: xRange * VertexDetectionEngine.SEARCH_RADIUS_FACTOR,
      mouthYMin:
        this.meshStats.center.y - yRange * VertexDetectionEngine.MOUTH_Y_RANGE,
      centerX: this.meshStats.center.x,
    };
  }

  /**
   * Checks if a vertex is in the expected mouth region
   */
  isVertexInMouthRegion(vertex, bounds) {
    return (
      vertex.z > bounds.frontZ &&
      Math.abs(vertex.x - bounds.centerX) < bounds.searchRadius &&
      vertex.y < bounds.centerY &&
      vertex.y > bounds.mouthYMin
    );
  }

  /**
   * Finds the best cluster of vertices from candidates
   */
  findBestVertexCluster(candidateVertices) {
    const clusters = this.analyzer.clusterVertices(
      candidateVertices,
      VertexDetectionEngine.CLUSTER_DISTANCE_THRESHOLD
    );

    let bestCluster = null;
    let bestConfidence = 0;

    for (const cluster of clusters) {
      const avgConfidence =
        cluster.reduce((sum, v) => sum + v.confidence, 0) / cluster.length;
      if (
        avgConfidence > bestConfidence &&
        cluster.length >= VertexDetectionEngine.MIN_CLUSTER_SIZE
      ) {
        bestCluster = cluster;
        bestConfidence = avgConfidence;
      }
    }

    if (bestCluster) {
      return {
        vertices: bestCluster,
        confidence:
          bestConfidence * VertexDetectionEngine.GEOMETRIC_CONFIDENCE_FACTOR,
        info: {
          totalClusters: clusters.length,
          selectedClusterSize: bestCluster.length,
          avgConfidence: bestConfidence,
        },
      };
    }

    return null;
  }

  calculateGeometricConfidence(vertex) {
    const yRange = this.meshStats.max.y - this.meshStats.min.y;
    const xRange = this.meshStats.max.x - this.meshStats.min.x;

    const expectedMouthY =
      this.meshStats.center.y - yRange * VertexDetectionEngine.MOUTH_Y_OFFSET;
    const yDistance = Math.abs(vertex.y - expectedMouthY);
    const maxYDistance = yRange * 0.2;

    const xDistance = Math.abs(vertex.x - this.meshStats.center.x);
    const maxXDistance = xRange * 0.25;

    const yConfidence = Math.max(0, 1 - yDistance / maxYDistance);
    const xConfidence = Math.max(0, 1 - xDistance / maxXDistance);

    return (yConfidence + xConfidence) / 2;
  }

  validateDetection(vertices) {
    if (!vertices || vertices.length === 0) {
      return {
        valid: false,
        issues: ['No vertices detected'],
        suggestions: [
          'Try adjusting bounding box parameters',
          'Check model orientation',
        ],
      };
    }

    const issues = [];
    const suggestions = [];

    if (vertices.length < VertexDetectionEngine.MIN_VERTEX_COUNT) {
      issues.push(
        'Very few vertices detected - may not cover full mouth region'
      );
      suggestions.push(
        'Expand bounding box parameters to capture more vertices'
      );
    } else if (vertices.length > VertexDetectionEngine.MAX_VERTEX_COUNT) {
      issues.push('Too many vertices detected - may include non-mouth regions');
      suggestions.push('Narrow bounding box parameters to focus on mouth area');
    }

    const positions = vertices.map((v) => v.position || v);
    const bounds = {
      minX: Math.min(...positions.map((p) => p.x)),
      maxX: Math.max(...positions.map((p) => p.x)),
      minY: Math.min(...positions.map((p) => p.y)),
      maxY: Math.max(...positions.map((p) => p.y)),
    };

    const width = bounds.maxX - bounds.minX;
    const height = bounds.maxY - bounds.minY;
    const aspectRatio = width / height;

    if (aspectRatio < VertexDetectionEngine.MIN_ASPECT_RATIO) {
      issues.push('Detected region too narrow for typical mouth proportions');
      suggestions.push('Increase X range to capture full mouth width');
    } else if (aspectRatio > VertexDetectionEngine.MAX_ASPECT_RATIO) {
      issues.push('Detected region too wide for typical mouth proportions');
      suggestions.push('Decrease X range to focus on mouth area');
    }

    const confidence = Math.max(
      0,
      1 - issues.length * VertexDetectionEngine.CONFIDENCE_PENALTY_PER_ISSUE
    );

    return {
      valid: issues.length === 0,
      confidence,
      issues,
      suggestions,
      vertexCount: vertices.length,
      bounds,
      aspectRatio: aspectRatio.toFixed(2),
    };
  }

  generateDiagnostics() {
    if (!this.meshStats) return {};

    return {
      meshInfo: {
        totalVertices: this.meshStats.count,
        bounds: {
          x: `${this.meshStats.min.x.toFixed(3)} to ${this.meshStats.max.x.toFixed(3)}`,
          y: `${this.meshStats.min.y.toFixed(3)} to ${this.meshStats.max.y.toFixed(3)}`,
          z: `${this.meshStats.min.z.toFixed(3)} to ${this.meshStats.max.z.toFixed(3)}`,
        },
        center: {
          x: this.meshStats.center.x.toFixed(3),
          y: this.meshStats.center.y.toFixed(3),
          z: this.meshStats.center.z.toFixed(3),
        },
      },
      currentParameters: this.currentConfig
        ? {
            minX: this.currentConfig.minX.toFixed(3),
            maxX: this.currentConfig.maxX.toFixed(3),
            minY: this.currentConfig.minY.toFixed(3),
            maxY: this.currentConfig.maxY.toFixed(3),
            minZ: this.currentConfig.minZ.toFixed(3),
            maxZ: this.currentConfig.maxZ.toFixed(3),
          }
        : null,
      recommendations: [
        'Check if model is properly oriented (face forward)',
        'Verify model scale matches expected dimensions',
        'Try adjusting Y parameters - mouth may be at different height',
        'Consider if model uses different coordinate system',
      ],
    };
  }

  /**
   * Factory method for creating standardized detection results
   */
  createDetectionResult(vertices = [], confidence = 0, additionalData = {}) {
    return {
      vertices,
      confidence,
      ...additionalData,
    };
  }

  /**
   * Factory method for creating error results
   */
  createErrorResult(error, strategy = 'None') {
    return this.createDetectionResult([], 0, { strategy, error });
  }
}
