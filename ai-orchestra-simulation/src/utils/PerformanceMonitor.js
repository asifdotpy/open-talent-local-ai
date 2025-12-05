import { Logger } from './Logger.js';

/**
 * Enhanced Performance Monitor for Phase 3 - Caching and Bottleneck Detection
 * Monitors application performance, cache efficiency, and provides intelligent alerts
 */
export class PerformanceMonitor {
  constructor(config) {
    this.config = config;
    this.logger = Logger.getInstance();
    this.frameCount = 0;
    this.lastTime = 0;
    this.performanceHistory = [];
    this.maxHistoryLength = 60; // Keep last 60 measurements
    this.isLipSyncActive = false; // Track if lip-sync is active

    // Phase 3: Cache performance tracking
    this.cacheMetrics = {
      intensityCache: { hits: 0, misses: 0, avgResponseTime: 0 },
      coarticulationCache: { hits: 0, misses: 0, avgResponseTime: 0 },
      totalCacheRequests: 0,
    };

    // Phase 3: Bottleneck detection
    this.bottlenecks = {
      matrixCalculations: [],
      coarticulationProcessing: [],
      blendOperations: [],
      cacheOperations: [],
    };

    // Phase 3: Alerting system
    this.alerts = [];
    this.alertThresholds = {
      cacheHitRate: 0.7, // 70% minimum cache hit rate
      maxResponseTime: 50, // 50ms max response time
      memoryGrowthRate: 10, // MB per minute
      consecutiveLowFPS: 5, // frames
    };

    // Phase 3: A/B testing support
    this.abTests = new Map();
    this.currentTestVariant = null;

    this.logger.log('Phase 3 Performance Monitor initialized', {
      cacheTracking: true,
      bottleneckDetection: true,
      alertingEnabled: true,
    });
  }

  update(deltaTime) {
    this.frameCount++;
    const currentTime = performance.now();

    // Calculate performance metrics
    const fps = deltaTime > 0 ? Math.round(1000 / deltaTime) : 0;
    const memory = performance.memory
      ? Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)
      : 0;

    const stats = {
      fps,
      memory,
      frame: this.frameCount,
      timestamp: currentTime,
      // Phase 3: Add cache metrics
      cacheHitRate: this.getCacheHitRate(),
      avgCacheResponseTime: this.getAverageCacheResponseTime(),
    };

    // Add to history
    this.performanceHistory.push(stats);
    if (this.performanceHistory.length > this.maxHistoryLength) {
      this.performanceHistory.shift();
    }

    // Log performance at intervals
    if (this.frameCount % this.config.animation.performanceLogInterval === 0) {
      this.logPerformance(stats);
    }

    // Phase 3: Check for performance issues with enhanced detection
    this.checkPerformanceThresholds(stats);

    // Phase 3: Check cache performance
    this.checkCachePerformance();

