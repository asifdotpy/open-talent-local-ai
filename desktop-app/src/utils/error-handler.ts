/**
 * Error Handling Utilities for OpenTalent
 * Provides custom error types, handlers, and recovery strategies
 */

/**
 * Custom error types for better error handling and debugging
 */
export enum ErrorType {
  OLLAMA_OFFLINE = 'OLLAMA_OFFLINE',
  MODEL_NOT_FOUND = 'MODEL_NOT_FOUND',
  TIMEOUT = 'TIMEOUT',
  INVALID_INPUT = 'INVALID_INPUT',
  NETWORK_ERROR = 'NETWORK_ERROR',
  API_ERROR = 'API_ERROR',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  RESOURCE_EXHAUSTED = 'RESOURCE_EXHAUSTED',
  UNKNOWN = 'UNKNOWN',
}

/**
 * Custom error class for better error tracking
 */
export class AppError extends Error {
  constructor(
    public type: ErrorType,
    message: string,
    public statusCode?: number,
    public originalError?: unknown,
    public retryable: boolean = false
  ) {
    super(message);
    this.name = 'AppError';
    Object.setPrototypeOf(this, AppError.prototype);
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage(): string {
    const messages: Record<ErrorType, string> = {
      [ErrorType.OLLAMA_OFFLINE]:
        'OpenTalent service is offline. Please ensure Ollama is running and accessible at localhost:11434.',
      [ErrorType.MODEL_NOT_FOUND]:
        'The selected AI model is not available. Please download it first or select another model.',
      [ErrorType.TIMEOUT]:
        'The request took too long to complete. Please check your internet connection and try again.',
      [ErrorType.INVALID_INPUT]:
        'The input provided is invalid. Please check and try again.',
      [ErrorType.NETWORK_ERROR]:
        'A network error occurred. Please check your internet connection.',
      [ErrorType.API_ERROR]:
        'An error occurred while communicating with the server.',
      [ErrorType.PERMISSION_DENIED]:
        'Permission denied. Please check your settings and try again.',
      [ErrorType.RESOURCE_EXHAUSTED]:
        'System resources are exhausted. Please close other applications and try again.',
      [ErrorType.UNKNOWN]:
        'An unexpected error occurred. Please try again or contact support.',
    };

    return messages[this.type] || messages[ErrorType.UNKNOWN];
  }

  /**
   * Get technical error details for debugging
   */
  getTechnicalDetails(): string {
    return `${this.type}: ${this.message}${
      this.statusCode ? ` (${this.statusCode})` : ''
    }`;
  }
}

/**
 * Error handler with retry logic
 */
export class ErrorHandler {
  private static readonly DEFAULT_RETRY_ATTEMPTS = 3;
  private static readonly DEFAULT_RETRY_DELAY = 1000; // ms

  /**
   * Handle errors and provide recovery strategy
   */
  static handleError(error: unknown, context?: string): AppError {
    console.error(`[Error Handler] ${context || 'Unknown context'}`, error);

    if (error instanceof AppError) {
      return error;
    }

    if (error instanceof TypeError) {
      return new AppError(
        ErrorType.INVALID_INPUT,
        `Type error: ${error.message}`,
        undefined,
        error,
        false
      );
    }

    if (error instanceof SyntaxError) {
      return new AppError(
        ErrorType.API_ERROR,
        `JSON parsing error: ${error.message}`,
        undefined,
        error,
        false
      );
    }

    // Handle axios errors
    if ((error as any)?.response) {
      const status = (error as any).response.status;
      const message = (error as any).response.data?.error || 'API Error';

      if (status === 404) {
        return new AppError(
          ErrorType.MODEL_NOT_FOUND,
          message,
          status,
          error,
          false
        );
      }

      if (status === 429 || status === 503) {
        return new AppError(
          ErrorType.RESOURCE_EXHAUSTED,
          'Server is busy. Please try again later.',
          status,
          error,
          true
        );
      }

      if (status >= 500) {
        return new AppError(
          ErrorType.API_ERROR,
          'Server error. Please try again later.',
          status,
          error,
          true
        );
      }

      return new AppError(
        ErrorType.API_ERROR,
        message,
        status,
        error,
        false
      );
    }

    // Handle timeout errors
    if ((error as any)?.code === 'ECONNABORTED') {
      return new AppError(
        ErrorType.TIMEOUT,
        'Request timeout. Please try again.',
        undefined,
        error,
        true
      );
    }

    // Handle network errors
    if ((error as any)?.code === 'ENOTFOUND' || (error as any)?.code === 'ECONNREFUSED') {
      return new AppError(
        ErrorType.OLLAMA_OFFLINE,
        'Unable to connect to OpenTalent service. Is it running?',
        undefined,
        error,
        true
      );
    }

    if ((error as any)?.message?.includes('Network Error')) {
      return new AppError(
        ErrorType.NETWORK_ERROR,
        'Network error occurred. Please check your connection.',
        undefined,
        error,
        true
      );
    }

    // Default unknown error
    return new AppError(
      ErrorType.UNKNOWN,
      error instanceof Error ? error.message : String(error),
      undefined,
      error,
      true
    );
  }

