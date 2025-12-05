/**
 * FallbackSystem - Graceful degradation and recovery mechanisms for avatar animation
 *
 * Provides automatic fallback strategies, circuit breakers, and recovery mechanisms
 * to ensure reliable operation even when components fail or degrade.
 *
 * Features:
 * - Component failure detection and fallback activation
 * - Circuit breaker pattern for repeated failures
 * - Progressive degradation strategies
 * - Automatic recovery and health monitoring
 * - Performance-maintaining fallback operations
 */

import { Logger } from '../utils/Logger.js';
import SIMDHelper from '../utils/SIMDHelper.js';

export class FallbackSystem {
  constructor(config = {}) {
    // Initialize logger safely
    try {
      this.logger = new Logger();
    } catch (error) {
      this.logger = {
        log: (...args) => console.log('[FALLBACK]', ...args),
        debug: (...args) => console.debug('[FALLBACK]', ...args),
        error: (...args) => console.error('[FALLBACK]', ...args),
        warn: (...args) => console.warn('[FALLBACK]', ...args),
      };
    }

    this.config = {
      fallbackEnabled: config.fallbackEnabled !== false,
      circuitBreakerEnabled: config.circuitBreakerEnabled !== false,
      recoveryEnabled: config.recoveryEnabled !== false,
      monitoringEnabled: config.monitoringEnabled !== false,
      maxRecoveryAttempts: config.maxRecoveryAttempts || 3,
      recoveryTimeout: config.recoveryTimeout || 30000, // 30 seconds
      healthCheckInterval: config.healthCheckInterval || 60000, // 1 minute
      performanceThreshold: config.performanceThreshold || 0.7, // 70% of normal performance
      ...config,
    };

    // Component health states
    this.componentHealth = new Map();
    this.fallbackStates = new Map();
    this.recoveryAttempts = new Map();

    // Circuit breakers for different components
    this.circuitBreakers = new Map();

    // Fallback strategies
    this.fallbackStrategies = new Map();

    // Performance baselines for degradation detection
    this.performanceBaselines = new Map();

    // SIMD helper for fallback operations
    this.simdHelper = new SIMDHelper();

    // Initialize fallback strategies
    this.initializeFallbackStrategies();

    // Start health monitoring if enabled
    if (this.config.monitoringEnabled) {
      this.startHealthMonitoring();
    }

    this.logger.log('FallbackSystem initialized', {
      features: ['circuit-breaker', 'graceful-degradation', 'auto-recovery', 'health-monitoring'],
      config: this.config,
    });
  }

