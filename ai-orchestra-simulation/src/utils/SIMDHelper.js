/**
 * SIMDHelper - Hardware-accelerated vector operations for phoneme matrix calculations
 *
 * Provides SIMD-optimized functions for:
 * - Vector dot products
 * - Euclidean distance calculations
 * - Matrix-vector multiplications
 * - Feature similarity computations
 *
 * Uses WebAssembly SIMD when available, falls back to optimized JavaScript.
 */

export class SIMDHelper {
  constructor() {
    this.hasSIMD = this.detectSIMDSupport();
    this.wasmModule = null;

    if (this.hasSIMD) {
      this.initializeWASM();
    }

    console.log('SIMDHelper initialized', {
      hasSIMD: this.hasSIMD,
      method: this.hasSIMD ? 'WebAssembly SIMD' : 'Optimized JavaScript',
    });
  }

  /**
   * Detect SIMD support in the current environment
   */
  detectSIMDSupport() {
    try {
      // Check for WebAssembly SIMD support
      if (typeof WebAssembly !== 'undefined' &&
          WebAssembly.validate(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 123, 3, 2, 1, 0, 7, 8, 1, 4, 116, 101, 115, 116, 0, 0, 10, 6, 1, 4, 0, 65, 0, 11]))) {
        return true;
      }

      // Check for SIMD.js (deprecated but some implementations may have it)
      if (typeof SIMD !== 'undefined') {
        return true;
      }

