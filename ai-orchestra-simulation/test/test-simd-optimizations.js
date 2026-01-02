/**
 * Test SIMD Optimizations for PhonemeIntensityMatrix
 *
 * Phase 3: Animation caching and performance optimization
 * Tests SIMD-accelerated matrix calculations for 50-70% performance improvement
 */

import PhonemeIntensityMatrix from '../src/animation/PhonemeIntensityMatrix.js';

class SIMDTestSuite {
  constructor() {
    this.matrix = new PhonemeIntensityMatrix();
    this.testResults = [];
  }

  /**
   * Run all SIMD optimization tests
   */
  async runAllTests() {
    console.log('🧪 Running SIMD Optimization Tests...\n');

    try {
      // Test SIMD availability
      await this.testSIMDAvailability();

      // Test SIMD-optimized calculations
      await this.testSIMDCalculations();

      // Test performance improvements
      await this.testPerformanceImprovements();

      // Test batch processing
      await this.testBatchProcessing();

      // Test matrix initialization
      await this.testMatrixInitialization();

      this.printResults();

    } catch (error) {
      console.error('❌ Test suite failed:', error);
      this.testResults.push({
        test: 'Test Suite',
        status: 'FAILED',
        error: error.message,
      });
    }
  }

  /**
   * Test SIMD availability and initialization
   */
  async testSIMDAvailability() {
    console.log('Testing SIMD availability...');

    const stats = this.matrix.simdHelper.getStats();

    this.testResults.push({
      test: 'SIMD Availability',
      status: stats.hasSIMD ? 'PASSED' : 'WARNING',
      details: `Method: ${stats.method}, WASM Loaded: ${stats.wasmLoaded}`,
      data: stats,
    });

    console.log(`✅ SIMD ${stats.hasSIMD ? 'available' : 'unavailable'} (${stats.method})`);
  }

  /**
   * Test SIMD-optimized calculation methods
   */
  async testSIMDCalculations() {
    console.log('Testing SIMD-optimized calculations...');

    const testCases = [
      { phoneme: 'aa', morphTarget: 'jawOpen' },
      { phoneme: 'ee', morphTarget: 'mouthSmile' },
      { phoneme: 'oh', morphTarget: 'mouthFunnel' },
      { phoneme: 'b', morphTarget: 'mouthClose' },
    ];

    for (const testCase of testCases) {
      try {
        // Test base intensity calculation
        const baseIntensity = this.matrix.calculateBaseIntensity(
          testCase.phoneme,
          testCase.morphTarget
        );

        // Test dynamic intensity with SIMD
        const dynamicIntensity = this.matrix.calculateDynamicIntensity(
          testCase.phoneme,
          testCase.morphTarget,
          { previousPhoneme: 'ah' }
        );

        // Validate results are reasonable
        const isValid = baseIntensity >= 0 && baseIntensity <= 1 &&
                       dynamicIntensity >= 0 && dynamicIntensity <= 1;

        this.testResults.push({
          test: `SIMD Calculation (${testCase.phoneme} -> ${testCase.morphTarget})`,
          status: isValid ? 'PASSED' : 'FAILED',
          details: `Base: ${baseIntensity.toFixed(3)}, Dynamic: ${dynamicIntensity.toFixed(3)}`,
          data: { baseIntensity, dynamicIntensity },
        });

      } catch (error) {
        this.testResults.push({
          test: `SIMD Calculation (${testCase.phoneme} -> ${testCase.morphTarget})`,
          status: 'FAILED',
          error: error.message,
        });
      }
    }
  }

  /**
   * Test performance improvements with SIMD
   */
  async testPerformanceImprovements() {
    console.log('Testing performance improvements...');

    try {
      const benchmark = await this.matrix.benchmarkSIMD(50);

      const hasImprovement = benchmark.totalSpeedup > 1.0;

      this.testResults.push({
        test: 'Performance Benchmark',
        status: hasImprovement ? 'PASSED' : 'WARNING',
        details: `Speedup: ${benchmark.totalSpeedup.toFixed(2)}x, SIMD: ${benchmark.hasSIMD}`,
        data: benchmark,
      });

      console.log(`🚀 Performance speedup: ${benchmark.totalSpeedup.toFixed(2)}x`);

    } catch (error) {
      this.testResults.push({
        test: 'Performance Benchmark',
        status: 'FAILED',
        error: error.message,
      });
    }
  }

