#!/usr/bin/env node

/**
 * Avatar Performance Testing Script
 * Executes comprehensive browser performance tests for Three.js avatar rendering
 * Validates production requirements: 60fps, <50ms sync, <100MB memory
 */

import fs from 'fs';
import path from 'path';
import { chromium, firefox, webkit } from 'playwright';

const TEST_CONFIG = {
  browsers: ['chromium', 'firefox', 'webkit'],
  testUrl: 'http://localhost:9000/test-avatar.html',
  voiceServiceUrl: 'http://localhost:8002',
  httpServerUrl: 'http://localhost:9000',
  targets: {
    fps: 60,
    syncError: 50, // ms
    memory: 100, // MB
    testDuration: 10000 // ms
  }
};

class AvatarPerformanceTester {
  constructor() {
    this.results = {
      browsers: {},
      summary: {
        passed: 0,
        failed: 0,
        total: 0
      }
    };
  }

  async checkPrerequisites() {
    console.log('🔍 Checking prerequisites...');

    // Check HTTP server
    try {
      const response = await fetch(TEST_CONFIG.httpServerUrl + '/test-phase1-browser.html');
      if (!response.ok) throw new Error('HTTP server not responding');
      console.log('✅ HTTP Server running');
    } catch (error) {
      throw new Error(`HTTP Server not available: ${error.message}`);
    }

    // Check Voice service
    try {
      const response = await fetch(TEST_CONFIG.voiceServiceUrl + '/health');
      const health = await response.json();
      if (health.status !== 'healthy') throw new Error('Voice service not healthy');
      console.log('✅ Voice Service running');
    } catch (error) {
      throw new Error(`Voice Service not available: ${error.message}`);
    }
  }

