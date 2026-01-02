/**
 * MonitoringInfrastructure - Real-time health monitoring and automated diagnostics
 *
 * Provides comprehensive monitoring capabilities for the avatar animation system,
 * including health checks, performance metrics, alerting, and automated diagnostics.
 *
 * Features:
 * - Real-time health monitoring with configurable intervals
 * - Performance metrics collection and alerting
 * - Automated diagnostics and issue detection
 * - Alert management and escalation
 * - Historical data retention and analysis
 * - Integration with external monitoring systems
 */

import { Logger } from '../utils/Logger.js';

export class MonitoringInfrastructure {
  constructor(config = {}) {
    // Initialize logger safely
    try {
      this.logger = new Logger();
    } catch (error) {
      this.logger = {
        log: (...args) => console.log('[MONITOR]', ...args),
        debug: (...args) => console.debug('[MONITOR]', ...args),
        error: (...args) => console.error('[MONITOR]', ...args),
        warn: (...args) => console.warn('[MONITOR]', ...args),
      };
    }

    this.config = {
      healthCheckInterval: config.healthCheckInterval || 30000, // 30 seconds
      performanceCheckInterval: config.performanceCheckInterval || 60000, // 1 minute
      alertCheckInterval: config.alertCheckInterval || 15000, // 15 seconds
      metricsRetentionPeriod: config.metricsRetentionPeriod || 3600000, // 1 hour
      maxMetricsHistory: config.maxMetricsHistory || 1000,
      alertThresholds: {
        cpuUsage: config.alertThresholds?.cpuUsage || 80,
        memoryUsage: config.alertThresholds?.memoryUsage || 85,
        errorRate: config.alertThresholds?.errorRate || 5,
        responseTime: config.alertThresholds?.responseTime || 1000,
        ...config.alertThresholds,
      },
      enableExternalIntegration: config.enableExternalIntegration || false,
      externalEndpoint: config.externalEndpoint,
      ...config,
    };

    // Component health status
    this.componentHealth = new Map();

    // Performance metrics storage
    this.metrics = {
      system: [],
      components: new Map(),
      alerts: [],
    };

    // Active alerts
    this.activeAlerts = new Map();

    // Alert escalation levels
    this.alertLevels = {
      INFO: 1,
      WARNING: 2,
      ERROR: 3,
      CRITICAL: 4,
    };

    // Monitoring intervals
    this.intervals = new Map();

    // Diagnostic results
    this.diagnostics = new Map();

    // External monitoring integration
    this.externalClient = null;

    // Initialize monitoring
    this.initializeMonitoring();

    this.logger.log('MonitoringInfrastructure initialized', {
      features: ['health-monitoring', 'performance-metrics', 'alerting', 'diagnostics'],
      config: this.config,
    });
  }

  /**
   * Initialize monitoring system
   */
  initializeMonitoring() {
    // Start health monitoring
    this.startHealthMonitoring();

    // Start performance monitoring
    this.startPerformanceMonitoring();

    // Start alert monitoring
    this.startAlertMonitoring();

    // Initialize external integration if enabled
    if (this.config.enableExternalIntegration && this.config.externalEndpoint) {
      this.initializeExternalIntegration();
    }
  }

  /**
   * Start health monitoring for all components
   */
  startHealthMonitoring() {
    const interval = setInterval(() => {
      this.performHealthChecks();
    }, this.config.healthCheckInterval);

    this.intervals.set('health', interval);
    this.logger.log('Health monitoring started', { interval: this.config.healthCheckInterval });
  }

  /**
   * Start performance monitoring
   */
  startPerformanceMonitoring() {
    const interval = setInterval(() => {
      this.collectPerformanceMetrics();
    }, this.config.performanceCheckInterval);

    this.intervals.set('performance', interval);
    this.logger.log('Performance monitoring started', { interval: this.config.performanceCheckInterval });
  }