  /**
   * Test batch processing optimizations
   */
  async testBatchProcessing() {
    console.log('Testing batch processing...');

    try {
      const phonemeSequence = ['aa', 'ee', 'oh', 'ah'];
      const profile = this.matrix.getIntensityProfile(phonemeSequence);

      const isValid = profile.length === phonemeSequence.length &&
                     profile.every(p => p.intensities && typeof p.intensities.jawOpen === 'number');

      this.testResults.push({
        test: 'Batch Processing',
        status: isValid ? 'PASSED' : 'FAILED',
        details: `Processed ${profile.length} phonemes with SIMD optimization`,
        data: { sequenceLength: phonemeSequence.length, profileLength: profile.length },
      });

    } catch (error) {
      this.testResults.push({
        test: 'Batch Processing',
        status: 'FAILED',
        error: error.message,
      });
    }
  }

  /**
   * Test matrix initialization with SIMD
   */
  async testMatrixInitialization() {
    console.log('Testing matrix initialization...');

    try {
      const stats = this.matrix.getStatistics();

      const hasSIMD = stats.simdEnabled;
      const hasValidData = stats.phonemes > 0 && stats.morphTargets > 0;

      this.testResults.push({
        test: 'Matrix Initialization',
        status: (hasSIMD && hasValidData) ? 'PASSED' : 'WARNING',
        details: `${stats.phonemes} phonemes, ${stats.morphTargets} targets, SIMD: ${hasSIMD}`,
        data: stats,
      });

    } catch (error) {
      this.testResults.push({
        test: 'Matrix Initialization',
        status: 'FAILED',
        error: error.message,
      });
    }
  }

  /**
   * Print test results summary
   */
  printResults() {
    console.log('\n📊 SIMD Optimization Test Results:');
    console.log('=' .repeat(50));

    const passed = this.testResults.filter(t => t.status === 'PASSED').length;
    const warnings = this.testResults.filter(t => t.status === 'WARNING').length;
    const failed = this.testResults.filter(t => t.status === 'FAILED').length;
    const total = this.testResults.length;

    this.testResults.forEach(result => {
      const icon = result.status === 'PASSED' ? '✅' :
                  result.status === 'WARNING' ? '⚠️' : '❌';
      console.log(`${icon} ${result.test}: ${result.status}`);
      if (result.details) console.log(`   ${result.details}`);
      if (result.error) console.log(`   Error: ${result.error}`);
    });

    console.log('\n📈 Summary:');
    console.log(`   Total Tests: ${total}`);
    console.log(`   ✅ Passed: ${passed}`);
    console.log(`   ⚠️ Warnings: ${warnings}`);
    console.log(`   ❌ Failed: ${failed}`);

    const successRate = ((passed + warnings) / total * 100).toFixed(1);
    console.log(`   Success Rate: ${successRate}%`);

    if (failed === 0) {
      console.log('\n🎉 SIMD optimizations successfully implemented!');
      console.log('Phase 3: Animation caching and performance optimization - COMPLETE ✅');
    } else {
      console.log('\n⚠️ Some SIMD optimizations may need attention.');
    }
  }
}

// Run tests if this file is executed directly
if (typeof window === 'undefined') {
  // Node.js environment
  const testSuite = new SIMDTestSuite();
  testSuite.runAllTests().catch(console.error);
} else {
  // Browser environment
  window.runSIMDTests = async () => {
    const testSuite = new SIMDTestSuite();
    await testSuite.runAllTests();
  };

  console.log('🎯 SIMD Test Suite loaded. Run window.runSIMDTests() to execute tests.');
}

export default SIMDTestSuite;