  /**
   * Retry failed operations with exponential backoff
   */
  static async retryWithBackoff<T>(
    fn: () => Promise<T>,
    attempts: number = this.DEFAULT_RETRY_ATTEMPTS,
    delay: number = this.DEFAULT_RETRY_DELAY,
    context?: string
  ): Promise<T> {
    let lastError: AppError | undefined;

    for (let attempt = 1; attempt <= attempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = this.handleError(error, context);

        // Don't retry non-retryable errors
        if (!lastError.retryable) {
          throw lastError;
        }

        // If last attempt, throw error
        if (attempt === attempts) {
          throw lastError;
        }

        // Calculate exponential backoff delay
        const backoffDelay = delay * Math.pow(2, attempt - 1);
        console.warn(
          `[Retry] Attempt ${attempt}/${attempts} failed. Retrying in ${backoffDelay}ms...`,
          lastError.getTechnicalDetails()
        );

        // Wait before retrying
        await new Promise((resolve) => setTimeout(resolve, backoffDelay));
      }
    }

    throw lastError;
  }

  /**
   * Validate user input
   */
  static validateInput(
    input: string,
    minLength: number = 1,
    maxLength: number = 5000
  ): void {
    if (!input || typeof input !== 'string') {
      throw new AppError(
        ErrorType.INVALID_INPUT,
        'Input must be a non-empty string',
        undefined,
        undefined,
        false
      );
    }

    if (input.trim().length < minLength) {
      throw new AppError(
        ErrorType.INVALID_INPUT,
        `Input must be at least ${minLength} characters`,
        undefined,
        undefined,
        false
      );
    }

    if (input.length > maxLength) {
      throw new AppError(
        ErrorType.INVALID_INPUT,
        `Input must not exceed ${maxLength} characters`,
        undefined,
        undefined,
        false
      );
    }
  }

  /**
   * Check if error is network-related (retryable)
   */
  static isNetworkError(error: AppError): boolean {
    return [
      ErrorType.OLLAMA_OFFLINE,
      ErrorType.NETWORK_ERROR,
      ErrorType.TIMEOUT,
      ErrorType.RESOURCE_EXHAUSTED,
    ].includes(error.type);
  }

  /**
   * Check if error is user input related (non-retryable)
   */
  static isValidationError(error: AppError): boolean {
    return [
      ErrorType.INVALID_INPUT,
      ErrorType.PERMISSION_DENIED,
      ErrorType.MODEL_NOT_FOUND,
    ].includes(error.type);
  }

  /**
   * Log error for monitoring/debugging
   */
  static logError(error: AppError, context?: string): void {
    const timestamp = new Date().toISOString();
    const logData = {
      timestamp,
      type: error.type,
      message: error.message,
      statusCode: error.statusCode,
      retryable: error.retryable,
      context,
      originalError: error.originalError,
    };

    // In production, send to error tracking service
    console.error('[ErrorLog]', JSON.stringify(logData, null, 2));
  }
}

/**
 * Connection health checker
 */
export class HealthChecker {
  private static readonly HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
  private static checkInterval: ReturnType<typeof setInterval> | null = null;
  private static isHealthy = true;

  /**
   * Start periodic health checks
   */
  static startHealthChecks(
    healthCheckFn: () => Promise<boolean>,
    onStatusChange?: (isHealthy: boolean) => void
  ): void {
    if (this.checkInterval) {
      return; // Already running
    }

    // Initial check
    healthCheckFn().then((healthy) => {
      this.isHealthy = healthy;
      if (!healthy && onStatusChange) {
        onStatusChange(false);
      }
    });

    // Periodic checks
    this.checkInterval = setInterval(async () => {
      try {
        const healthy = await healthCheckFn();

        // Notify if status changed
        if (healthy !== this.isHealthy) {
          this.isHealthy = healthy;
          if (onStatusChange) {
            onStatusChange(healthy);
          }
        }
      } catch (error) {
        console.warn('[HealthCheck] Check failed:', error);
        if (this.isHealthy) {
          this.isHealthy = false;
          if (onStatusChange) {
            onStatusChange(false);
          }
        }
      }
    }, this.HEALTH_CHECK_INTERVAL);
  }

  /**
   * Stop health checks
   */
  static stopHealthChecks(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  /**
   * Get current health status
   */
  static isServiceHealthy(): boolean {
    return this.isHealthy;
  }
}

export default ErrorHandler;
