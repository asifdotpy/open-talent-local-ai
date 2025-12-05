/**
 * Singleton logger utility for structured logging
 */
export class Logger {
  static instance = null;

  constructor() {
    if (Logger.instance) {
      return Logger.instance;
    }

    this.logLevel = 'INFO';
    this.enabledCategories = new Set([
      'ANALYSIS',
      'SUCCESS',
      'ERROR',
      'WARNING',
      'INFO',
    ]);
    Logger.instance = this;
  }

  static getInstance() {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  log(category, message, data = null) {
    if (!this.enabledCategories.has(category)) {
      return;
    }

    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${category}: ${message}`;

    if (data) {
      console.log(logMessage, data);
    } else {
      console.log(logMessage);
    }
  }

  warn(message, data = null) {
    this.log('WARNING', message, data);
  }

  error(message, data = null) {
    this.log('ERROR', message, data);
  }

  info(message, data = null) {
    this.log('INFO', message, data);
  }

  debug(message, data = null) {
    this.log('DEBUG', message, data);
  }

  setLogLevel(level) {
    this.logLevel = level;
  }

  enableCategory(category) {
    this.enabledCategories.add(category);
  }

  disableCategory(category) {
    this.enabledCategories.delete(category);
  }
}
