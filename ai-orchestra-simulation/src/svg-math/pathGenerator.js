/**
 * @file SVG Path Generation System
 *
 * This file is the core of the "Computational Elegance" engine's visual output.
 * It takes a set of expression parameters and uses the Bezier curve utilities
 * to generate the final SVG path data for various facial features.
 *
 * The system is designed to be modular, with dedicated functions for each
 * major facial feature (mouth, eyes, brows). This allows for easier maintenance
 * and future expansion.
 */

import { expressionSchema, getDefaultParameters } from './expressionSchema.js';
import { createCubicPath } from './bezierUtils.js';

/**
 * Defines the base anchor points for facial features in a normalized coordinate space.
 * These points represent the neutral state of the face.
 * The coordinate system assumes a canvas of 100x100 units for simplicity.
 */
const baseAnchors = {
  mouth: {
    leftCorner: { x: 35, y: 60 },
    rightCorner: { x: 65, y: 60 },
    upperLipTop: { x: 50, y: 55 },
    upperLipBottom: { x: 50, y: 60 },
    lowerLipTop: { x: 50, y: 60 },
    lowerLipBottom: { x: 50, y: 65 },
  },
  // TODO: Add base anchors for eyes and eyebrows
};

/**
 * Generates the SVG path for the mouth based on expression parameters.
 *
 * @param {object} params - A full or partial object of expression parameters.
 * @returns {{upper: string, lower: string}} An object containing the SVG path strings for the upper and lower lips.
 */
export function generateMouthPath(params = {}) {
  const currentParams = { ...getDefaultParameters(), ...params };

  // --- Calculate Control Points based on parameters ---
  const anchors = JSON.parse(JSON.stringify(baseAnchors.mouth)); // Deep copy

  // Smile/Frown affects corner vertical position
  const smileAmount = currentParams.mouthSmile - currentParams.mouthFrown;
  anchors.leftCorner.y -= smileAmount * 5;
  anchors.rightCorner.y -= smileAmount * 5;

  // MouthOpen affects vertical position of lips
  anchors.upperLipTop.y -= currentParams.mouthOpen * 2;
  anchors.upperLipBottom.y += currentParams.mouthOpen * 3;
  anchors.lowerLipTop.y += currentParams.mouthOpen * 3;
  anchors.lowerLipBottom.y += currentParams.mouthOpen * 8;

  // Pucker brings corners inward
  anchors.leftCorner.x += currentParams.mouthPucker * 5;
  anchors.rightCorner.x -= currentParams.mouthPucker * 5;

  // --- Define Bezier control points from anchors ---
  const upperLip = {
    start: anchors.leftCorner,
    control1: { x: 40, y: anchors.upperLipTop.y - smileAmount * 3 },
    control2: { x: 60, y: anchors.upperLipTop.y - smileAmount * 3 },
    end: anchors.rightCorner,
  };

  const lowerLip = {
    start: anchors.leftCorner,
    control1: { x: 40, y: anchors.lowerLipBottom.y - smileAmount * 2 },
    control2: { x: 60, y: anchors.lowerLipBottom.y - smileAmount * 2 },
    end: anchors.rightCorner,
  };

  // --- Generate SVG Path Strings ---
  const upperPath = createCubicPath(
    upperLip.start,
    upperLip.control1,
    upperLip.control2,
    upperLip.end
  );
  const lowerPath = createCubicPath(
    lowerLip.start,
    lowerLip.control1,
    lowerLip.control2,
    lowerLip.end
  );

  return { upper: upperPath, lower: lowerPath };
}

/**
 * Generates all facial feature paths based on the given parameters.
 *
 * @param {object} params - A full or partial object of expression parameters.
 * @returns {{mouth: {upper: string, lower: string}, eyes: object, brows: object}}
 *           An object containing all generated SVG paths.
 */
export function generateFacePaths(params = {}) {
  const mouth = generateMouthPath(params);
  // TODO: Implement eye and eyebrow path generation
  const eyes = { left: '', right: '' };
  const brows = { left: '', right: '' };

  return { mouth, eyes, brows };
}
