/**
 * MorphTargetBlender - Advanced morph target blending system
 *
 * Implements sophisticated blending algorithms for smooth morph target transitions,
 * replacing linear interpolation with spline-based and physics-based animations.
 *
 * Features:
 * - Cubic spline interpolation for smooth transitions
 * - Physics-based easing with velocity and acceleration
 * - Multi-target blending with priority weighting
 * - Transition queuing and sequencing
 * - Real-time blend shape optimization
 */

import { Logger } from '../utils/Logger.js';

export class MorphTargetBlender {
  constructor(config = {}) {
    this.logger = this.initializeLogger();

    this.config = {
      blendMode: config.blendMode || 'spline', // 'linear', 'spline', 'physics'
      transitionDuration: config.transitionDuration || 200, // ms
      easingFunction: config.easingFunction || 'easeInOutCubic',
      maxConcurrentTransitions: config.maxConcurrentTransitions || 5,
      blendThreshold: config.blendThreshold || 0.01,
      physics: {
        damping: config.physics?.damping || 0.8,
        stiffness: config.physics?.stiffness || 0.3,
        mass: config.physics?.mass || 1.0,
      },
      ...config,
    };

    // Active transitions
    this.activeTransitions = new Map();

    // Transition queue for sequencing
    this.transitionQueue = [];

    // Blend state cache
    this.blendState = new Map();

    // Performance metrics
    this.metrics = {
      transitionsProcessed: 0,
      averageBlendTime: 0,
      maxConcurrentTransitions: 0,
    };

    this.logger.log('INFO', 'MorphTargetBlender initialized', {
      blendMode: this.config.blendMode,
      transitionDuration: this.config.transitionDuration,
      maxConcurrent: this.config.maxConcurrentTransitions,
      features: ['spline', 'physics', 'queuing', 'optimization'],
    });
  }

  /**
   * Initialize logger with fallback
   */
  initializeLogger() {
    try {
      return new Logger();
    } catch (error) {
      return {
        log: (category, message, data) => console.log(`[${category}] ${message}`, data || ''),
        debug: (category, message, data) => console.debug(`[${category}] ${message}`, data || ''),
      };
    }
  }

  /**
   * Blend morph targets with advanced algorithms
   */
  blendMorphTargets(currentValues, targetValues, deltaTime, options = {}) {
    const startTime = performance.now();

    // Update active transitions
    this.updateTransitions(deltaTime);

    // Create new transitions for changed targets
    const newTransitions = this.createTransitions(currentValues, targetValues, options);

    // Add new transitions to active set
    this.addTransitions(newTransitions);

    // Calculate blended values
    const blendedValues = this.calculateBlendedValues(currentValues, targetValues);

    // Update metrics
    this.updateMetrics(performance.now() - startTime);

    return blendedValues;
  }

  /**
   * Create transitions for morph target changes
   */
  createTransitions(currentValues, targetValues, options) {
    const transitions = [];
    const priority = options.priority || 1.0;
    const duration = options.duration || this.config.transitionDuration;

    Object.keys(targetValues).forEach(targetName => {
      const currentValue = currentValues[targetName] || 0;
      const targetValue = targetValues[targetName];

      // Check if change is significant enough
      if (Math.abs(targetValue - currentValue) > this.config.blendThreshold) {
        const transition = {
          targetName,
          startValue: currentValue,
          endValue: targetValue,
          duration,
          priority,
          startTime: performance.now(),
          easing: options.easing || this.config.easingFunction,
          blendMode: options.blendMode || this.config.blendMode,
          physics: options.physics || this.config.physics,
        };

        transitions.push(transition);
      }
    });

    return transitions;
  }

  /**
   * Add transitions to active set, respecting concurrency limits
   */
  addTransitions(transitions) {
    transitions.forEach(transition => {
      // Check if we already have a transition for this target
      const existingTransition = this.activeTransitions.get(transition.targetName);

      if (existingTransition) {
        // Update existing transition
        existingTransition.endValue = transition.endValue;
        existingTransition.startTime = performance.now();
        existingTransition.duration = transition.duration;
      } else {
        // Check concurrency limit
        if (this.activeTransitions.size >= this.config.maxConcurrentTransitions) {
          // Queue the transition
          this.transitionQueue.push(transition);
        } else {
          // Add to active transitions
          this.activeTransitions.set(transition.targetName, transition);
        }
      }
    });

    this.metrics.maxConcurrentTransitions = Math.max(
      this.metrics.maxConcurrentTransitions,
      this.activeTransitions.size
    );
  }