  async runBrowserTest(browserName) {
    console.log(`\n🌐 Testing ${browserName}...`);

    const browserType = browserName === 'chromium' ? chromium :
                       browserName === 'firefox' ? firefox :
                       webkit;

    // Launch browser with appropriate options
    const launchOptions = {
      headless: true,
      args: browserName === 'webkit' ? [] : ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--enable-webgl']
    };

    const browser = await browserType.launch(launchOptions);

    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });

    const page = await context.newPage();
    page.setDefaultTimeout(10000);

    // Log console messages from the page
    page.on('console', msg => console.log(`   [PAGE] ${msg.text()}`));

    const testResults = {
      browser: browserName,
      metrics: {},
      tests: [],
      passed: 0,
      failed: 0
    };

    try {
      // Navigate to test page
      console.log(`   Loading test page...`);
      await page.goto(TEST_CONFIG.testUrl, { waitUntil: 'networkidle' });

      // Wait for avatar to be ready (simpler check)
      console.log(`   Starting performance test...`);
      await page.waitForFunction(
        () => window.avatarTest && window.avatarTest.isAvatarReady(),
        { timeout: 10000 }
      );

      // Wait a bit for performance metrics to stabilize
      await page.waitForTimeout(5000);

      // Extract performance metrics
      console.log(`   Extracting performance metrics...`);

      const metrics = await page.evaluate(() => {
        if (!window.avatarTest) return null;

        return {
          fps: window.avatarTest.getFPS(),
          memoryUsage: window.avatarTest.getMemoryUsage(),
          syncLatency: window.avatarTest.getSyncLatency(),
          isReady: window.avatarTest.isAvatarReady()
        };
      });

      if (!metrics) {
        throw new Error('Avatar test framework not loaded');
      }

      testResults.metrics = metrics;

      // Performance validation
      const { fps, memoryUsage, syncLatency } = metrics;

      const performanceTests = [
        {
          name: 'FPS Target (≥60)',
          passed: fps >= TEST_CONFIG.targets.fps,
          value: fps,
          target: TEST_CONFIG.targets.fps
        },
        {
          name: 'Memory Usage (<100MB)',
          passed: memoryUsage < TEST_CONFIG.targets.memory,
          value: memoryUsage,
          target: TEST_CONFIG.targets.memory
        },
        {
          name: 'Sync Latency (<50ms)',
          passed: syncLatency < TEST_CONFIG.targets.syncError,
          value: syncLatency,
          target: TEST_CONFIG.targets.syncError
        }
      ];

      testResults.performanceTests = performanceTests;
      testResults.passed = performanceTests.filter(t => t.passed).length;
      testResults.failed = performanceTests.filter(t => !t.passed).length;

      console.log(`   ✅ ${testResults.passed} tests passed, ${testResults.failed} failed`);
      console.log(`   📊 FPS: ${fps}, Memory: ${memoryUsage}MB, Sync: ${syncLatency}ms`);

    } catch (error) {
      console.log(`   ❌ Test failed: ${error.message}`);
      testResults.failed++;
      testResults.error = error.message;
    } finally {
      await browser.close();
    }

    return testResults;
  }

  async runAllTests() {
    console.log('🎬 Avatar Performance Testing Suite');
    console.log('=====================================');

    try {
      await this.checkPrerequisites();

      for (const browser of TEST_CONFIG.browsers) {
        const result = await this.runBrowserTest(browser);
        this.results.browsers[browser] = result;
        this.results.summary.total += result.passed + result.failed;
        this.results.summary.passed += result.passed;
        this.results.summary.failed += result.failed;
      }

      this.generateReport();

    } catch (error) {
      console.error(`❌ Testing failed: ${error.message}`);
      process.exit(1);
    }
  }

  generateReport() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 AVATAR PERFORMANCE TEST RESULTS');
    console.log('='.repeat(60));

    let allPassed = true;

    for (const [browser, result] of Object.entries(this.results.browsers)) {
      console.log(`\n🌐 ${browser.toUpperCase()}`);
      console.log('-'.repeat(20));

      if (result.error) {
        console.log(`❌ Browser test failed: ${result.error}`);
        allPassed = false;
        continue;
      }

      // Performance metrics
      const { fps, syncError, memoryUsage } = result.metrics;
      console.log(`📈 Performance Metrics:`);
      console.log(`   FPS: ${fps} (target: ≥${TEST_CONFIG.targets.fps}) ${fps >= TEST_CONFIG.targets.fps ? '✅' : '❌'}`);
      console.log(`   Sync Error: ${syncError}ms (target: <${TEST_CONFIG.targets.syncError}ms) ${syncError < TEST_CONFIG.targets.syncError ? '✅' : '❌'}`);
      console.log(`   Memory: ${memoryUsage}MB (target: <${TEST_CONFIG.targets.memory}MB) ${memoryUsage < TEST_CONFIG.targets.memory ? '✅' : '❌'}`);

      // Test results
      console.log(`\n🧪 Test Results: ${result.passed}/${result.passed + result.failed} passed`);

      result.tests.forEach(test => {
        console.log(`   ${test.passed ? '✅' : '❌'} ${test.name}`);
      });

      if (result.performanceTests) {
        result.performanceTests.forEach(test => {
          console.log(`   ${test.passed ? '✅' : '❌'} ${test.name} (${test.value})`);
        });
      }

      if (result.failed > 0) allPassed = false;
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('🎯 OVERALL SUMMARY');
    console.log('='.repeat(60));

    const { passed, failed, total } = this.results.summary;
    const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;

    console.log(`Total Tests: ${total}`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📊 Pass Rate: ${passRate}%`);

    if (allPassed && passRate >= 80) {
      console.log('\n🎉 ALL REQUIREMENTS MET!');
      console.log('✅ Avatar rendering meets production requirements');
      console.log('🚀 Ready for deployment');
    } else {
      console.log('\n⚠️ REQUIREMENTS NOT FULLY MET');
      console.log('🔧 Additional optimization needed before deployment');
    }

    // Save detailed results
    const reportPath = path.join(process.cwd(), 'avatar-performance-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
    console.log(`\n📄 Detailed report saved: ${reportPath}`);
  }
}

// Run the tests
const tester = new AvatarPerformanceTester();
tester.runAllTests().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});