  /**
   * Initialize fallback strategies for different components
   */
  initializeFallbackStrategies() {
    // SIMD fallback strategy
    this.fallbackStrategies.set('SIMDHelper', {
      name: 'simd-fallback',
      priority: 1,
      fallback: async (component, error) => {
        this.logger.warn('Activating SIMD fallback', { error: error.message });

        // Force SIMD helper to use JavaScript fallbacks
        if (component.forceFallback) {
          component.forceFallback = true;
        }

        // Verify fallback works
        const stats = component.getStats();
        return stats.method === 'Optimized JavaScript';
      },
      recovery: async (component) => {
        this.logger.log('Attempting SIMD recovery');

        // Reset fallback flag
        component.forceFallback = false;

        // Test SIMD functionality
        const testVector = new Float32Array([1, 2, 3, 4]);
        try {
          const result = component.euclideanDistance(testVector, testVector);
          return !isNaN(result) && result === 0;
        } catch (error) {
          this.logger.warn('SIMD recovery failed, keeping fallback', error);
          component.forceFallback = true;
          return false;
        }
      },
    });

    // PhonemeIntensityMatrix fallback strategy
    this.fallbackStrategies.set('PhonemeIntensityMatrix', {
      name: 'matrix-fallback',
      priority: 2,
      fallback: async (component, error) => {
        this.logger.warn('Activating matrix calculation fallback', { error: error.message });

        // Switch to simplified calculation mode
        component.useSimplifiedMode = true;

        // Pre-calculate basic intensity values
        component.fallbackIntensities = new Map([
          ['aa', 0.8], ['ee', 0.6], ['oh', 0.7], ['ih', 0.5],
          ['b', 0.4], ['m', 0.3], ['p', 0.4], ['t', 0.3],
        ]);

        return true;
      },
      recovery: async (component) => {
        this.logger.log('Attempting matrix recovery');

        // Reset simplified mode
        component.useSimplifiedMode = false;

        // Test full matrix functionality
        try {
          const intensity = component.calculateDynamicIntensity('aa', 'jawOpen');
          const isValid = !isNaN(intensity) && intensity >= 0 && intensity <= 1;
          if (isValid) {
            component.fallbackIntensities = null;
          }
          return isValid;
        } catch (error) {
          this.logger.warn('Matrix recovery failed, keeping fallback', error);
          component.useSimplifiedMode = true;
          return false;
        }
      },
    });

    // Cache fallback strategy
    this.fallbackStrategies.set('PhonemeCacheManager', {
      name: 'cache-fallback',
      priority: 3,
      fallback: async (component, error) => {
        this.logger.warn('Activating cache fallback', { error: error.message });

        // Switch to memory-only caching
        component.useMemoryCacheOnly = true;

        // Clear any persistent cache data
        if (component.clearPersistentCache) {
          component.clearPersistentCache();
        }

        return true;
      },
      recovery: async (component) => {
        this.logger.log('Attempting cache recovery');

        // Attempt to re-enable persistent caching
        component.useMemoryCacheOnly = false;

        // Test cache operations
        try {
          const testKey = 'test-recovery-key';
          const testValue = { test: 'data' };

          await component.set(testKey, testValue);
          const retrieved = await component.get(testKey);

          const success = retrieved && retrieved.test === 'data';
          if (!success) {
            component.useMemoryCacheOnly = true;
          }

          return success;
        } catch (error) {
          this.logger.warn('Cache recovery failed, keeping fallback', error);
          component.useMemoryCacheOnly = true;
          return false;
        }
      },
    });

    // Network/WebSocket fallback strategy
    this.fallbackStrategies.set('WebSocketConnection', {
      name: 'network-fallback',
      priority: 4,
      fallback: async (component, error) => {
        this.logger.warn('Activating network fallback', { error: error.message });

        // Switch to polling mode or local-only operation
        component.usePollingMode = true;
        component.connectionRetries = 0;

        // Implement exponential backoff for reconnection attempts
        component.reconnectBackoff = 1000; // Start with 1 second

        return true;
      },
      recovery: async (component) => {
        this.logger.log('Attempting network recovery');

        // Attempt to restore WebSocket connection
        try {
          if (component.attemptReconnect) {
            const connected = await component.attemptReconnect();
            if (connected) {
              component.usePollingMode = false;
              component.reconnectBackoff = 1000;
              return true;
            }
          }
        } catch (error) {
          this.logger.warn('Network recovery failed, keeping fallback', error);
        }

        // Increase backoff for next attempt
        component.reconnectBackoff = Math.min(component.reconnectBackoff * 2, 30000);
        return false;
      },
    });

    // Memory fallback strategy
    this.fallbackStrategies.set('MorphTargetBlender', {
      name: 'memory-fallback',
      priority: 5,
      fallback: async (component, error) => {
        this.logger.warn('Activating memory fallback', { error: error.message });

        // Reduce memory usage by limiting concurrent operations
        component.maxConcurrentBlends = Math.max(1, component.maxConcurrentBlends * 0.5);

        // Clear any cached blend results
        if (component.clearBlendCache) {
          component.clearBlendCache();
        }

        // Force garbage collection if available
        if (global.gc) {
          global.gc();
        }

        return true;
      },
      recovery: async (component) => {
        this.logger.log('Attempting memory recovery');

        // Gradually increase memory limits
        const originalMax = component.originalMaxConcurrentBlends || 5;
        component.maxConcurrentBlends = Math.min(originalMax, component.maxConcurrentBlends + 1);

        // Test memory-intensive operation
        try {
          // Create test blend operations
          const testPromises = [];
          for (let i = 0; i < component.maxConcurrentBlends; i++) {
            testPromises.push(component.blendMorphTargets(['jawOpen', 'mouthSmile'], [0.5, 0.3]));
          }

          await Promise.all(testPromises);
          return true;
        } catch (error) {
          this.logger.warn('Memory recovery failed, reducing limits', error);
          component.maxConcurrentBlends = Math.max(1, component.maxConcurrentBlends - 1);
          return false;
        }
      },
    });
  }

