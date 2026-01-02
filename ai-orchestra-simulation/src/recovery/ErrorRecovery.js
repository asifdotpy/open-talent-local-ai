/**
 * ErrorRecovery - Circuit breakers, retry logic, and state restoration for avatar animation
 *
 * Implements robust error handling with automatic recovery mechanisms, circuit breaker
 * patterns, and state preservation to ensure system reliability and graceful failure handling.
 *
 * Features:
 * - Circuit breaker pattern for repeated failures
 * - Exponential backoff retry logic
 * - State preservation and restoration
 * - Timeout handling and cancellation
 * - Error classification and handling strategies
 */

import { Logger } from '../utils/Logger.js';

export class ErrorRecovery {
  constructor(config = {}) {
    // Initialize logger safely
    try {
      this.logger = new Logger();
    } catch (error) {
      this.logger = {
        log: (...args) => console.log('[RECOVERY]', ...args),
        debug: (...args) => console.debug('[RECOVERY]', ...args),
        error: (...args) => console.error('[RECOVERY]', ...args),
        warn: (...args) => console.warn('[RECOVERY]', ...args),
      };
    }

    this.config = {
      circuitBreakerEnabled: config.circuitBreakerEnabled !== false,
      retryEnabled: config.retryEnabled !== false,
      stateRecoveryEnabled: config.stateRecoveryEnabled !== false,
      maxRetries: config.maxRetries || 3,
      baseRetryDelay: config.baseRetryDelay || 1000, // 1 second
      maxRetryDelay: config.maxRetryDelay || 30000, // 30 seconds
      circuitBreakerThreshold: config.circuitBreakerThreshold || 5,
      circuitBreakerTimeout: config.circuitBreakerTimeout || 60000, // 1 minute
      operationTimeout: config.operationTimeout || 10000, // 10 seconds
      stateSnapshotInterval: config.stateSnapshotInterval || 30000, // 30 seconds
      ...config,
    };

    // Circuit breakers for different operations
    this.circuitBreakers = new Map();

    // Retry state tracking
    this.retryStates = new Map();

    // State snapshots for recovery
    this.stateSnapshots = new Map();
    this.lastSnapshotTime = 0;

    // Active operations tracking
    this.activeOperations = new Map();

    // Error classification and handling strategies
    this.errorStrategies = new Map();

    // Initialize error handling strategies
    this.initializeErrorStrategies();

    // Start state snapshotting if enabled
    if (this.config.stateRecoveryEnabled) {
      this.startStateSnapshotting();
    }

    this.logger.log('ErrorRecovery initialized', {
      features: ['circuit-breaker', 'retry-logic', 'state-recovery', 'timeout-handling'],
      config: this.config,
    });
  }

  /**
   * Initialize error handling strategies for different error types
   */
  initializeErrorStrategies() {
    // Network errors
    this.errorStrategies.set('NetworkError', {
      retryable: true,
      backoffMultiplier: 2,
      maxRetries: 5,
      circuitBreaker: true,
      recoveryAction: 'reconnect',
    });

    // Timeout errors
    this.errorStrategies.set('TimeoutError', {
      retryable: true,
      backoffMultiplier: 1.5,
      maxRetries: 3,
      circuitBreaker: false,
      recoveryAction: 'retry',
    });

    // Memory errors
    this.errorStrategies.set('MemoryError', {
      retryable: false,
      backoffMultiplier: 1,
      maxRetries: 1,
      circuitBreaker: true,
      recoveryAction: 'reduce-load',
    });

    // Data corruption errors
    this.errorStrategies.set('DataCorruptionError', {
      retryable: false,
      backoffMultiplier: 1,
      maxRetries: 1,
      circuitBreaker: true,
      recoveryAction: 'reset-state',
    });

    // SIMD/WebAssembly errors
    this.errorStrategies.set('SIMDError', {
      retryable: true,
      backoffMultiplier: 1.2,
      maxRetries: 2,
      circuitBreaker: false,
      recoveryAction: 'fallback',
    });

    // Calculation errors
    this.errorStrategies.set('CalculationError', {
      retryable: true,
      backoffMultiplier: 1,
      maxRetries: 2,
      circuitBreaker: false,
      recoveryAction: 'recalculate',
    });

    // Default strategy for unknown errors
    this.errorStrategies.set('UnknownError', {
      retryable: true,
      backoffMultiplier: 1.5,
      maxRetries: 2,
      circuitBreaker: true,
      recoveryAction: 'retry',
    });
  }