  /**
   * Start alert monitoring and processing
   */
  startAlertMonitoring() {
    const interval = setInterval(() => {
      this.processAlerts();
    }, this.config.alertCheckInterval);

    this.intervals.set('alerts', interval);
    this.logger.log('Alert monitoring started', { interval: this.config.alertCheckInterval });
  }

  /**
   * Perform health checks on all registered components
   */
  async performHealthChecks() {
    const components = [
      'SIMDHelper',
      'PhonemeIntensityMatrix',
      'PhonemeCacheManager',
      'PerformanceMonitor',
      'ValidationFramework',
      'FallbackSystem',
      'ErrorRecovery',
    ];

    for (const componentName of components) {
      try {
        const health = await this.checkComponentHealth(componentName);
        this.updateComponentHealth(componentName, health);

        // Trigger alerts if health is degraded
        if (health.status !== 'HEALTHY') {
          this.triggerHealthAlert(componentName, health);
        }

      } catch (error) {
        this.logger.error('Health check failed', { component: componentName, error: error.message });
        this.updateComponentHealth(componentName, {
          status: 'UNKNOWN',
          timestamp: Date.now(),
          error: error.message,
        });
      }
    }

    this.logger.debug('Health checks completed', { components: components.length });
  }

  /**
   * Check health of a specific component
   */
  async checkComponentHealth(componentName) {
    const health = {
      status: 'UNKNOWN',
      timestamp: Date.now(),
      responseTime: 0,
      memoryUsage: 0,
      errorRate: 0,
      lastError: null,
    };

    const startTime = performance.now();

    try {
      // Import and check component based on name
      switch (componentName) {
        case 'SIMDHelper':
          const { SIMDHelper } = await import('../utils/SIMDHelper.js');
          health.status = SIMDHelper.isSupported() ? 'HEALTHY' : 'DEGRADED';
          health.capabilities = SIMDHelper.getCapabilities();
          break;

        case 'PhonemeIntensityMatrix':
          const { PhonemeIntensityMatrix } = await import('../animation/PhonemeIntensityMatrix.js');
          // Perform a quick calculation test
          const testMatrix = new PhonemeIntensityMatrix();
          await testMatrix.calculateBaseIntensity('test', { x: 0, y: 0, z: 0 });
          health.status = 'HEALTHY';
          break;

        case 'PhonemeCacheManager':
          const { PhonemeCacheManager } = await import('../animation/PhonemeCacheManager.js');
          const cacheManager = new PhonemeCacheManager();
          health.status = cacheManager.isHealthy() ? 'HEALTHY' : 'DEGRADED';
          health.cacheStats = cacheManager.getStats();
          break;

        case 'PerformanceMonitor':
          const { PerformanceMonitor } = await import('../utils/PerformanceMonitor.js');
          const perfMonitor = new PerformanceMonitor();
          health.status = 'HEALTHY';
          health.performanceStats = perfMonitor.getMetrics();
          break;

        case 'ValidationFramework':
          const { ValidationFramework } = await import('../validation/ValidationFramework.js');
          const validator = new ValidationFramework();
          health.status = 'HEALTHY';
          break;

        case 'FallbackSystem':
          const { FallbackSystem } = await import('../fallback/FallbackSystem.js');
          const fallback = new FallbackSystem();
          health.status = fallback.isHealthy() ? 'HEALTHY' : 'DEGRADED';
          break;

        case 'ErrorRecovery':
          const { ErrorRecovery } = await import('../recovery/ErrorRecovery.js');
          const recovery = new ErrorRecovery();
          health.status = 'HEALTHY';
          health.recoveryStats = recovery.getStatistics();
          break;

        default:
          health.status = 'UNKNOWN';
      }

    } catch (error) {
      health.status = 'UNHEALTHY';
      health.lastError = error.message;
      this.logger.warn('Component health check failed', { component: componentName, error: error.message });
    }

    health.responseTime = performance.now() - startTime;

    // Get memory usage if available
    if (performance.memory) {
      health.memoryUsage = performance.memory.usedJSHeapSize / performance.memory.totalJSHeapSize * 100;
    }

    return health;
  }