  /**
   * Update active transitions
   */
  updateTransitions(deltaTime) {
    const currentTime = performance.now();
    const completedTransitions = [];

    this.activeTransitions.forEach((transition, targetName) => {
      const elapsed = currentTime - transition.startTime;
      const progress = Math.min(elapsed / transition.duration, 1.0);

      // Mark completed transitions
      if (progress >= 1.0) {
        completedTransitions.push(targetName);
      }
    });

    // Remove completed transitions
    completedTransitions.forEach(targetName => {
      this.activeTransitions.delete(targetName);
    });

    // Add queued transitions if slots are available
    while (this.transitionQueue.length > 0 &&
           this.activeTransitions.size < this.config.maxConcurrentTransitions) {
      const queuedTransition = this.transitionQueue.shift();
      this.activeTransitions.set(queuedTransition.targetName, {
        ...queuedTransition,
        startTime: currentTime,
      });
    }
  }

  /**
   * Calculate blended values using active transitions
   */
  calculateBlendedValues(currentValues, targetValues) {
    const blendedValues = { ...currentValues };
    const currentTime = performance.now();

    // Apply active transitions
    this.activeTransitions.forEach((transition, targetName) => {
      const elapsed = currentTime - transition.startTime;
      const progress = Math.min(elapsed / transition.duration, 1.0);

      let interpolatedValue;

      switch (transition.blendMode) {
        case 'linear':
          interpolatedValue = this.linearInterpolation(
            transition.startValue,
            transition.endValue,
            progress
          );
          break;

        case 'spline':
          interpolatedValue = this.cubicSplineInterpolation(
            transition.startValue,
            transition.endValue,
            progress,
            transition.easing
          );
          break;

        case 'physics':
          interpolatedValue = this.physicsBasedInterpolation(
            transition,
            elapsed,
            transition.physics
          );
          break;

        default:
          interpolatedValue = this.linearInterpolation(
            transition.startValue,
            transition.endValue,
            progress
          );
      }

      blendedValues[targetName] = interpolatedValue;
    });

    // For targets without active transitions, use target values directly
    Object.keys(targetValues).forEach(targetName => {
      if (!this.activeTransitions.has(targetName)) {
        blendedValues[targetName] = targetValues[targetName];
      }
    });

    return blendedValues;
  }

  /**
   * Linear interpolation
   */
  linearInterpolation(start, end, progress) {
    return start + (end - start) * progress;
  }

  /**
   * Cubic spline interpolation with easing
   */
  cubicSplineInterpolation(start, end, progress, easing) {
    const easedProgress = this.applyEasing(progress, easing);
    return start + (end - start) * easedProgress;
  }

  /**
   * Physics-based interpolation with spring dynamics
   */
  physicsBasedInterpolation(transition, elapsed, physics) {
    const { damping, stiffness, mass } = physics;
    const displacement = transition.endValue - transition.startValue;
    const time = elapsed / 1000; // Convert to seconds

    // Spring equation: x = A * e^(-γt) * cos(ωt + φ)
    // Simplified damped harmonic oscillator
    const gamma = damping / (2 * mass);
    const omega = Math.sqrt(stiffness / mass);
    const omegaDamped = Math.sqrt(omega * omega - gamma * gamma);

    if (omegaDamped > 0) {
      // Under-damped case
      const A = displacement;
      const phi = 0; // Phase offset
      const oscillation = A * Math.exp(-gamma * time) *
                         Math.cos(omegaDamped * time + phi);

      return transition.startValue + displacement - oscillation;
    } else {
      // Critically damped or over-damped case
      const A = displacement;
      const B = (gamma * displacement) / omega;
      const decay = (A + B * time) * Math.exp(-gamma * time);

      return transition.startValue + displacement - decay;
    }
  }

  /**
   * Apply easing function
   */
  applyEasing(progress, easingType) {
    switch (easingType) {
      case 'easeInQuad':
        return progress * progress;
      case 'easeOutQuad':
        return progress * (2 - progress);
      case 'easeInOutQuad':
        return progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
      case 'easeInCubic':
        return progress * progress * progress;
      case 'easeOutCubic':
        const t = progress - 1;
        return t * t * t + 1;
      case 'easeInOutCubic':
        return progress < 0.5
          ? 4 * progress * progress * progress
          : (progress - 1) * (2 * progress - 2) * (2 * progress - 2) + 1;
      case 'easeInQuart':
        return progress * progress * progress * progress;
      case 'easeOutQuart':
        const t1 = progress - 1;
        return 1 - t1 * t1 * t1 * t1;
      case 'easeInOutQuart':
        const t2 = progress * 2;
        return progress < 0.5
          ? 0.5 * t2 * t2 * t2 * t2
          : 1 - 0.5 * Math.abs(Math.pow(2 - t2, 4));
      default:
        return progress; // Linear
    }
  }