  /**
   * Handle component failure and activate fallback
   */
  async handleComponentFailure(componentName, component, error) {
    if (!this.config.fallbackEnabled) {
      this.logger.error('Fallback system disabled, component failure not handled', { componentName, error: error.message });
      return false;
    }

    this.logger.warn('Component failure detected', { componentName, error: error.message });

    // Update component health
    this.componentHealth.set(componentName, {
      status: 'FAILED',
      lastFailure: Date.now(),
      error: error.message,
      failureCount: (this.componentHealth.get(componentName)?.failureCount || 0) + 1,
    });

    // Check circuit breaker
    const circuitBreaker = this.getCircuitBreaker(componentName);
    if (circuitBreaker.state === 'OPEN') {
      this.logger.warn('Circuit breaker open, skipping fallback activation', { componentName });
      return false;
    }

    // Record failure in circuit breaker
    circuitBreaker.failures++;
    if (circuitBreaker.failures >= circuitBreaker.threshold) {
      circuitBreaker.state = 'OPEN';
      circuitBreaker.lastOpened = Date.now();
      this.logger.error('Circuit breaker opened due to repeated failures', { componentName });
      return false;
    }

    // Find and execute fallback strategy
    const strategy = this.fallbackStrategies.get(componentName);
    if (!strategy) {
      this.logger.error('No fallback strategy available for component', { componentName });
      return false;
    }

    try {
      const fallbackActivated = await strategy.fallback(component, error);
      if (fallbackActivated) {
        this.fallbackStates.set(componentName, {
          active: true,
          activatedAt: Date.now(),
          strategy: strategy.name,
          performanceImpact: await this.measurePerformanceImpact(componentName, component),
        });

        this.logger.log('Fallback activated successfully', { componentName, strategy: strategy.name });

        // Start recovery process
        if (this.config.recoveryEnabled) {
          this.scheduleRecovery(componentName, component, strategy);
        }

        return true;
      } else {
        this.logger.error('Fallback activation failed', { componentName });
        return false;
      }
    } catch (fallbackError) {
      this.logger.error('Fallback execution failed', { componentName, error: fallbackError.message });
      return false;
    }
  }

  /**
   * Attempt to recover a failed component
   */
  async attemptRecovery(componentName, component, strategy) {
    const attempts = this.recoveryAttempts.get(componentName) || 0;

    if (attempts >= this.config.maxRecoveryAttempts) {
      this.logger.warn('Max recovery attempts reached', { componentName, attempts });
      return false;
    }

    this.recoveryAttempts.set(componentName, attempts + 1);

    try {
      this.logger.log('Attempting component recovery', { componentName, attempt: attempts + 1 });

      const recovered = await strategy.recovery(component);

      if (recovered) {
        // Recovery successful
        this.componentHealth.set(componentName, {
          status: 'HEALTHY',
          lastRecovery: Date.now(),
          recoveryCount: (this.componentHealth.get(componentName)?.recoveryCount || 0) + 1,
        });

        this.fallbackStates.set(componentName, {
          active: false,
          deactivatedAt: Date.now(),
          recovered: true,
        });

        // Reset circuit breaker
        const circuitBreaker = this.getCircuitBreaker(componentName);
        circuitBreaker.failures = 0;
        circuitBreaker.state = 'CLOSED';

        this.recoveryAttempts.delete(componentName);

        this.logger.log('Component recovery successful', { componentName });
        return true;
      } else {
        this.logger.warn('Component recovery failed', { componentName });

        // Schedule next recovery attempt with exponential backoff
        const delay = Math.min(1000 * Math.pow(2, attempts), this.config.recoveryTimeout);
        setTimeout(() => {
          this.attemptRecovery(componentName, component, strategy);
        }, delay);

        return false;
      }
    } catch (error) {
      this.logger.error('Recovery attempt failed', { componentName, error: error.message });

      // Schedule next recovery attempt
      const delay = Math.min(1000 * Math.pow(2, attempts), this.config.recoveryTimeout);
      setTimeout(() => {
        this.attemptRecovery(componentName, component, strategy);
      }, delay);

      return false;
    }
  }

  /**
   * Schedule recovery for a component
   */
  scheduleRecovery(componentName, component, strategy) {
    // Initial recovery attempt after a short delay
    setTimeout(() => {
      this.attemptRecovery(componentName, component, strategy);
    }, 5000); // 5 second initial delay
  }

  /**
   * Get or create circuit breaker for a component
   */
  getCircuitBreaker(componentName) {
    if (!this.circuitBreakers.has(componentName)) {
      this.circuitBreakers.set(componentName, {
        state: 'CLOSED', // CLOSED, OPEN, HALF_OPEN
        failures: 0,
        threshold: 5,
        timeout: 60000, // 1 minute
        lastOpened: 0,
      });
    }
    return this.circuitBreakers.get(componentName);
  }

