/**
 * Phase 3 Integration Test - Node.js Compatible
 * Tests caching and performance monitoring without browser APIs
 */

import PhonemeMapper from './src/animation/PhonemeMapper.js';
import { Logger } from './src/utils/Logger.js';
import { PerformanceMonitor } from './src/utils/PerformanceMonitor.js';

class Phase3IntegrationTester {
  constructor() {
    this.logger = new Logger('Phase3IntegrationTester');
    this.phonemeMapper = null;
    this.performanceMonitor = null;
  }

  async init() {
    this.logger.log('Initializing Phase 3 Integration Test...', 'info');

    try {
      // Create mock animation controller
      const mockController = {
        setMorphTarget: (index, value, duration) => {
          // Mock implementation
        },
        getMorphTarget: (index) => {
          return Math.random() * 0.5; // Mock current value
        },
        resetMorphTargets: () => {
          // Mock implementation
        }
      };

      // Create performance monitor
      this.performanceMonitor = new PerformanceMonitor({
        animation: { performanceLogInterval: 10 },
        performance: {
          minFPS: 30,
          memoryWarningMB: 100,
        }
      });

      // Initialize PhonemeMapper with Phase 3 features
      this.phonemeMapper = new PhonemeMapper(mockController, {
        l1CacheSize: 50,
        l2CacheSize: 200,
        enableL3Cache: false, // Disable IndexedDB for Node.js
        performanceMonitor: this.performanceMonitor,
      });

      this.logger.log('✅ Phase 3 components initialized successfully', 'success');
      return true;
    } catch (error) {
      this.logger.log(`❌ Initialization failed: ${error.message}`, 'error');
      return false;
    }
  }

  async testCacheFunctionality() {
    this.logger.log('🧪 Testing cache functionality...', 'info');

    const testCases = [
      { phoneme: 'aa', target: 'jawOpen', context: { duration: 100 } },
      { phoneme: 'eh', target: 'mouthSmile', context: { duration: 150 } },
      { phoneme: 'oh', target: 'mouthFunnel', context: { duration: 200 } },
    ];

    let passed = 0;
    let total = 0;

    for (const testCase of testCases) {
      total += 2; // Two calls per test case

      try {
        // First call (should be cache miss)
        const result1 = await this.phonemeMapper.getCachedIntensity(
          testCase.phoneme,
          testCase.target,
          testCase.context
        );

        // Second call (should be cache hit)
        const result2 = await this.phonemeMapper.getCachedIntensity(
          testCase.phoneme,
          testCase.target,
          testCase.context
        );

        if (typeof result1 === 'number' && typeof result2 === 'number') {
          passed += 2;
          this.logger.log(`✅ Cache test passed for ${testCase.phoneme}:${testCase.target}`, 'success');
        } else {
          this.logger.log(`❌ Cache test failed for ${testCase.phoneme}:${testCase.target} - invalid results`, 'error');
        }
      } catch (error) {
        this.logger.log(`❌ Cache test failed for ${testCase.phoneme}:${testCase.target} - ${error.message}`, 'error');
      }
    }

    const successRate = (passed / total * 100).toFixed(1);
    this.logger.log(`📊 Cache functionality test: ${passed}/${total} (${successRate}%)`, 'info');
    return passed === total;
  }

  async testPerformanceMonitoring() {
    this.logger.log('📈 Testing performance monitoring...', 'info');

    try {
      // Simulate some performance data
      for (let i = 0; i < 10; i++) {
        this.performanceMonitor.update(16.67); // ~60fps
        this.performanceMonitor.recordCacheAccess('intensityCache', i % 2 === 0, Math.random() * 10);
      }

      const report = this.performanceMonitor.getPerformanceReport();
      const cacheStats = this.phonemeMapper.getCacheStats();

      if (report && report.average && cacheStats) {
        this.logger.log(`✅ Performance monitoring working - Avg FPS: ${report.average.avgFps}, Cache hits: ${cacheStats.l1Hits + cacheStats.l2Hits + cacheStats.l3Hits}`, 'success');
        return true;
      } else {
        this.logger.log('❌ Performance monitoring not working properly', 'error');
        return false;
      }
    } catch (error) {
      this.logger.log(`❌ Performance monitoring test failed: ${error.message}`, 'error');
      return false;
    }
  }

  async testCoarticulationCaching() {
    this.logger.log('🔗 Testing coarticulation caching...', 'info');

    const testCases = [
      { phoneme: 'b', context: { previousPhoneme: 'aa', nextPhoneme: 'eh' } },
      { phoneme: 'm', context: { previousPhoneme: 'eh', nextPhoneme: 'oh' } },
    ];

    let passed = 0;
    let total = 0;

    for (const testCase of testCases) {
      total += 2;

      try {
        // First call
        const result1 = await this.phonemeMapper.getCachedCoarticulationFactors(
          testCase.phoneme,
          testCase.context
        );

        // Second call
        const result2 = await this.phonemeMapper.getCachedCoarticulationFactors(
          testCase.phoneme,
          testCase.context
        );

        if (result1 && result2 && typeof result1 === 'object' && typeof result2 === 'object') {
          passed += 2;
          this.logger.log(`✅ Coarticulation cache test passed for ${testCase.phoneme}`, 'success');
        } else {
          this.logger.log(`❌ Coarticulation cache test failed for ${testCase.phoneme}`, 'error');
        }
      } catch (error) {
        this.logger.log(`❌ Coarticulation cache test failed for ${testCase.phoneme} - ${error.message}`, 'error');
      }
    }

    const successRate = (passed / total * 100).toFixed(1);
    this.logger.log(`📊 Coarticulation caching test: ${passed}/${total} (${successRate}%)`, 'info');
    return passed === total;
  }

  async runAllTests() {
    this.logger.log('🚀 Starting Phase 3 Integration Tests...', 'info');

    const results = {
      initialization: false,
      cacheFunctionality: false,
      performanceMonitoring: false,
      coarticulationCaching: false,
    };

    // Test initialization
    results.initialization = await this.init();
    if (!results.initialization) {
      this.logger.log('❌ Tests aborted due to initialization failure', 'error');
      return results;
    }

    // Run individual tests
    results.cacheFunctionality = await this.testCacheFunctionality();
    results.performanceMonitoring = await this.testPerformanceMonitoring();
    results.coarticulationCaching = await this.testCoarticulationCaching();

    // Calculate overall results
    const passedTests = Object.values(results).filter(Boolean).length;
    const totalTests = Object.keys(results).length;
    const successRate = (passedTests / totalTests * 100).toFixed(1);

    this.logger.log(`📊 Phase 3 Integration Test Results: ${passedTests}/${totalTests} (${successRate}%)`, 'info');

    if (passedTests === totalTests) {
      this.logger.log('🎉 All Phase 3 tests passed! Implementation is working correctly.', 'success');
    } else {
      this.logger.log('⚠️ Some Phase 3 tests failed. Check implementation.', 'warning');
    }

    return results;
  }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new Phase3IntegrationTester();
  tester.runAllTests().then(results => {
    console.log('\n📋 Final Results:', results);
    process.exit(Object.values(results).every(Boolean) ? 0 : 1);
  }).catch(error => {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  });
}

export default Phase3IntegrationTester;