  /**
   * Update component health status
   */
  updateComponentHealth(componentName, health) {
    this.componentHealth.set(componentName, health);

    // Store in metrics history
    this.storeMetric('component-health', {
      component: componentName,
      ...health,
    });
  }

  /**
   * Collect system and component performance metrics
   */
  collectPerformanceMetrics() {
    const metrics = {
      timestamp: Date.now(),
      system: this.getSystemMetrics(),
      components: {},
    };

    // Collect component-specific metrics
    for (const [componentName, health] of this.componentHealth) {
      metrics.components[componentName] = {
        responseTime: health.responseTime,
        memoryUsage: health.memoryUsage,
        errorRate: health.errorRate,
        status: health.status,
      };
    }

    // Store metrics
    this.storeMetric('performance', metrics);

    // Check for performance alerts
    this.checkPerformanceAlerts(metrics);

    this.logger.debug('Performance metrics collected', {
      components: Object.keys(metrics.components).length,
    });
  }

  /**
   * Get system-level performance metrics
   */
  getSystemMetrics() {
    const metrics = {
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine,
    };

    // Memory information
    if (performance.memory) {
      metrics.memory = {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit,
        usagePercent: (performance.memory.usedJSHeapSize / performance.memory.totalJSHeapSize) * 100,
      };
    }

    // Timing information
    if (performance.timing) {
      metrics.timing = {
        loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
        domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
      };
    }

    // Connection information
    if (navigator.connection) {
      metrics.connection = {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt,
      };
    }

    return metrics;
  }

  /**
   * Store metric in history with retention management
   */
  storeMetric(type, data) {
    const metric = {
      type,
      timestamp: Date.now(),
      data,
    };

    // Store based on type
    if (type === 'performance') {
      this.metrics.system.push(metric);
    } else if (type === 'component-health') {
      if (!this.metrics.components.has(data.component)) {
        this.metrics.components.set(data.component, []);
      }
      this.metrics.components.get(data.component).push(metric);
    } else if (type === 'alert') {
      this.metrics.alerts.push(metric);
    }

    // Clean up old metrics
    this.cleanupOldMetrics();

    // Send to external monitoring if enabled
    if (this.externalClient) {
      this.sendToExternalMonitoring(metric);
    }
  }

  /**
   * Clean up old metrics based on retention policy
   */
  cleanupOldMetrics() {
    const cutoffTime = Date.now() - this.config.metricsRetentionPeriod;

    // Clean system metrics
    this.metrics.system = this.metrics.system.filter(m => m.timestamp > cutoffTime);

    // Clean component metrics
    for (const [component, metrics] of this.metrics.components) {
      this.metrics.components.set(component, metrics.filter(m => m.timestamp > cutoffTime));
    }

    // Clean alerts (keep more history for alerts)
    const alertCutoff = Date.now() - (this.config.metricsRetentionPeriod * 2);
    this.metrics.alerts = this.metrics.alerts.filter(m => m.timestamp > alertCutoff);

    // Enforce max history limits
    if (this.metrics.system.length > this.config.maxMetricsHistory) {
      this.metrics.system = this.metrics.system.slice(-this.config.maxMetricsHistory);
    }

    for (const [component, metrics] of this.metrics.components) {
      if (metrics.length > this.config.maxMetricsHistory) {
        this.metrics.components.set(component, metrics.slice(-this.config.maxMetricsHistory));
      }
    }
  }

