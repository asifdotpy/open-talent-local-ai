/**
 * @file Facial Region Mapper
 *
 * This module is responsible for identifying and mapping the vertices of the 3D model
 * to specific facial regions (e.g., mouth, eyes, eyebrows). It uses a bounding box
 * approach, leveraging the existing VertexAnalyzer to find vertices within
 * anatomically estimated regions.
 *
 * This mapping is the critical link between the abstract SVG path deformations
 * and the concrete 3D geometry of the avatar.
 */

import { VertexAnalyzer } from '../animation/VertexAnalyzer.js';
import { Logger } from '../utils/Logger.js';

export class FacialRegionMapper {
  constructor(mesh) {
    this.mesh = mesh;
    this.analyzer = new VertexAnalyzer();
    this.logger = Logger.getInstance();
    this.meshStats = this.analyzer.analyzeVertexDistribution(this.mesh);
    this.regions = new Map();
  }

  /**
   * Calculates and maps all facial regions.
   */
  mapAllRegions() {
    if (!this.meshStats) {
      this.logger.log('ERROR', 'Cannot map regions without mesh statistics.');
      return;
    }

    this.logger.log('MAPPER', 'Starting facial region mapping...');

    const regionDefinitions = this.getRegionDefinitions();

    for (const [name, definition] of Object.entries(regionDefinitions)) {
      const boundingBox = this.calculateBoundingBox(definition);
      const vertices = this.analyzer.findVerticesInRegion(this.mesh, boundingBox);
      this.regions.set(name, {
        vertices,
        boundingBox,
        confidence: this.analyzer.calculateVertexConfidence(vertices[0]?.position, boundingBox) || 0,
      });
      this.logger.log('MAPPER', `Mapped region "${name}" with ${vertices.length} vertices.`);
    }

    this.logger.log('MAPPER', 'Facial region mapping complete.');
  }

  /**
   * Returns the mapped vertices for a specific region.
   * @param {string} regionName - The name of the region (e.g., 'mouth', 'leftEye').
   * @returns {{vertices: object[], boundingBox: object, confidence: number}|undefined}
   */
  getRegion(regionName) {
    return this.regions.get(regionName);
  }

  /**
   * Defines the anatomical properties for each facial region.
   * Values are proportions of the total face dimensions.
   * @returns {object} An object containing definitions for each region.
   */
  getRegionDefinitions() {
    return {
      mouth: { y: -0.15, h: 0.08, w: 0.25, d: 0.15 },
      leftEye: { x: -0.1, y: 0.1, h: 0.06, w: 0.15, d: 0.1 },
      rightEye: { x: 0.1, y: 0.1, h: 0.06, w: 0.15, d: 0.1 },
      leftEyebrow: { x: -0.12, y: 0.2, h: 0.04, w: 0.18, d: 0.1 },
      rightEyebrow: { x: 0.12, y: 0.2, h: 0.04, w: 0.18, d: 0.1 },
      nose: { y: -0.05, h: 0.1, w: 0.1, d: 0.2 },
    };
  }

  /**
   * Calculates a 3D bounding box for a region based on its definition.
   * @param {object} definition - The anatomical definition of the region.
   * @returns {object} A bounding box object with min/max coordinates.
   */
  calculateBoundingBox(definition) {
    const faceHeight = this.meshStats.max.y - this.meshStats.min.y;
    const faceWidth = this.meshStats.max.x - this.meshStats.min.x;
    const faceDepth = this.meshStats.max.z - this.meshStats.min.z;

    const centerX = this.meshStats.center.x + (definition.x || 0) * faceWidth;
    const centerY = this.meshStats.center.y + (definition.y || 0) * faceHeight;

    const height = definition.h * faceHeight;
    const width = definition.w * faceWidth;
    const depth = definition.d * faceDepth;

    return {
      minX: centerX - width,
      maxX: centerX + width,
      minY: centerY - height,
      maxY: centerY + height,
      minZ: this.meshStats.max.z - depth,
      maxZ: this.meshStats.max.z + depth * 0.3, // Bias towards the front
    };
  }
}