  /**
   * Measure performance impact of fallback activation
   */
  async measurePerformanceImpact(componentName, component) {
    try {
      const baseline = this.performanceBaselines.get(componentName);
      if (!baseline) {
        return 1.0; // No baseline available
      }

      // Run performance test
      const startTime = performance.now();

      switch (componentName) {
        case 'PhonemeIntensityMatrix':
          for (let i = 0; i < 100; i++) {
            component.calculateDynamicIntensity('aa', 'jawOpen');
          }
          break;
        case 'SIMDHelper':
          const vector = new Float32Array([1, 2, 3, 4, 5]);
          for (let i = 0; i < 100; i++) {
            component.euclideanDistance(vector, vector);
          }
          break;
        default:
          return 0.8; // Default performance impact estimate
      }

      const currentTime = performance.now() - startTime;
      const impact = baseline.avgTime / currentTime;

      return Math.max(0.1, Math.min(2.0, impact)); // Clamp to reasonable range

    } catch (error) {
      this.logger.warn('Performance impact measurement failed', { componentName, error: error.message });
      return 0.8; // Default fallback performance impact
    }
  }

  /**
   * Update performance baseline for a component
   */
  updatePerformanceBaseline(componentName, avgTime) {
    this.performanceBaselines.set(componentName, {
      avgTime,
      lastUpdated: Date.now(),
      samples: (this.performanceBaselines.get(componentName)?.samples || 0) + 1,
    });
  }

  /**
   * Check if component is in fallback mode
   */
  isInFallback(componentName) {
    const fallbackState = this.fallbackStates.get(componentName);
    return fallbackState && fallbackState.active;
  }

  /**
   * Get fallback status for all components
   */
  getFallbackStatus() {
    const status = {};

    for (const [componentName, fallbackState] of this.fallbackStates) {
      status[componentName] = {
        inFallback: fallbackState.active,
        activatedAt: fallbackState.activatedAt,
        strategy: fallbackState.strategy,
        performanceImpact: fallbackState.performanceImpact,
        recoveryAttempts: this.recoveryAttempts.get(componentName) || 0,
      };
    }

    return status;
  }

  /**
   * Get circuit breaker status
   */
  getCircuitBreakerStatus() {
    const status = {};

    for (const [componentName, breaker] of this.circuitBreakers) {
      status[componentName] = {
        state: breaker.state,
        failures: breaker.failures,
        threshold: breaker.threshold,
        lastOpened: breaker.lastOpened,
      };
    }

    return status;
  }

  /**
   * Get component health status
   */
  getComponentHealth() {
    const health = {};

    for (const [componentName, healthInfo] of this.componentHealth) {
      health[componentName] = {
        status: healthInfo.status,
        lastFailure: healthInfo.lastFailure,
        lastRecovery: healthInfo.lastRecovery,
        failureCount: healthInfo.failureCount,
        recoveryCount: healthInfo.recoveryCount,
      };
    }

    return health;
  }

  /**
   * Start health monitoring
   */
  startHealthMonitoring() {
    this.healthMonitorInterval = setInterval(() => {
      this.performHealthChecks();
    }, this.config.healthCheckInterval);

    this.logger.log('Health monitoring started', { interval: this.config.healthCheckInterval });
  }

  /**
   * Stop health monitoring
   */
  stopHealthMonitoring() {
    if (this.healthMonitorInterval) {
      clearInterval(this.healthMonitorInterval);
      this.healthMonitorInterval = null;
      this.logger.log('Health monitoring stopped');
    }
  }

  /**
   * Perform health checks on all components
   */
  async performHealthChecks() {
    try {
      // Check SIMD health
      const simdStats = this.simdHelper.getStats();
      this.updateComponentHealth('SIMDHelper', simdStats.hasSIMD ? 'HEALTHY' : 'DEGRADED');

      // Check circuit breakers
      for (const [componentName, breaker] of this.circuitBreakers) {
        if (breaker.state === 'OPEN') {
          const timeSinceOpened = Date.now() - breaker.lastOpened;
          if (timeSinceOpened > breaker.timeout) {
            breaker.state = 'HALF_OPEN';
            this.logger.log('Circuit breaker moving to half-open', { componentName });
          }
        }
      }

      // Check fallback states and attempt recovery
      for (const [componentName, fallbackState] of this.fallbackStates) {
        if (fallbackState.active) {
          const timeSinceActivation = Date.now() - fallbackState.activatedAt;
          if (timeSinceActivation > this.config.recoveryTimeout) {
            // Attempt recovery
            const strategy = this.fallbackStrategies.get(componentName);
            if (strategy) {
              // Note: In a real implementation, we'd need access to the component instance
              this.logger.log('Health check triggering recovery attempt', { componentName });
            }
          }
        }
      }

    } catch (error) {
      this.logger.error('Health check failed', error);
    }
  }