  /**
   * Check for performance alerts based on thresholds
   */
  checkPerformanceAlerts(metrics) {
    const thresholds = this.config.alertThresholds;

    // Check memory usage
    if (metrics.system.memory?.usagePercent > thresholds.memoryUsage) {
      this.triggerAlert('HIGH_MEMORY_USAGE', 'WARNING', {
        current: metrics.system.memory.usagePercent,
        threshold: thresholds.memoryUsage,
        component: 'system',
      });
    }

    // Check response times
    for (const [componentName, componentMetrics] of Object.entries(metrics.components)) {
      if (componentMetrics.responseTime > thresholds.responseTime) {
        this.triggerAlert('HIGH_RESPONSE_TIME', 'WARNING', {
          component: componentName,
          current: componentMetrics.responseTime,
          threshold: thresholds.responseTime,
        });
      }
    }

    // Check error rates
    for (const [componentName, componentMetrics] of Object.entries(metrics.components)) {
      if (componentMetrics.errorRate > thresholds.errorRate) {
        this.triggerAlert('HIGH_ERROR_RATE', 'ERROR', {
          component: componentName,
          current: componentMetrics.errorRate,
          threshold: thresholds.errorRate,
        });
      }
    }
  }

  /**
   * Trigger health alert for degraded component
   */
  triggerHealthAlert(componentName, health) {
    const alertType = health.status === 'UNHEALTHY' ? 'COMPONENT_UNHEALTHY' : 'COMPONENT_DEGRADED';
    const severity = health.status === 'UNHEALTHY' ? 'ERROR' : 'WARNING';

    this.triggerAlert(alertType, severity, {
      component: componentName,
      status: health.status,
      lastError: health.lastError,
      responseTime: health.responseTime,
    });
  }

