/**
 * StructuredLogger - Production-ready logging system
 * 
 * Features:
 * - Multiple log levels (DEBUG, INFO, WARN, ERROR)
 * - JSON and text formats
 * - Context-aware logging
 * - Request correlation IDs
 */

export class StructuredLogger {
  constructor(config = {}) {
    this.config = {
      level: config.level || 'info',
      format: config.format || 'json',
      includeTimestamp: config.includeTimestamp !== false,
      includeRequestId: config.includeRequestId !== false,
      namespace: config.namespace || 'avatar-renderer',
      ...config
    };

    this.levels = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3
    };

    this.currentLevel = this.levels[this.config.level] || this.levels.info;
  }

  /**
   * Log a debug message
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  debug(message, context = {}) {
    this._log('debug', message, context);
  }

  /**
   * Log an info message
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  info(message, context = {}) {
    this._log('info', message, context);
  }

  /**
   * Log a warning message
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  warn(message, context = {}) {
    this._log('warn', message, context);
  }

  /**
   * Log an error message
   * @param {string} message - Log message
   * @param {Object|Error} context - Additional context or Error object
   */
  error(message, context = {}) {
    // Handle Error objects
    if (context instanceof Error) {
      context = {
        error: context.message,
        stack: context.stack,
        name: context.name
      };
    }
    this._log('error', message, context);
  }

  /**
   * Alias for info (backward compatibility with console.log)
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  log(message, context = {}) {
    this.info(message, context);
  }

  /**
   * Create a child logger with additional context
   * @param {Object} context - Context to include in all logs
   * @returns {StructuredLogger} Child logger
   */
  child(context = {}) {
    const childLogger = new StructuredLogger(this.config);
    childLogger.defaultContext = { ...this.defaultContext, ...context };
    return childLogger;
  }

  /**
   * Internal log method
   * @private
   */
  _log(level, message, context = {}) {
    if (this.levels[level] < this.currentLevel) {
      return; // Skip if below current log level
    }

    const logEntry = this._buildLogEntry(level, message, context);

    if (this.config.format === 'json') {
      this._outputJSON(logEntry);
    } else {
      this._outputText(logEntry);
    }
  }

  /**
   * Build log entry object
   * @private
   */
  _buildLogEntry(level, message, context) {
    const entry = {
      level: level.toUpperCase(),
      message,
      namespace: this.config.namespace
    };

    if (this.config.includeTimestamp) {
      entry.timestamp = new Date().toISOString();
    }

    // Merge default context and provided context
    if (this.defaultContext) {
      Object.assign(entry, this.defaultContext);
    }

    if (context && Object.keys(context).length > 0) {
      Object.assign(entry, context);
    }

    return entry;
  }

  /**
   * Output log entry as JSON
   * @private
   */
  _outputJSON(entry) {
    const output = JSON.stringify(entry);
    
    if (entry.level === 'ERROR') {
      console.error(output);
    } else if (entry.level === 'WARN') {
      console.warn(output);
    } else {
      console.log(output);
    }
  }

  /**
   * Output log entry as formatted text
   * @private
   */
  _outputText(entry) {
    const timestamp = entry.timestamp ? `[${entry.timestamp}] ` : '';
    const level = `[${entry.level}]`;
    const namespace = `[${entry.namespace}]`;
    const message = entry.message;

    // Remove standard fields from context
    const context = { ...entry };
    delete context.level;
    delete context.message;
    delete context.timestamp;
    delete context.namespace;

    const contextStr = Object.keys(context).length > 0 
      ? ' ' + JSON.stringify(context, null, 2)
      : '';

    const output = `${timestamp}${level} ${namespace} ${message}${contextStr}`;

    if (entry.level === 'ERROR') {
      console.error(output);
    } else if (entry.level === 'WARN') {
      console.warn(output);
    } else {
      console.log(output);
    }
  }

  /**
   * Set log level
   * @param {string} level - New log level
   */
  setLevel(level) {
    if (this.levels[level] !== undefined) {
      this.config.level = level;
      this.currentLevel = this.levels[level];
    } else {
      throw new Error(`Invalid log level: ${level}. Must be one of: ${Object.keys(this.levels).join(', ')}`);
    }
  }

  /**
   * Get current log level
   * @returns {string} Current log level
   */
  getLevel() {
    return this.config.level;
  }
}

export default StructuredLogger;