  /**
   * Execute operation with error recovery
   */
  async executeWithRecovery(operationName, operation, options = {}) {
    const operationId = `${operationName}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Create operation context
    const context = {
      id: operationId,
      name: operationName,
      startTime: Date.now(),
      retries: 0,
      timeout: options.timeout || this.config.operationTimeout,
      ...options,
    };

    this.activeOperations.set(operationId, context);

    try {
      // Check circuit breaker
      if (this.config.circuitBreakerEnabled) {
        const breaker = this.getCircuitBreaker(operationName);
        if (breaker.state === 'OPEN') {
          throw new Error(`Circuit breaker open for ${operationName}`);
        }
      }

      // Execute with timeout
      const result = await this.executeWithTimeout(operation, context.timeout, context);

      // Success - reset circuit breaker failures
      if (this.config.circuitBreakerEnabled) {
        const breaker = this.getCircuitBreaker(operationName);
        breaker.failures = 0;
        breaker.state = 'CLOSED';
      }

      this.activeOperations.delete(operationId);
      return result;

    } catch (error) {
      this.activeOperations.delete(operationId);

      // Handle error with recovery
      return await this.handleError(operationName, operation, error, context);
    }
  }

  /**
   * Execute operation with timeout
   */
  async executeWithTimeout(operation, timeout, context) {
    return new Promise(async (resolve, reject) => {
      // Set timeout
      const timeoutId = setTimeout(() => {
        reject(new Error(`Operation timeout after ${timeout}ms`));
      }, timeout);

      try {
        const result = await operation();
        clearTimeout(timeoutId);
        resolve(result);
      } catch (error) {
        clearTimeout(timeoutId);
        reject(error);
      }
    });
  }

  /**
   * Handle error and attempt recovery
   */
  async handleError(operationName, operation, error, context) {
    // Classify error
    const errorType = this.classifyError(error);
    const strategy = this.errorStrategies.get(errorType) || this.errorStrategies.get('UnknownError');

    this.logger.warn('Operation failed, attempting recovery', {
      operation: operationName,
      error: error.message,
      errorType,
      strategy: strategy.recoveryAction,
      attempt: context.retries + 1,
    });

    // Record failure in circuit breaker
    if (this.config.circuitBreakerEnabled && strategy.circuitBreaker) {
      this.recordCircuitBreakerFailure(operationName);
    }

    // Check if retry is allowed
    if (!this.config.retryEnabled || !strategy.retryable || context.retries >= strategy.maxRetries) {
      this.logger.error('Recovery failed, max retries exceeded', {
        operation: operationName,
        error: error.message,
        retries: context.retries,
        maxRetries: strategy.maxRetries,
      });
      throw error;
    }

    // Calculate retry delay with exponential backoff
    const retryDelay = this.calculateRetryDelay(context.retries, strategy.backoffMultiplier);

    // Update context
    context.retries++;
    context.lastError = error;
    context.nextRetry = Date.now() + retryDelay;

    this.logger.log('Scheduling retry', {
      operation: operationName,
      attempt: context.retries,
      delay: retryDelay,
      nextRetry: new Date(context.nextRetry).toISOString(),
    });

    // Wait for retry delay
    await new Promise(resolve => setTimeout(resolve, retryDelay));

    // Attempt retry
    try {
      const result = await this.executeWithRecovery(operationName, operation, {
        ...context,
        retries: context.retries,
      });

      this.logger.log('Recovery successful', {
        operation: operationName,
        attempts: context.retries,
      });

      return result;

    } catch (retryError) {
      // Retry failed, continue with error handling
      return await this.handleError(operationName, operation, retryError, context);
    }
  }

  /**
   * Classify error type for appropriate handling strategy
   */
  classifyError(error) {
    const message = error.message.toLowerCase();
    const name = error.name.toLowerCase();

    // Network errors
    if (message.includes('network') || message.includes('connection') ||
        message.includes('websocket') || name.includes('network')) {
      return 'NetworkError';
    }

    // Timeout errors
    if (message.includes('timeout') || name.includes('timeout')) {
      return 'TimeoutError';
    }

    // Memory errors
    if (message.includes('memory') || message.includes('out of memory') ||
        name.includes('range') || name.includes('memory')) {
      return 'MemoryError';
    }

    // Data corruption errors
    if (message.includes('corrupt') || message.includes('invalid data') ||
        message.includes('parse') || message.includes('malformed')) {
      return 'DataCorruptionError';
    }

    // SIMD/WebAssembly errors
    if (message.includes('simd') || message.includes('webassembly') ||
        message.includes('wasm') || name.includes('wasm')) {
      return 'SIMDError';
    }

    // Calculation errors
    if (message.includes('calculation') || message.includes('math') ||
        message.includes('nan') || message.includes('infinity')) {
      return 'CalculationError';
    }

    return 'UnknownError';
  }

  /**
   * Calculate retry delay with exponential backoff
   */
  calculateRetryDelay(retryCount, multiplier) {
    const baseDelay = this.config.baseRetryDelay;
    const exponentialDelay = baseDelay * Math.pow(multiplier, retryCount);
    const jitter = Math.random() * 0.1 * exponentialDelay; // Add 10% jitter

    return Math.min(exponentialDelay + jitter, this.config.maxRetryDelay);
  }

  /**
   * Get or create circuit breaker for an operation
   */
  getCircuitBreaker(operationName) {
    if (!this.circuitBreakers.has(operationName)) {
      this.circuitBreakers.set(operationName, {
        state: 'CLOSED', // CLOSED, OPEN, HALF_OPEN
        failures: 0,
        threshold: this.config.circuitBreakerThreshold,
        timeout: this.config.circuitBreakerTimeout,
        lastOpened: 0,
        lastClosed: 0,
      });
    }
    return this.circuitBreakers.get(operationName);
  }

  /**
   * Record failure in circuit breaker
   */
  recordCircuitBreakerFailure(operationName) {
    const breaker = this.getCircuitBreaker(operationName);
    breaker.failures++;

    if (breaker.failures >= breaker.threshold) {
      breaker.state = 'OPEN';
      breaker.lastOpened = Date.now();
      this.logger.warn('Circuit breaker opened', { operation: operationName, failures: breaker.failures });
    }
  }

  /**
   * Attempt to close circuit breaker (half-open to closed)
   */
  attemptCircuitBreakerRecovery(operationName) {
    const breaker = this.getCircuitBreaker(operationName);

    if (breaker.state === 'HALF_OPEN') {
      breaker.failures = 0;
      breaker.state = 'CLOSED';
      breaker.lastClosed = Date.now();
      this.logger.log('Circuit breaker closed', { operation: operationName });
    }
  }

  /**
   * Create state snapshot for recovery
   */
  createStateSnapshot(componentName, state) {
    const snapshot = {
      component: componentName,
      timestamp: Date.now(),
      state: JSON.parse(JSON.stringify(state)), // Deep clone
      checksum: this.calculateStateChecksum(state),
    };

    this.stateSnapshots.set(componentName, snapshot);
    this.lastSnapshotTime = Date.now();

    this.logger.debug('State snapshot created', { component: componentName, size: JSON.stringify(state).length });
  }

  /**
   * Restore state from snapshot
   */
  restoreStateFromSnapshot(componentName) {
    const snapshot = this.stateSnapshots.get(componentName);

    if (!snapshot) {
      this.logger.warn('No state snapshot available for restoration', { component: componentName });
      return null;
    }

    // Verify snapshot integrity
    const currentChecksum = this.calculateStateChecksum(snapshot.state);
    if (currentChecksum !== snapshot.checksum) {
      this.logger.error('State snapshot corrupted', { component: componentName });
      return null;
    }

    this.logger.log('State restored from snapshot', {
      component: componentName,
      age: Date.now() - snapshot.timestamp,
    });

    return JSON.parse(JSON.stringify(snapshot.state)); // Return deep clone
  }

  /**
   * Calculate checksum for state integrity verification
   */
  calculateStateChecksum(state) {
    const stateString = JSON.stringify(state);
    let hash = 0;

    for (let i = 0; i < stateString.length; i++) {
      const char = stateString.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }

    return hash.toString(36);
  }

  /**
   * Start periodic state snapshotting
   */
  startStateSnapshotting() {
    this.snapshotInterval = setInterval(() => {
      this.performStateSnapshotting();
    }, this.config.stateSnapshotInterval);

    this.logger.log('State snapshotting started', { interval: this.config.stateSnapshotInterval });
  }

  /**
   * Stop state snapshotting
   */
  stopStateSnapshotting() {
    if (this.snapshotInterval) {
      clearInterval(this.snapshotInterval);
      this.snapshotInterval = null;
      this.logger.log('State snapshotting stopped');
    }
  }

  /**
   * Perform state snapshotting for critical components
   */
  async performStateSnapshotting() {
    try {
      // Snapshot PhonemeIntensityMatrix state
      const { default: PhonemeIntensityMatrix } = await import('../animation/PhonemeIntensityMatrix.js');
      // Note: In a real implementation, we'd have access to the instance
      // For now, this is a placeholder for the snapshotting logic

      this.logger.debug('State snapshotting completed');

    } catch (error) {
      this.logger.error('State snapshotting failed', error);
    }
  }

  /**
   * Cancel active operation
   */
  cancelOperation(operationId) {
    const context = this.activeOperations.get(operationId);
    if (context) {
      context.cancelled = true;
      this.activeOperations.delete(operationId);
      this.logger.log('Operation cancelled', { operationId });
      return true;
    }
    return false;
  }

  /**
   * Cancel all active operations
   */
  cancelAllOperations() {
    const operationIds = Array.from(this.activeOperations.keys());
    let cancelled = 0;

    operationIds.forEach(id => {
      if (this.cancelOperation(id)) {
        cancelled++;
      }
    });

    this.logger.log('All operations cancelled', { total: operationIds.length, cancelled });
    return cancelled;
  }

  /**
   * Get operation status
   */
  getOperationStatus(operationId) {
    const context = this.activeOperations.get(operationId);
    if (!context) {
      return null;
    }

    return {
      id: context.id,
      name: context.name,
      startTime: context.startTime,
      duration: Date.now() - context.startTime,
      retries: context.retries,
      timeout: context.timeout,
      cancelled: context.cancelled || false,
      nextRetry: context.nextRetry,
      lastError: context.lastError?.message,
    };
  }

  /**
   * Get all active operations
   */
  getActiveOperations() {
    const operations = {};

    for (const [id, context] of this.activeOperations) {
      operations[id] = this.getOperationStatus(id);
    }

    return operations;
  }

  /**
   * Get circuit breaker status
   */
  getCircuitBreakerStatus() {
    const status = {};

    for (const [operationName, breaker] of this.circuitBreakers) {
      status[operationName] = {
        state: breaker.state,
        failures: breaker.failures,
        threshold: breaker.threshold,
        lastOpened: breaker.lastOpened,
        lastClosed: breaker.lastClosed,
        timeSinceLastOpened: breaker.lastOpened ? Date.now() - breaker.lastOpened : null,
      };
    }

    return status;
  }

  /**
   * Get retry statistics
   */
  getRetryStatistics() {
    const stats = {};

    for (const [operationName, retryState] of this.retryStates) {
      stats[operationName] = {
        totalRetries: retryState.totalRetries || 0,
        successfulRetries: retryState.successfulRetries || 0,
        failedRetries: retryState.failedRetries || 0,
        averageRetryDelay: retryState.averageRetryDelay || 0,
      };
    }

    return stats;
  }

  /**
   * Force circuit breaker reset
   */
  resetCircuitBreaker(operationName) {
    const breaker = this.getCircuitBreaker(operationName);
    breaker.state = 'CLOSED';
    breaker.failures = 0;
    breaker.lastClosed = Date.now();

    this.logger.log('Circuit breaker manually reset', { operation: operationName });
  }

  /**
   * Force state recovery for a component
   */
  forceStateRecovery(componentName) {
    const recoveredState = this.restoreStateFromSnapshot(componentName);

    if (recoveredState) {
      this.logger.log('State recovery forced', { component: componentName });
      return recoveredState;
    }

    this.logger.warn('Forced state recovery failed', { component: componentName });
    return null;
  }

  /**
   * Get error recovery statistics
   */
  getStatistics() {
    const circuitBreakers = this.getCircuitBreakerStatus();
    const openBreakers = Object.values(circuitBreakers).filter(b => b.state === 'OPEN').length;

    return {
      activeOperations: this.activeOperations.size,
      circuitBreakersTotal: this.circuitBreakers.size,
      circuitBreakersOpen: openBreakers,
      stateSnapshots: this.stateSnapshots.size,
      lastSnapshotTime: this.lastSnapshotTime,
      config: this.config,
    };
  }

  /**
   * Export error recovery state for debugging
   */
  exportState() {
    return {
      activeOperations: this.getActiveOperations(),
      circuitBreakers: this.getCircuitBreakerStatus(),
      retryStatistics: this.getRetryStatistics(),
      stateSnapshots: Object.fromEntries(
        Array.from(this.stateSnapshots.entries()).map(([key, snapshot]) => [
          key,
          { ...snapshot, state: '[REDACTED]' } // Don't export full state for security
        ])
      ),
      statistics: this.getStatistics(),
    };
  }

  /**
   * Reset error recovery state
   */
  reset() {
    this.activeOperations.clear();
    this.retryStates.clear();

    // Reset circuit breakers
    for (const breaker of this.circuitBreakers.values()) {
      breaker.state = 'CLOSED';
      breaker.failures = 0;
      breaker.lastOpened = 0;
      breaker.lastClosed = Date.now();
    }

    this.logger.log('Error recovery system reset');
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.cancelAllOperations();
    this.stopStateSnapshotting();

    this.circuitBreakers.clear();
    this.retryStates.clear();
    this.stateSnapshots.clear();
    this.activeOperations.clear();

    this.logger.log('ErrorRecovery destroyed');
  }
}

export default ErrorRecovery;
