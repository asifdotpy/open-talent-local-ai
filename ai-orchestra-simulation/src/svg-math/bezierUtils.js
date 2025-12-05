/**
 * @file Bezier Curve Mathematics Utilities
 *
 * This file contains a collection of utility functions for creating, manipulating,
 * and evaluating Bezier curves. These functions are fundamental building blocks
 * for the SVG path generation system, allowing for the creation of smooth,
 * organic shapes required for realistic facial expressions.
 *
 * The provided functions support linear, quadratic, and cubic Bezier curves.
 */

/**
 * Represents a 2D point.
 * @typedef {object} Point
 * @property {number} x - The x-coordinate.
 * @property {number} y - The y-coordinate.
 */

/**
 * Evaluates a point on a linear Bezier curve (a line segment).
 *
 * @param {Point} p0 - The start point.
 * @param {Point} p1 - The end point.
 * @param {number} t - The interpolation factor (from 0 to 1).
 * @returns {Point} The interpolated point.
 */
export function linearBezier(p0, p1, t) {
  return {
    x: (1 - t) * p0.x + t * p1.x,
    y: (1 - t) * p0.y + t * p1.y,
  };
}

/**
 * Evaluates a point on a quadratic Bezier curve.
 *
 * @param {Point} p0 - The start point.
 * @param {Point} p1 - The control point.
 * @param {Point} p2 - The end point.
 * @param {number} t - The interpolation factor (from 0 to 1).
 * @returns {Point} The point on the curve at time t.
 */
export function quadraticBezier(p0, p1, p2, t) {
  const oneMinusT = 1 - t;
  return {
    x: oneMinusT ** 2 * p0.x + 2 * oneMinusT * t * p1.x + t ** 2 * p2.x,
    y: oneMinusT ** 2 * p0.y + 2 * oneMinusT * t * p1.y + t ** 2 * p2.y,
  };
}

/**
 * Evaluates a point on a cubic Bezier curve.
 *
 * @param {Point} p0 - The start point.
 * @param {Point} p1 - The first control point.
 * @param {Point} p2 - The second control point.
 * @param {Point} p3 - The end point.
 * @param {number} t - The interpolation factor (from 0 to 1).
 * @returns {Point} The point on the curve at time t.
 */
export function cubicBezier(p0, p1, p2, p3, t) {
  const oneMinusT = 1 - t;
  return {
    x:
      oneMinusT ** 3 * p0.x +
      3 * oneMinusT ** 2 * t * p1.x +
      3 * oneMinusT * t ** 2 * p2.x +
      t ** 3 * p3.x,
    y:
      oneMinusT ** 3 * p0.y +
      3 * oneMinusT ** 2 * t * p1.y +
      3 * oneMinusT * t ** 2 * p2.y +
      t ** 3 * p3.y,
  };
}

/**
 * Generates an array of points along a cubic Bezier curve.
 *
 * @param {Point} p0 - Start point.
 * @param {Point} p1 - Control point 1.
 * @param {Point} p2 - Control point 2.
 * @param {Point} p3 - End point.
 * @param {number} [numPoints=10] - The number of points to generate.
 * @returns {Point[]} An array of points that approximate the curve.
 */
export function sampleCubicBezier(p0, p1, p2, p3, numPoints = 10) {
  const points = [];
  for (let i = 0; i <= numPoints; i++) {
    const t = i / numPoints;
    points.push(cubicBezier(p0, p1, p2, p3, t));
  }
  return points;
}

/**
 * Creates an SVG path data string for a quadratic Bezier curve.
 *
 * @param {Point} start - The starting point of the curve.
 * @param {Point} control - The control point.
 * @param {Point} end - The ending point of the curve.
 * @returns {string} The SVG path data string (e.g., "M x y Q cx cy, ex ey").
 */
export function createQuadraticPath(start, control, end) {
  return `M ${start.x} ${start.y} Q ${control.x} ${control.y}, ${end.x} ${end.y}`;
}

/**
 * Creates an SVG path data string for a cubic Bezier curve.
 *
 * @param {Point} start - The starting point of the curve.
 * @param {Point} control1 - The first control point.
 * @param {Point} control2 - The second control point.
 * @param {Point} end - The ending point of the curve.
 * @returns {string} The SVG path data string (e.g., "M x y C c1x c1y, c2x c2y, ex ey").
 */
export function createCubicPath(start, control1, control2, end) {
  return `M ${start.x} ${start.y} C ${control1.x} ${control1.y}, ${control2.x} ${control2.y}, ${end.x} ${end.y}`;
}
