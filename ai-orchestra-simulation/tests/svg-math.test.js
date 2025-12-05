/**
 * @file Unit tests for the SVG Mathematics engine.
 *
 * This test suite validates the core mathematical functions, schema logic,
 * and path generation to ensure accuracy, precision, and reliability.
 */

import assert from 'assert';
import { expressionSchema, validateParameters, getDefaultParameters } from '../src/svg-math/expressionSchema.js';
import { linearBezier, quadraticBezier, cubicBezier } from '../src/svg-math/bezierUtils.js';
import { generateMouthPath } from '../src/svg-math/pathGenerator.js';

function runTest(name, testFn) {
  try {
    testFn();
    console.log(`✅ PASS: ${name}`);
  } catch (error) {
    console.error(`❌ FAIL: ${name}`);
    console.error(error);
    process.exit(1); // Exit with error code on failure
  }
}

// --- expressionSchema.js Tests ---

runTest('Schema should contain over 50 parameters', () => {
  assert.ok(Object.keys(expressionSchema).length >= 50, 'Schema has less than 50 parameters.');
});

runTest('getDefaultParameters should return all default values', () => {
  const defaults = getDefaultParameters();
  assert.strictEqual(Object.keys(defaults).length, Object.keys(expressionSchema).length);
  assert.strictEqual(defaults.mouthSmile, 0);
});

runTest('validateParameters should pass for valid parameters', () => {
  const validParams = { mouthSmile: 0.5, eyesBlink: 1.0 };
  assert.doesNotThrow(() => validateParameters(validParams));
});

runTest('validateParameters should throw for an invalid parameter name', () => {
  const invalidParams = { nonExistentParam: 0.5 };
  assert.throws(() => validateParameters(invalidParams), /is not defined in the schema/);
});

runTest('validateParameters should throw for an out-of-range value', () => {
  const invalidParams = { mouthSmile: 1.1 };
  assert.throws(() => validateParameters(invalidParams), /is outside the allowed range/);
});


// --- bezierUtils.js Tests ---

const p0 = { x: 0, y: 0 };
const p1 = { x: 10, y: 10 };
const p2 = { x: 20, y: 0 };
const p3 = { x: 30, y: 10 };

runTest('linearBezier should correctly interpolate a point', () => {
  const midPoint = linearBezier(p0, p1, 0.5);
  assert.deepStrictEqual(midPoint, { x: 5, y: 5 });
});

runTest('quadraticBezier should correctly evaluate a point', () => {
  const midPoint = quadraticBezier(p0, p1, p2, 0.5);
  assert.deepStrictEqual(midPoint, { x: 10, y: 5 });
});

runTest('cubicBezier should correctly evaluate a point', () => {
  const midPoint = cubicBezier(p0, p1, p2, p3, 0.5);
  assert.deepStrictEqual(midPoint, { x: 15, y: 5 });
});


// --- pathGenerator.js Tests ---

runTest('generateMouthPath should return valid SVG path strings', () => {
  const { upper, lower } = generateMouthPath({ mouthSmile: 0.5, mouthOpen: 0.2 });
  assert.ok(upper.startsWith('M 35 57.5 C'), 'Upper path format is incorrect.');
  assert.ok(lower.startsWith('M 35 57.5 C'), 'Lower path format is incorrect.');
});

runTest('generateMouthPath should react to smile parameter', () => {
    const neutral = generateMouthPath();
    const smile = generateMouthPath({ mouthSmile: 1 });
    assert.notStrictEqual(neutral.upper, smile.upper, 'Smile should change the upper path.');
});

console.log('\nAll tests passed successfully!');