  /**
   * Trigger a new alert
   */
  triggerAlert(type, severity, data) {
    const alert = {
      id: `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      severity,
      level: this.alertLevels[severity] || 1,
      timestamp: Date.now(),
      data,
      status: 'ACTIVE',
      acknowledged: false,
      escalated: false,
    };

    // Check if similar alert already exists
    const existingAlert = this.findSimilarAlert(alert);
    if (existingAlert) {
      this.updateExistingAlert(existingAlert, alert);
      return;
    }

    // Create new alert
    this.activeAlerts.set(alert.id, alert);
    this.storeMetric('alert', alert);

    this.logger.warn('Alert triggered', {
      id: alert.id,
      type: alert.type,
      severity: alert.severity,
      component: alert.data.component,
    });

    // Auto-escalate critical alerts
    if (alert.level >= this.alertLevels.CRITICAL) {
      this.escalateAlert(alert);
    }
  }

  /**
   * Find similar active alert
   */
  findSimilarAlert(newAlert) {
    for (const [id, existingAlert] of this.activeAlerts) {
      if (existingAlert.type === newAlert.type &&
          existingAlert.data.component === newAlert.data.component &&
          existingAlert.status === 'ACTIVE') {
        return existingAlert;
      }
    }
    return null;
  }

  /**
   * Update existing alert with new occurrence
   */
  updateExistingAlert(existingAlert, newAlert) {
    existingAlert.occurrences = (existingAlert.occurrences || 1) + 1;
    existingAlert.lastOccurrence = newAlert.timestamp;
    existingAlert.lastData = newAlert.data;

    // Escalate if too many occurrences
    if (existingAlert.occurrences > 5 && !existingAlert.escalated) {
      this.escalateAlert(existingAlert);
    }

    this.logger.debug('Alert updated', {
      id: existingAlert.id,
      occurrences: existingAlert.occurrences,
    });
  }

  /**
   * Escalate alert to higher severity
   */
  escalateAlert(alert) {
    alert.escalated = true;
    alert.escalationTime = Date.now();

    // Increase severity level
    if (alert.level < this.alertLevels.CRITICAL) {
      alert.level++;
      alert.severity = Object.keys(this.alertLevels)[alert.level - 1];
    }

    this.logger.error('Alert escalated', {
      id: alert.id,
      type: alert.type,
      severity: alert.severity,
      component: alert.data.component,
    });

    // Trigger emergency diagnostics
    this.performEmergencyDiagnostics(alert);
  }

  /**
   * Process active alerts (acknowledgment, resolution, etc.)
   */
  processAlerts() {
    const now = Date.now();
    const alertsToRemove = [];

    for (const [id, alert] of this.activeAlerts) {
      // Auto-resolve alerts after certain time
      const alertAge = now - alert.timestamp;
      const maxAge = alert.level >= this.alertLevels.ERROR ? 300000 : 600000; // 5-10 minutes

      if (alertAge > maxAge && !alert.acknowledged) {
        alert.status = 'AUTO_RESOLVED';
        alert.resolvedAt = now;
        alertsToRemove.push(id);

        this.logger.log('Alert auto-resolved', { id: alert.id, age: alertAge });
      }
    }

    // Remove resolved alerts
    alertsToRemove.forEach(id => this.activeAlerts.delete(id));
  }

  /**
   * Perform emergency diagnostics when alert is escalated
   */
  async performEmergencyDiagnostics(alert) {
    this.logger.log('Performing emergency diagnostics', { alertId: alert.id, type: alert.type });

    const diagnostics = {
      alertId: alert.id,
      timestamp: Date.now(),
      component: alert.data.component,
      findings: [],
      recommendations: [],
    };

    try {
      // Run component-specific diagnostics
      switch (alert.data.component) {
        case 'SIMDHelper':
          diagnostics.findings = await this.diagnoseSIMDIssues();
          break;
        case 'PhonemeIntensityMatrix':
          diagnostics.findings = await this.diagnoseMatrixIssues();
          break;
        case 'PhonemeCacheManager':
          diagnostics.findings = await this.diagnoseCacheIssues();
          break;
        default:
          diagnostics.findings = ['No specific diagnostics available for this component'];
      }

      // Generate recommendations
      diagnostics.recommendations = this.generateRecommendations(diagnostics.findings, alert);

    } catch (error) {
      diagnostics.findings = [`Diagnostic failed: ${error.message}`];
      diagnostics.recommendations = ['Contact system administrator'];
    }

    this.diagnostics.set(alert.id, diagnostics);

    this.logger.log('Emergency diagnostics completed', {
      alertId: alert.id,
      findings: diagnostics.findings.length,
      recommendations: diagnostics.recommendations.length,
    });
  }

  /**
   * Diagnose SIMD-related issues
   */
  async diagnoseSIMDIssues() {
    const findings = [];

    try {
      const { SIMDHelper } = await import('../utils/SIMDHelper.js');

      if (!SIMDHelper.isSupported()) {
        findings.push('SIMD not supported in this environment');
      }

      const capabilities = SIMDHelper.getCapabilities();
      if (!capabilities.simd) {
        findings.push('WebAssembly SIMD not available');
      }

      // Test SIMD operations
      const testResult = SIMDHelper.testSIMDOperations();
      if (!testResult.success) {
        findings.push(`SIMD operations failed: ${testResult.error}`);
      }

    } catch (error) {
      findings.push(`SIMD diagnostic error: ${error.message}`);
    }

    return findings;
  }

  /**
   * Diagnose matrix calculation issues
   */
  async diagnoseMatrixIssues() {
    const findings = [];

    try {
      const { PhonemeIntensityMatrix } = await import('../animation/PhonemeIntensityMatrix.js');
      const matrix = new PhonemeIntensityMatrix();

      // Test basic calculations
      const testResult = await matrix.testCalculations();
      if (!testResult.success) {
        findings.push(`Matrix calculations failed: ${testResult.error}`);
      }

      // Check memory usage
      if (performance.memory) {
        const usagePercent = (performance.memory.usedJSHeapSize / performance.memory.totalJSHeapSize) * 100;
        if (usagePercent > 80) {
          findings.push(`High memory usage: ${usagePercent.toFixed(1)}%`);
        }
      }

    } catch (error) {
      findings.push(`Matrix diagnostic error: ${error.message}`);
    }

    return findings;
  }

  /**
   * Diagnose cache-related issues
   */
  async diagnoseCacheIssues() {
    const findings = [];

    try {
      const { PhonemeCacheManager } = await import('../animation/PhonemeCacheManager.js');
      const cache = new PhonemeCacheManager();

      const stats = cache.getStats();

      if (stats.hitRate < 0.5) {
        findings.push(`Low cache hit rate: ${(stats.hitRate * 100).toFixed(1)}%`);
      }

      if (stats.evictionRate > 0.1) {
        findings.push(`High cache eviction rate: ${(stats.evictionRate * 100).toFixed(1)}%`);
      }

      if (stats.size > stats.maxSize * 0.9) {
        findings.push('Cache near capacity limit');
      }

    } catch (error) {
      findings.push(`Cache diagnostic error: ${error.message}`);
    }

    return findings;
  }

  /**
   * Generate recommendations based on diagnostic findings
   */
  generateRecommendations(findings, alert) {
    const recommendations = [];

    findings.forEach(finding => {
      if (finding.includes('SIMD not supported')) {
        recommendations.push('Enable WebAssembly SIMD support in browser');
        recommendations.push('Consider fallback to JavaScript implementations');
      }

      if (finding.includes('memory usage')) {
        recommendations.push('Reduce cache size or implement memory cleanup');
        recommendations.push('Monitor for memory leaks in animation calculations');
      }

      if (finding.includes('cache hit rate')) {
        recommendations.push('Optimize cache key generation');
        recommendations.push('Increase cache size if memory allows');
      }

      if (finding.includes('timeout') || finding.includes('response time')) {
        recommendations.push('Optimize calculation algorithms');
        recommendations.push('Consider pre-computing intensive operations');
      }
    });

    // Default recommendations
    if (recommendations.length === 0) {
      recommendations.push('Monitor system resources and logs');
      recommendations.push('Consider restarting the application');
      recommendations.push('Contact system administrator if issue persists');
    }

    return recommendations;
  }

  /**
   * Initialize external monitoring integration
   */
  initializeExternalIntegration() {
    // Placeholder for external monitoring integration
    // This could integrate with services like DataDog, New Relic, etc.
    this.externalClient = {
      send: (metric) => {
        // Send to external service
        this.logger.debug('Sending metric to external monitoring', { type: metric.type });
      },
    };

    this.logger.log('External monitoring integration initialized', { endpoint: this.config.externalEndpoint });
  }

  /**
   * Send metric to external monitoring system
   */
  sendToExternalMonitoring(metric) {
    if (this.externalClient) {
      try {
        this.externalClient.send(metric);
      } catch (error) {
        this.logger.error('Failed to send metric to external monitoring', error);
      }
    }
  }

  /**
   * Acknowledge alert
   */
  acknowledgeAlert(alertId) {
    const alert = this.activeAlerts.get(alertId);
    if (alert) {
      alert.acknowledged = true;
      alert.acknowledgedAt = Date.now();
      this.logger.log('Alert acknowledged', { id: alertId });
      return true;
    }
    return false;
  }

  /**
   * Resolve alert manually
   */
  resolveAlert(alertId) {
    const alert = this.activeAlerts.get(alertId);
    if (alert) {
      alert.status = 'RESOLVED';
      alert.resolvedAt = Date.now();
      this.activeAlerts.delete(alertId);
      this.logger.log('Alert resolved', { id: alertId });
      return true;
    }
    return false;
  }

  /**
   * Get current health status of all components
   */
  getHealthStatus() {
    const status = {};

    for (const [componentName, health] of this.componentHealth) {
      status[componentName] = {
        status: health.status,
        timestamp: health.timestamp,
        responseTime: health.responseTime,
        lastError: health.lastError,
        uptime: this.calculateUptime(componentName),
      };
    }

    return status;
  }

  /**
   * Calculate component uptime percentage
   */
  calculateUptime(componentName) {
    const componentMetrics = this.metrics.components.get(componentName) || [];
    if (componentMetrics.length === 0) return 100;

    const totalChecks = componentMetrics.length;
    const healthyChecks = componentMetrics.filter(m => m.data.status === 'HEALTHY').length;

    return (healthyChecks / totalChecks) * 100;
  }

  /**
   * Get performance metrics summary
   */
  getPerformanceSummary(timeRange = 3600000) { // 1 hour default
    const cutoffTime = Date.now() - timeRange;
    const recentMetrics = this.metrics.system.filter(m => m.timestamp > cutoffTime);

    if (recentMetrics.length === 0) {
      return { message: 'No recent metrics available' };
    }

    const summary = {
      timeRange,
      totalMetrics: recentMetrics.length,
      averageMemoryUsage: 0,
      peakMemoryUsage: 0,
      averageResponseTime: {},
      errorRates: {},
    };

    let totalMemoryUsage = 0;
    let peakMemory = 0;
    const responseTimes = {};
    const errorCounts = {};

    recentMetrics.forEach(metric => {
      // Memory usage
      if (metric.data.system.memory) {
        const memUsage = metric.data.system.memory.usagePercent;
        totalMemoryUsage += memUsage;
        peakMemory = Math.max(peakMemory, memUsage);
      }

      // Component response times and errors
      Object.entries(metric.data.components).forEach(([component, compData]) => {
        if (!responseTimes[component]) responseTimes[component] = [];
        if (!errorCounts[component]) errorCounts[component] = 0;

        responseTimes[component].push(compData.responseTime);
        if (compData.errorRate > 0) errorCounts[component]++;
      });
    });

    summary.averageMemoryUsage = totalMemoryUsage / recentMetrics.length;
    summary.peakMemoryUsage = peakMemory;

    // Calculate average response times
    Object.entries(responseTimes).forEach(([component, times]) => {
      summary.averageResponseTime[component] = times.reduce((a, b) => a + b, 0) / times.length;
    });

    // Calculate error rates
    Object.entries(errorCounts).forEach(([component, errors]) => {
      summary.errorRates[component] = (errors / recentMetrics.length) * 100;
    });

    return summary;
  }

  /**
   * Get active alerts
   */
  getActiveAlerts() {
    return Array.from(this.activeAlerts.values()).map(alert => ({
      id: alert.id,
      type: alert.type,
      severity: alert.severity,
      level: alert.level,
      timestamp: alert.timestamp,
      data: alert.data,
      occurrences: alert.occurrences || 1,
      escalated: alert.escalated,
      acknowledged: alert.acknowledged,
    }));
  }

  /**
   * Get diagnostic results for an alert
   */
  getDiagnostics(alertId) {
    return this.diagnostics.get(alertId) || null;
  }

  /**
   * Export monitoring data for analysis
   */
  exportMonitoringData() {
    return {
      healthStatus: this.getHealthStatus(),
      performanceSummary: this.getPerformanceSummary(),
      activeAlerts: this.getActiveAlerts(),
      metricsHistory: {
        system: this.metrics.system.length,
        components: Object.fromEntries(
          Array.from(this.metrics.components.entries()).map(([k, v]) => [k, v.length])
        ),
        alerts: this.metrics.alerts.length,
      },
      diagnostics: Object.fromEntries(this.diagnostics.entries()),
      config: this.config,
    };
  }

  /**
   * Reset monitoring state
   */
  reset() {
    this.componentHealth.clear();
    this.activeAlerts.clear();
    this.diagnostics.clear();

    // Clear metrics but keep structure
    this.metrics.system = [];
    this.metrics.components.clear();
    this.metrics.alerts = [];

    this.logger.log('Monitoring infrastructure reset');
  }

  /**
   * Stop all monitoring
   */
  stop() {
    // Clear all intervals
    for (const [name, interval] of this.intervals) {
      clearInterval(interval);
      this.logger.log(`Stopped ${name} monitoring`);
    }
    this.intervals.clear();

    this.logger.log('Monitoring infrastructure stopped');
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.stop();
    this.reset();

    if (this.externalClient) {
      // Cleanup external integration
      this.externalClient = null;
    }

    this.logger.log('MonitoringInfrastructure destroyed');
  }
}

export default MonitoringInfrastructure;