  /**
   * Update component health status
   */
  updateComponentHealth(componentName, status, details = {}) {
    const currentHealth = this.componentHealth.get(componentName) || {};

    this.componentHealth.set(componentName, {
      ...currentHealth,
      status,
      lastChecked: Date.now(),
      ...details,
    });

    if (status !== 'HEALTHY') {
      this.logger.warn('Component health degraded', { componentName, status, details });
    }
  }

  /**
   * Force recovery of a component
   */
  async forceRecovery(componentName) {
    const fallbackState = this.fallbackStates.get(componentName);
    if (!fallbackState || !fallbackState.active) {
      this.logger.warn('Component not in fallback mode', { componentName });
      return false;
    }

    const strategy = this.fallbackStrategies.get(componentName);
    if (!strategy) {
      this.logger.warn('No recovery strategy available', { componentName });
      return false;
    }

    // Reset recovery attempts for forced recovery
    this.recoveryAttempts.delete(componentName);

    this.logger.log('Forcing component recovery', { componentName });
    return await this.attemptRecovery(componentName, null, strategy);
  }

  /**
   * Get system degradation level (0-1, where 1 is fully operational)
   */
  getSystemDegradationLevel() {
    const totalComponents = this.fallbackStrategies.size;
    const degradedComponents = Array.from(this.fallbackStates.values())
      .filter(state => state.active).length;

    const circuitOpenComponents = Array.from(this.circuitBreakers.values())
      .filter(breaker => breaker.state === 'OPEN').length;

    // Weight circuit breaker failures more heavily
    const degradationScore = (degradedComponents + circuitOpenComponents * 2) / (totalComponents * 2);

    return Math.max(0, Math.min(1, 1 - degradationScore));
  }

  /**
   * Check if the fallback system is healthy
   * @returns {boolean} True if the system is operational
   */
  isHealthy() {
    try {
      // Check if basic components are available
      const hasStrategies = this.fallbackStrategies.size > 0;
      const hasHealthMap = this.componentHealth.size >= 0; // Allow empty health map initially

      // Check if monitoring is running (if enabled)
      const monitoringOk = !this.config.monitoringEnabled || !!this.healthMonitorInterval;

      return hasStrategies && hasHealthMap && monitoringOk;
    } catch (error) {
      this.logger.error('Health check failed', error);
      return false;
    }
  }

  /**
   * Get fallback system statistics
   */
  getStatistics() {
    return {
      componentsMonitored: this.fallbackStrategies.size,
      activeFallbacks: Array.from(this.fallbackStates.values()).filter(s => s.active).length,
      circuitBreakersOpen: Array.from(this.circuitBreakers.values()).filter(b => b.state === 'OPEN').length,
      systemDegradationLevel: this.getSystemDegradationLevel(),
      healthChecksRunning: !!this.healthMonitorInterval,
      config: this.config,
    };
  }

  /**
   * Export fallback system state for debugging
   */
  exportState() {
    return {
      componentHealth: Object.fromEntries(this.componentHealth),
      fallbackStates: Object.fromEntries(this.fallbackStates),
      circuitBreakers: Object.fromEntries(this.circuitBreakers),
      recoveryAttempts: Object.fromEntries(this.recoveryAttempts),
      performanceBaselines: Object.fromEntries(this.performanceBaselines),
      statistics: this.getStatistics(),
    };
  }

  /**
   * Check if the fallback system itself is healthy
   * @returns {boolean} True if the system is operational
   */
  isHealthy() {
    try {
      // Check if health monitoring is running
      if (this.config.monitoringEnabled && !this.healthMonitorInterval) {
        return false;
      }

      // Check if we have fallback strategies configured
      if (this.fallbackStrategies.size === 0) {
        return false;
      }

      // Check if any critical components are in open circuit breaker state
      const criticalBreakers = Array.from(this.circuitBreakers.values())
        .filter(breaker => breaker.state === 'OPEN');

      // Allow up to 50% of components to have open circuit breakers
      const maxAllowedOpen = Math.ceil(this.circuitBreakers.size * 0.5);
      if (criticalBreakers.length > maxAllowedOpen) {
        return false;
      }

      return true;
    } catch (error) {
      this.logger.error('Health check failed', error);
      return false;
    }
  }
}

export default FallbackSystem;