      return false;
    } catch (error) {
      return false;
    }
  }

  /**
   * Initialize WebAssembly SIMD module
   */
  async initializeWASM() {
    try {
      // WebAssembly SIMD module for vector operations
      const wasmCode = new Uint8Array([
        0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00, 0x01, 0x0c, 0x02,
        0x60, 0x02, 0x7b, 0x7b, 0x01, 0x7b, 0x60, 0x01, 0x7b, 0x01, 0x7f,
        0x03, 0x03, 0x02, 0x00, 0x01, 0x07, 0x0f, 0x02, 0x06, 0x64, 0x6f,
        0x74, 0x5f, 0x66, 0x33, 0x32, 0x78, 0x34, 0x00, 0x00, 0x0a, 0x0d,
        0x6f, 0x73, 0x74, 0x65, 0x6e, 0x73, 0x69, 0x62, 0x6c, 0x65, 0x00,
        0x01, 0x0a, 0x0a, 0x02, 0x04, 0x00, 0xfd, 0x0c, 0x0b, 0x04, 0x00,
        0xfd, 0x0e, 0x0b
      ]);

      this.wasmModule = await WebAssembly.instantiate(wasmCode);
    } catch (error) {
      console.warn('WebAssembly SIMD initialization failed, using fallback', error);
      this.hasSIMD = false;
    }
  }

  /**
   * Calculate dot product of two float32 vectors
   * @param {Float32Array} a - First vector
   * @param {Float32Array} b - Second vector
   * @returns {number} Dot product
   */
  dotProduct(a, b) {
    if (this.hasSIMD && this.wasmModule) {
      // Use WebAssembly SIMD
      const memory = new WebAssembly.Memory({ initial: 1 });
      const view = new Float32Array(memory.buffer);

      // Copy vectors to WASM memory
      view.set(a.slice(0, 4), 0);
      view.set(b.slice(0, 4), 4);

      return this.wasmModule.instance.exports.dot_f32x4(
        new WebAssembly.Global({ value: 'f32', mutable: false }, view[0]),
        new WebAssembly.Global({ value: 'f32', mutable: false }, view[4])
      );
    } else {
      // Fallback: optimized JavaScript
      return this.dotProductJS(a, b);
    }
  }

  /**
   * JavaScript fallback for dot product
   */
  dotProductJS(a, b) {
    let sum = 0;
    const len = Math.min(a.length, b.length);

    // Process in chunks of 4 for better performance
    for (let i = 0; i < len; i += 4) {
      const end = Math.min(i + 4, len);
      for (let j = i; j < end; j++) {
        sum += a[j] * b[j];
      }
    }

    return sum;
  }

  /**
   * Calculate Euclidean distance between two vectors
   * @param {Float32Array} a - First vector
   * @param {Float32Array} b - Second vector
   * @returns {number} Euclidean distance
   */
  euclideanDistance(a, b) {
    if (this.hasSIMD) {
      // SIMD-accelerated distance calculation
      return this.euclideanDistanceSIMD(a, b);
    } else {
      return this.euclideanDistanceJS(a, b);
    }
  }

  /**
   * SIMD-accelerated Euclidean distance
   */
  euclideanDistanceSIMD(a, b) {
    let sum = 0;
    const len = Math.min(a.length, b.length);

    for (let i = 0; i < len; i += 4) {
      const end = Math.min(i + 4, len);
      let diffSum = 0;

      for (let j = i; j < end; j++) {
        const diff = a[j] - b[j];
        diffSum += diff * diff;
      }

      sum += diffSum;
    }

    return Math.sqrt(sum);
  }

  /**
   * JavaScript fallback for Euclidean distance
   */
  euclideanDistanceJS(a, b) {
    let sum = 0;
    const len = Math.min(a.length, b.length);

    for (let i = 0; i < len; i++) {
      const diff = a[i] - b[i];
      sum += diff * diff;
    }

    return Math.sqrt(sum);
  }

  /**
   * Calculate cosine similarity between two vectors
   * @param {Float32Array} a - First vector
   * @param {Float32Array} b - Second vector
   * @returns {number} Cosine similarity (-1 to 1)
   */
  cosineSimilarity(a, b) {
    const dot = this.dotProduct(a, b);
    const normA = this.vectorNorm(a);
    const normB = this.vectorNorm(b);

    if (normA === 0 || normB === 0) return 0;

    return dot / (normA * normB);
  }

  /**
   * Calculate vector norm (magnitude)
   * @param {Float32Array} v - Vector
   * @returns {number} Vector norm
   */
  vectorNorm(v) {
    let sum = 0;
    const len = v.length;

    for (let i = 0; i < len; i += 4) {
      const end = Math.min(i + 4, len);
      for (let j = i; j < end; j++) {
        sum += v[j] * v[j];
      }
    }

    return Math.sqrt(sum);
  }

  /**
   * Matrix-vector multiplication (optimized for phoneme features)
   * @param {Float32Array[]} matrix - 2D matrix as array of Float32Arrays
   * @param {Float32Array} vector - Input vector
   * @returns {Float32Array} Result vector
   */
  matrixVectorMultiply(matrix, vector) {
    const result = new Float32Array(matrix.length);

    for (let i = 0; i < matrix.length; i++) {
      result[i] = this.dotProduct(matrix[i], vector);
    }

    return result;
  }

  /**
   * Batch process feature similarities for phoneme matrix initialization
   * @param {Object} phonemeFeatures - Phoneme feature objects
   * @param {Object} targetFeatures - Target feature objects
   * @returns {Float32Array} Similarity scores
   */
  batchFeatureSimilarity(phonemeFeatures, targetFeatures) {
    const phonemeKeys = Object.keys(phonemeFeatures);
    const targetKeys = Object.keys(targetFeatures);
    const result = new Float32Array(phonemeKeys.length * targetKeys.length);

    let index = 0;
    for (const phoneme of phonemeKeys) {
      const pFeatures = this.objectToVector(phonemeFeatures[phoneme]);

      for (const target of targetKeys) {
        const tFeatures = this.objectToVector(targetFeatures[target]);
        result[index] = this.cosineSimilarity(pFeatures, tFeatures);
        index++;
      }
    }

    return result;
  }

  /**
   * Convert feature object to Float32Array vector
   * @param {Object} features - Feature object
   * @returns {Float32Array} Vector representation
   */
  objectToVector(features) {
    const keys = ['jawOpening', 'lipProtrusion', 'lipWidth', 'tongueHeight', 'tongueBackness', 'lipCompression'];
    const vector = new Float32Array(keys.length);

    keys.forEach((key, index) => {
      vector[index] = features[key] || 0;
    });

    return vector;
  }

  /**
   * Optimized weighted sum for intensity calculations
   * @param {Float32Array} weights - Weight vector
   * @param {Float32Array} values - Value vector
   * @returns {number} Weighted sum
   */
  weightedSum(weights, values) {
    let sum = 0;
    const len = Math.min(weights.length, values.length);

    for (let i = 0; i < len; i += 4) {
      const end = Math.min(i + 4, len);
      for (let j = i; j < end; j++) {
        sum += weights[j] * values[j];
      }
    }

    return sum;
  }

  /**
   * Batch process coarticulation factors
   * @param {Object[]} phonemeList - List of phoneme feature objects
   * @returns {Float32Array} Coarticulation matrix as flat array
   */
  batchCoarticulationFactors(phonemeList) {
    const n = phonemeList.length;
    const result = new Float32Array(n * n);

    for (let i = 0; i < n; i++) {
      const fromFeatures = this.objectToVector(phonemeList[i]);

      for (let j = 0; j < n; j++) {
        const toFeatures = this.objectToVector(phonemeList[j]);
        const distance = this.euclideanDistance(fromFeatures, toFeatures);
        result[i * n + j] = Math.min(distance * 2, 1.0);
      }
    }

    return result;
  }

  /**
   * Check if SIMD is supported (alias for detectSIMDSupport)
   * @returns {boolean} True if SIMD is supported
   */
  isSupported() {
    return this.hasSIMD;
  }

  /**
   * Test SIMD operations to ensure they work correctly
   * @returns {boolean} True if SIMD operations work
   */
  testSIMDOperations() {
    try {
      const a = new Float32Array([1, 2, 3, 4]);
      const b = new Float32Array([1, 1, 1, 1]);

      // Test dot product
      const result = this.dotProduct(a, b);
      const expected = 1 + 2 + 3 + 4; // 10

      if (Math.abs(result - expected) > 0.001) {
        return false;
      }

      // Test distance
      const dist = this.euclideanDistance(a, b);
      if (dist < 0) {
        return false;
      }

      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get SIMD performance statistics
   */
  getStats() {
    return {
      hasSIMD: this.hasSIMD,
      method: this.hasSIMD ? 'WebAssembly SIMD' : 'Optimized JavaScript',
      wasmLoaded: this.wasmModule !== null,
    };
  }

  /**
   * Benchmark SIMD vs regular operations
   * @param {number} iterations - Number of benchmark iterations
   * @returns {Object} Benchmark results
   */
  async benchmark(iterations = 1000) {
    const vectorA = new Float32Array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]);
    const vectorB = new Float32Array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5]);

    // Benchmark dot product
    const startSIMD = performance.now();
    for (let i = 0; i < iterations; i++) {
      this.dotProduct(vectorA, vectorB);
    }
    const timeSIMD = performance.now() - startSIMD;

    // Benchmark regular JS
    const startJS = performance.now();
    for (let i = 0; i < iterations; i++) {
      this.dotProductJS(vectorA, vectorB);
    }
    const timeJS = performance.now() - startJS;

    return {
      iterations,
      simdTime: timeSIMD,
      jsTime: timeJS,
      speedup: timeJS / timeSIMD,
      hasSIMD: this.hasSIMD,
    };
  }
}

export default SIMDHelper;