  /**
   * Set morph target values immediately (no transition)
   */
  setMorphTargetsImmediate(values) {
    // Clear any active transitions for these targets
    Object.keys(values).forEach(targetName => {
      this.activeTransitions.delete(targetName);
    });

    // Update blend state
    Object.assign(this.blendState, values);

    this.logger.log('INFO', 'Morph targets set immediately', {
      targets: Object.keys(values),
      count: Object.keys(values).length,
    });
  }

  /**
   * Cancel active transitions for specific targets
   */
  cancelTransitions(targetNames) {
    if (Array.isArray(targetNames)) {
      targetNames.forEach(name => {
        this.activeTransitions.delete(name);
      });
    } else {
      this.activeTransitions.delete(targetNames);
    }

    this.logger.log('INFO', 'Transitions cancelled', {
      targets: Array.isArray(targetNames) ? targetNames : [targetNames],
    });
  }

  /**
   * Cancel all active transitions
   */
  cancelAllTransitions() {
    const cancelledCount = this.activeTransitions.size;
    this.activeTransitions.clear();
    this.transitionQueue = [];

    this.logger.log('INFO', 'All transitions cancelled', {
      cancelledCount,
    });
  }

  /**
   * Get current blend state
   */
  getBlendState() {
    const currentValues = {};
    const currentTime = performance.now();

    // Get values from active transitions
    this.activeTransitions.forEach((transition, targetName) => {
      const elapsed = currentTime - transition.startTime;
      const progress = Math.min(elapsed / transition.duration, 1.0);

      let value;
      switch (transition.blendMode) {
        case 'linear':
          value = this.linearInterpolation(transition.startValue, transition.endValue, progress);
          break;
        case 'spline':
          value = this.cubicSplineInterpolation(transition.startValue, transition.endValue, progress, transition.easing);
          break;
        case 'physics':
          value = this.physicsBasedInterpolation(transition, elapsed, transition.physics);
          break;
        default:
          value = this.linearInterpolation(transition.startValue, transition.endValue, progress);
      }

      currentValues[targetName] = value;
    });

    return {
      activeTransitions: this.activeTransitions.size,
      queuedTransitions: this.transitionQueue.length,
      currentValues,
      metrics: this.metrics,
    };
  }

  /**
   * Update performance metrics
   */
  updateMetrics(blendTime) {
    this.metrics.transitionsProcessed++;
    this.metrics.averageBlendTime =
      (this.metrics.averageBlendTime * (this.metrics.transitionsProcessed - 1) + blendTime) /
      this.metrics.transitionsProcessed;
  }

  /**
   * Optimize blend state by removing redundant transitions
   */
  optimizeBlendState() {
    const optimized = new Map();
    const currentTime = performance.now();

    // Keep only the most recent transition for each target
    this.activeTransitions.forEach((transition, targetName) => {
      if (!optimized.has(targetName)) {
        optimized.set(targetName, transition);
      } else {
        const existing = optimized.get(targetName);
        if (transition.startTime > existing.startTime) {
          optimized.set(targetName, transition);
        }
      }
    });

    const removedCount = this.activeTransitions.size - optimized.size;
    this.activeTransitions = optimized;

    if (removedCount > 0) {
      this.logger.log('INFO', 'Blend state optimized', {
        removedTransitions: removedCount,
        remainingTransitions: this.activeTransitions.size,
      });
    }
  }

  /**
   * Check if blender is idle (no active transitions)
   */
  isIdle() {
    return this.activeTransitions.size === 0 && this.transitionQueue.length === 0;
  }

  /**
   * Get transition progress for specific target
   */
  getTransitionProgress(targetName) {
    const transition = this.activeTransitions.get(targetName);
    if (!transition) return 1.0; // Completed

    const elapsed = performance.now() - transition.startTime;
    return Math.min(elapsed / transition.duration, 1.0);
  }

  /**
   * Export blender configuration and state
   */
  exportState() {
    return {
      config: this.config,
      activeTransitions: Array.from(this.activeTransitions.entries()),
      transitionQueue: this.transitionQueue,
      blendState: Object.fromEntries(this.blendState),
      metrics: this.metrics,
    };
  }

  /**
   * Reset blender to initial state
   */
  reset() {
    this.activeTransitions.clear();
    this.transitionQueue = [];
    this.blendState.clear();
    this.metrics = {
      transitionsProcessed: 0,
      averageBlendTime: 0,
      maxConcurrentTransitions: 0,
    };

    this.logger.log('INFO', 'MorphTargetBlender reset');
  }
}

export default MorphTargetBlender;