    return stats;
  }

  // Phase 3: Cache performance tracking
  recordCacheAccess(type, isHit, responseTime) {
    if (!this.cacheMetrics[type]) {
      this.cacheMetrics[type] = { hits: 0, misses: 0, avgResponseTime: 0 };
    }

    const metric = this.cacheMetrics[type];
    if (isHit) {
      metric.hits++;
    } else {
      metric.misses++;
    }

    // Update rolling average response time
    const totalRequests = metric.hits + metric.misses;
    metric.avgResponseTime = (metric.avgResponseTime * (totalRequests - 1) + responseTime) / totalRequests;

    this.cacheMetrics.totalCacheRequests++;
  }

  // Phase 3: Bottleneck detection
  recordBottleneck(operation, duration, threshold) {
    if (duration > threshold) {
      const bottleneck = {
        operation,
        duration,
        threshold,
        timestamp: performance.now(),
        frame: this.frameCount,
      };

      // Keep only recent bottlenecks (last 100)
      if (!this.bottlenecks[operation]) {
        this.bottlenecks[operation] = [];
      }

      this.bottlenecks[operation].push(bottleneck);
      if (this.bottlenecks[operation].length > 100) {
        this.bottlenecks[operation].shift();
      }

      // Alert on critical bottlenecks
      if (duration > threshold * 2) {
        this.addAlert('CRITICAL_BOTTLENECK', {
          operation,
          duration,
          threshold,
          severity: 'high',
        });
      }
    }
  }

  // Phase 3: A/B testing support
  startABTest(testName, variants) {
    this.abTests.set(testName, {
      variants,
      startTime: performance.now(),
      measurements: new Map(),
    });
    this.logger.log('A/B test started', { testName, variants });
  }

  recordABMeasurement(testName, variant, metric, value) {
    if (!this.abTests.has(testName)) return;

    const test = this.abTests.get(testName);
    if (!test.measurements.has(variant)) {
      test.measurements.set(variant, new Map());
    }

    const variantMetrics = test.measurements.get(variant);
    if (!variantMetrics.has(metric)) {
      variantMetrics.set(metric, []);
    }

    variantMetrics.get(metric).push({
      value,
      timestamp: performance.now(),
    });
  }

  getABTestResults(testName) {
    if (!this.abTests.has(testName)) return null;

    const test = this.abTests.get(testName);
    const results = {};

    for (const [variant, metrics] of test.measurements) {
      results[variant] = {};
      for (const [metric, measurements] of metrics) {
        const values = measurements.map(m => m.value);
        results[variant][metric] = {
          avg: values.reduce((a, b) => a + b, 0) / values.length,
          min: Math.min(...values),
          max: Math.max(...values),
          count: values.length,
        };
      }
    }

    return results;
  }

  logPerformance(stats) {
    const cacheInfo = this.getCachePerformanceSummary();
    this.logger.log(
      'PERFORMANCE',
      `Frame ${stats.frame}: ${stats.fps}fps, ${stats.memory}MB, Cache: ${cacheInfo.hitRate}% hit rate`
    );
  }

  checkPerformanceThresholds(stats) {
    const isLipSyncActive = this.isLipSyncActive || false;
    const fpsThreshold = isLipSyncActive ? this.config.performance.minFPS : 15;

    // FPS monitoring with consecutive frame tracking
    if (stats.fps < fpsThreshold && stats.fps > 0) {
      this.addAlert('LOW_FPS', {
        fps: stats.fps,
        threshold: fpsThreshold,
        consecutiveFrames: this.getConsecutiveLowFPS(),
        lipSyncActive: isLipSyncActive,
      });
    }

    // Memory monitoring
    if (stats.memory > this.config.performance.memoryWarningMB) {
      this.addAlert('HIGH_MEMORY', {
        memory: stats.memory,
        threshold: this.config.performance.memoryWarningMB,
      });
    }

    // Phase 3: Memory growth rate monitoring
    const growthRate = this.calculateMemoryGrowthRate();
    if (growthRate > this.alertThresholds.memoryGrowthRate) {
      this.addAlert('MEMORY_LEAK', {
        growthRate,
        threshold: this.alertThresholds.memoryGrowthRate,
      });
    }
  }

  // Phase 3: Enhanced cache performance checking
  checkCachePerformance() {
    const hitRate = this.getCacheHitRate();
    const avgResponseTime = this.getAverageCacheResponseTime();

    if (hitRate < this.alertThresholds.cacheHitRate) {
      this.addAlert('LOW_CACHE_HIT_RATE', {
        hitRate,
        threshold: this.alertThresholds.cacheHitRate,
      });
    }

    if (avgResponseTime > this.alertThresholds.maxResponseTime) {
      this.addAlert('SLOW_CACHE_RESPONSE', {
        avgResponseTime,
        threshold: this.alertThresholds.maxResponseTime,
      });
    }
  }

  addAlert(type, data) {
    const alert = {
      type,
      data,
      timestamp: performance.now(),
      frame: this.frameCount,
    };

    this.alerts.push(alert);

    // Keep only recent alerts (last 50)
    if (this.alerts.length > 50) {
      this.alerts.shift();
    }

    // Log critical alerts immediately
    if (type.includes('CRITICAL') || data.severity === 'high') {
      this.logger.log('ERROR', `Performance Alert: ${type}`, data);
    }
  }

  getAlerts(since = 0) {
    return this.alerts.filter(alert => alert.timestamp > since);
  }

  getCacheHitRate() {
    const total = this.cacheMetrics.totalCacheRequests;
    if (total === 0) return 1.0;

    let totalHits = 0;
    for (const metric of Object.values(this.cacheMetrics)) {
      if (typeof metric === 'object' && metric.hits !== undefined) {
        totalHits += metric.hits;
      }
    }

    return totalHits / total;
  }

  getAverageCacheResponseTime() {
    const metrics = Object.values(this.cacheMetrics).filter(m => typeof m === 'object' && m.avgResponseTime);
    if (metrics.length === 0) return 0;

    return metrics.reduce((sum, m) => sum + m.avgResponseTime, 0) / metrics.length;
  }

  getCachePerformanceSummary() {
    return {
      hitRate: (this.getCacheHitRate() * 100).toFixed(1),
      avgResponseTime: this.getAverageCacheResponseTime().toFixed(2),
      totalRequests: this.cacheMetrics.totalCacheRequests,
    };
  }

  getConsecutiveLowFPS() {
    if (this.performanceHistory.length < 2) return 0;

    let consecutive = 0;
    const isLipSyncActive = this.isLipSyncActive || false;
    const fpsThreshold = isLipSyncActive ? this.config.performance.minFPS : 15;

    for (let i = this.performanceHistory.length - 1; i >= 0; i--) {
      if (this.performanceHistory[i].fps >= fpsThreshold) break;
      consecutive++;
    }

    return consecutive;
  }

  calculateMemoryGrowthRate() {
    if (this.performanceHistory.length < 10) return 0;

    const recent = this.performanceHistory.slice(-10);
    const oldest = recent[0];
    const newest = recent[recent.length - 1];

    const timeDiff = (newest.timestamp - oldest.timestamp) / 1000 / 60; // minutes
    const memoryDiff = newest.memory - oldest.memory;

    return timeDiff > 0 ? memoryDiff / timeDiff : 0;
  }

  getAveragePerformance(sampleSize = 30) {
    if (this.performanceHistory.length === 0) return null;

    const samples = this.performanceHistory.slice(-sampleSize);
    const avgFps = samples.reduce((sum, s) => sum + s.fps, 0) / samples.length;
    const avgMemory =
      samples.reduce((sum, s) => sum + s.memory, 0) / samples.length;
    const avgCacheHitRate = samples.reduce((sum, s) => sum + (s.cacheHitRate || 0), 0) / samples.length;

    return {
      avgFps: Math.round(avgFps),
      avgMemory: Math.round(avgMemory),
      avgCacheHitRate: (avgCacheHitRate * 100).toFixed(1),
      sampleSize: samples.length,
    };
  }

  getPerformanceReport() {
    const current = this.performanceHistory[this.performanceHistory.length - 1];
    const average = this.getAveragePerformance();

    return {
      current,
      average,
      totalFrames: this.frameCount,
      historyLength: this.performanceHistory.length,
      cachePerformance: this.getCachePerformanceSummary(),
      bottlenecks: this.bottlenecks,
      alerts: this.getAlerts(),
      abTestResults: this.getABTestResults(),
      thresholds: {
        minFPS: this.config.performance.minFPS,
        memoryWarningMB: this.config.performance.memoryWarningMB,
        ...this.alertThresholds,
      },
    };
  }

  setLipSyncActive(active) {
    this.isLipSyncActive = active;
  }

  reset() {
    this.frameCount = 0;
    this.lastTime = 0;
    this.performanceHistory = [];
    this.cacheMetrics = {
      intensityCache: { hits: 0, misses: 0, avgResponseTime: 0 },
      coarticulationCache: { hits: 0, misses: 0, avgResponseTime: 0 },
      totalCacheRequests: 0,
    };
    this.bottlenecks = {
      matrixCalculations: [],
      coarticulationProcessing: [],
      blendOperations: [],
      cacheOperations: [],
    };
    this.alerts = [];
    this.logger.log('INFO', 'Performance monitor reset (Phase 3)');
  }

  dispose() {
    this.performanceHistory = [];
    this.abTests.clear();
  }
}
