/**
 * Input Validation Utilities
 * Provides validation functions for user input and data
 */

import { AppError, ErrorType } from './error-handler';

/**
 * Validation result with error details
 */
export interface ValidationResult {
  valid: boolean;
  error?: string;
  message?: string;
}

/**
 * Validation utilities class
 */
export class InputValidator {
  /**
   * Validate interview response
   */
  static validateInterviewResponse(
    response: string
  ): ValidationResult {
    if (!response || typeof response !== 'string') {
      return {
        valid: false,
        error: 'Response must be a non-empty string',
      };
    }

    const trimmed = response.trim();

    if (trimmed.length === 0) {
      return {
        valid: false,
        error: 'Response cannot be empty or whitespace only',
      };
    }

    if (trimmed.length < 10) {
      return {
        valid: false,
        error: 'Response should be at least 10 characters long',
      };
    }

    if (trimmed.length > 2000) {
      return {
        valid: false,
        error: 'Response cannot exceed 2000 characters',
      };
    }

    // Check for excessive special characters (potential spam)
    const specialCharRatio =
      (trimmed.match(/[^a-zA-Z0-9\s\.\,\!\?\'\"\-\:\;]/g) || []).length /
      trimmed.length;

    if (specialCharRatio > 0.3) {
      return {
        valid: false,
        error: 'Response contains too many special characters',
      };
    }

    return { valid: true, message: 'Response is valid' };
  }

  /**
   * Validate role selection
   */
  static validateRole(role: string): ValidationResult {
    const validRoles = [
      'Software Engineer',
      'Product Manager',
      'Data Analyst',
    ];

    if (!role || typeof role !== 'string') {
      return {
        valid: false,
        error: 'Role must be a non-empty string',
      };
    }

    if (!validRoles.includes(role)) {
      return {
        valid: false,
        error: `Invalid role. Valid options: ${validRoles.join(', ')}`,
      };
    }

    return { valid: true, message: 'Role is valid' };
  }

  /**
   * Validate model selection
   */
  static validateModel(
    model: string,
    availableModels: string[]
  ): ValidationResult {
    if (!model || typeof model !== 'string') {
      return {
        valid: false,
        error: 'Model must be a non-empty string',
      };
    }

    if (availableModels.length === 0) {
      return {
        valid: false,
        error: 'No models available',
      };
    }

    if (!availableModels.includes(model)) {
      return {
        valid: false,
        error: `Model "${model}" is not available. Available models: ${availableModels.join(', ')}`,
      };
    }

    return { valid: true, message: 'Model is valid' };
  }

  /**
   * Validate number of questions
   */
  static validateTotalQuestions(
    totalQuestions: unknown
  ): ValidationResult {
    const num = typeof totalQuestions === 'number' 
      ? totalQuestions 
      : parseInt(String(totalQuestions), 10);

    if (isNaN(num)) {
      return {
        valid: false,
        error: 'Total questions must be a number',
      };
    }

    if (num < 1) {
      return {
        valid: false,
        error: 'Total questions must be at least 1',
      };
    }

    if (num > 20) {
      return {
        valid: false,
        error: 'Total questions cannot exceed 20',
      };
    }

    return { valid: true, message: 'Total questions is valid' };
  }

  /**
   * Validate URL
   */
  static validateURL(url: string): ValidationResult {
    try {
      new URL(url);
      return { valid: true, message: 'URL is valid' };
    } catch {
      return {
        valid: false,
        error: 'Invalid URL format',
      };
    }
  }

  /**
   * Validate email
   */
  static validateEmail(email: string): ValidationResult {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email || typeof email !== 'string') {
      return {
        valid: false,
        error: 'Email must be a non-empty string',
      };
    }

    if (!emailRegex.test(email)) {
      return {
        valid: false,
        error: 'Invalid email format',
      };
    }

    return { valid: true, message: 'Email is valid' };
  }

  /**
   * Validate required fields
   */
  static validateRequired(
    fields: Record<string, unknown>
  ): ValidationResult {
    for (const [key, value] of Object.entries(fields)) {
      if (value === undefined || value === null || value === '') {
        return {
          valid: false,
          error: `Field "${key}" is required`,
        };
      }
    }

    return { valid: true, message: 'All required fields are present' };
  }

  /**
   * Validate password strength
   */
  static validatePassword(password: string): ValidationResult {
    if (!password || typeof password !== 'string') {
      return {
        valid: false,
        error: 'Password must be a non-empty string',
      };
    }

    if (password.length < 8) {
      return {
        valid: false,
        error: 'Password must be at least 8 characters long',
      };
    }

    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*]/.test(password);

    const strength = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChar]
      .filter(Boolean).length;

    if (strength < 2) {
      return {
        valid: false,
        error:
          'Password must contain uppercase, lowercase, numbers, and special characters',
      };
    }

    return { valid: true, message: 'Password is valid' };
  }

  /**
   * Sanitize string input
   */
  static sanitizeInput(input: string): string {
    if (typeof input !== 'string') {
      return '';
    }

    // Remove null bytes
    let sanitized = input.replace(/\0/g, '');

    // Remove control characters
    sanitized = sanitized.replace(/[\x00-\x1F\x7F]/g, '');

    // Trim whitespace
    sanitized = sanitized.trim();

    return sanitized;
  }

  /**
   * Escape HTML special characters
   */
  static escapeHTML(text: string): string {
    if (typeof text !== 'string') {
      return '';
    }

    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Validate file upload
   */
  static validateFileUpload(
    file: File,
    maxSizeInMB: number = 10,
    allowedTypes: string[] = ['text/plain', 'application/json']
  ): ValidationResult {
    if (!(file instanceof File)) {
      return {
        valid: false,
        error: 'File must be a File object',
      };
    }

    const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
    if (file.size > maxSizeInBytes) {
      return {
        valid: false,
        error: `File size must not exceed ${maxSizeInMB}MB`,
      };
    }

    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `File type must be one of: ${allowedTypes.join(', ')}`,
      };
    }

    return { valid: true, message: 'File is valid' };
  }

  /**
   * Batch validate multiple fields
   */
  static validateBatch(
    validations: Array<[string, ValidationResult]>
  ): { valid: boolean; errors: Record<string, string> } {
    const errors: Record<string, string> = {};

    for (const [field, result] of validations) {
      if (!result.valid && result.error) {
        errors[field] = result.error;
      }
    }

    return {
      valid: Object.keys(errors).length === 0,
      errors,
    };
  }
}

/**
 * Data sanitization utilities
 */
export class DataSanitizer {
  /**
   * Sanitize JSON data
   */
  static sanitizeJSON(json: unknown): unknown {
    if (json === null || json === undefined) {
      return null;
    }

    if (typeof json === 'string') {
      return InputValidator.sanitizeInput(json);
    }

    if (typeof json === 'object') {
      if (Array.isArray(json)) {
        return json.map((item) => this.sanitizeJSON(item));
      }

      const sanitized: Record<string, unknown> = {};
      for (const [key, value] of Object.entries(json)) {
        sanitized[key] = this.sanitizeJSON(value);
      }
      return sanitized;
    }

    return json;
  }

  /**
   * Remove sensitive data from objects
   */
  static removeSensitiveData(
    obj: Record<string, unknown>,
    sensitiveFields: string[] = ['password', 'apiKey', 'token', 'secret']
  ): Record<string, unknown> {
    const cleaned = { ...obj };

    for (const field of sensitiveFields) {
      if (field in cleaned) {
        cleaned[field] = '[REDACTED]';
      }
    }

    return cleaned;
  }
}

export default InputValidator;
