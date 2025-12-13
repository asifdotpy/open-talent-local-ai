# Error Handling Guide

**Version:** 1.0  
**Date:** December 14, 2025  
**Status:** Phase 8 Implementation

---

## Overview

OpenTalent implements comprehensive error handling with user-friendly messages, automatic retry logic, and graceful degradation. This guide explains the error handling system and how to handle errors in your code.

---

## Error Types

OpenTalent defines the following error types:

### 1. **OLLAMA_OFFLINE**
**Cause:** Ollama service is not running or unreachable  
**User Message:** "OpenTalent service is offline. Please ensure Ollama is running and accessible at localhost:11434."  
**Retryable:** Yes  
**Recovery:** Ensure Ollama is installed and running

```bash
# Start Ollama
ollama serve

# Check health
curl http://localhost:11434/api/tags
```

### 2. **MODEL_NOT_FOUND**
**Cause:** Selected model is not available  
**User Message:** "The selected AI model is not available. Please download it first or select another model."  
**Retryable:** No  
**Recovery:** Download the model or select an available model

### 3. **TIMEOUT**
**Cause:** Request took too long to complete  
**User Message:** "The request took too long to complete. Please check your internet connection and try again."  
**Retryable:** Yes  
**Recovery:** Improve network connection or increase timeout

### 4. **INVALID_INPUT**
**Cause:** User provided invalid input  
**User Message:** "The input provided is invalid. Please check and try again."  
**Retryable:** No  
**Recovery:** Validate input and try again

**Validation Rules:**
- Response must be 10-2000 characters
- Response cannot be empty or whitespace only
- Response cannot have excessive special characters (> 30%)
- Role must be one of: Software Engineer, Product Manager, Data Analyst
- Questions must be between 1-20

### 5. **NETWORK_ERROR**
**Cause:** Network connectivity issue  
**User Message:** "A network error occurred. Please check your internet connection."  
**Retryable:** Yes  
**Recovery:** Check internet connection

### 6. **API_ERROR**
**Cause:** Server returned error response  
**User Message:** "An error occurred while communicating with the server."  
**Retryable:** Depends on status code (5xx errors are retryable)  
**Recovery:** Check logs and retry

### 7. **PERMISSION_DENIED**
**Cause:** User lacks required permissions  
**User Message:** "Permission denied. Please check your settings and try again."  
**Retryable:** No  
**Recovery:** Check permissions and try again

### 8. **RESOURCE_EXHAUSTED**
**Cause:** System resources are exhausted  
**User Message:** "System resources are exhausted. Please close other applications and try again."  
**Retryable:** Yes  
**Recovery:** Free up system resources

### 9. **UNKNOWN**
**Cause:** Unexpected error  
**User Message:** "An unexpected error occurred. Please try again or contact support."  
**Retryable:** Yes  
**Recovery:** Check logs and restart application

---

## Handling Errors in Code

### Basic Error Handling

```typescript
import { ErrorHandler, AppError } from '../utils/error-handler';

try {
  const result = await someAsyncOperation();
} catch (error) {
  const appError = ErrorHandler.handleError(error, 'Operation context');
  
  // Get user-friendly message
  console.log(appError.getUserMessage());
  
  // Get technical details for debugging
  console.log(appError.getTechnicalDetails());
  
  // Check if error is retryable
  if (appError.retryable) {
    // Attempt retry
  }
}
```

### Retry with Exponential Backoff

```typescript
const result = await ErrorHandler.retryWithBackoff(
  () => someAsyncOperation(),
  3,        // attempts
  1000,     // initial delay in ms
  'Operation context'
);
```

### Input Validation

```typescript
import { InputValidator } from '../utils/validation';

// Validate interview response
const result = InputValidator.validateInterviewResponse(userInput);
if (!result.valid) {
  console.error(result.error);
}

// Validate role
const roleValidation = InputValidator.validateRole(role);
if (!roleValidation.valid) {
  throw new Error(roleValidation.error);
}

// Batch validate multiple fields
const validations = [
  ['role', InputValidator.validateRole(role)],
  ['response', InputValidator.validateInterviewResponse(response)],
];
const batch = InputValidator.validateBatch(validations);
if (!batch.valid) {
  console.error(batch.errors); // { role: 'error message', ... }
}
```

### Error Boundary Component

```typescript
import ErrorBoundary from '../components/ErrorBoundary';

// Wrap components
<ErrorBoundary
  onError={(error) => {
    // Log error to monitoring service
    console.error('Component error:', error);
  }}
  fallback={(error, reset) => (
    <div>
      <h1>Error: {error.getUserMessage()}</h1>
      <button onClick={reset}>Try Again</button>
    </div>
  )}
>
  <YourComponent />
</ErrorBoundary>
```

### Using LoadingSpinner

```typescript
import { LoadingSpinner, LoadingOverlay } from '../components/LoadingSpinner';

// Basic spinner
<LoadingSpinner
  isLoading={loading}
  message="Initializing interview..."
  size="medium"
/>

// With progress
<LoadingSpinner
  isLoading={loading}
  message="Downloading model..."
  progress={currentProgress}
  cancelable
  onCancel={() => cancelDownload()}
/>

// Full-screen overlay
<LoadingOverlay
  isVisible={loading}
  message="Starting interview session..."
/>
```

---

## Best Practices

### 1. **Always Provide Context**

```typescript
// Good: Context helps debugging
try {
  await startInterview(role, model);
} catch (error) {
  const appError = ErrorHandler.handleError(error, 'Start interview with role: ' + role);
}

// Bad: No context
catch (error) {
  const appError = ErrorHandler.handleError(error);
}
```

### 2. **Check Retryable Flag**

```typescript
try {
  await operation();
} catch (error) {
  const appError = ErrorHandler.handleError(error);
  
  if (appError.retryable) {
    // Safe to retry
    await ErrorHandler.retryWithBackoff(() => operation());
  } else {
    // Don't retry - user error
    throw appError;
  }
}
```

### 3. **Validate User Input Early**

```typescript
// Validate before processing
const validation = InputValidator.validateInterviewResponse(userInput);
if (!validation.valid) {
  setError(validation.error);
  return;
}

// Process validated input
await processResponse(userInput);
```

### 4. **Use Health Checks**

```typescript
import { HealthChecker } from '../utils/error-handler';

// Start health checks
HealthChecker.startHealthChecks(
  () => service.checkStatus(),
  (isHealthy) => {
    console.log('Service health changed:', isHealthy);
  }
);

// Check current health
if (HealthChecker.isServiceHealthy()) {
  // Proceed
} else {
  // Show maintenance message
}
```

### 5. **Sanitize Input**

```typescript
import { InputValidator, DataSanitizer } from '../utils/validation';

// Sanitize user input
const sanitized = InputValidator.sanitizeInput(userInput);

// Escape HTML
const safe = InputValidator.escapeHTML(userInput);

// Remove sensitive data from logs
const cleaned = DataSanitizer.removeSensitiveData(userData);
```

---

## Common Error Scenarios

### Scenario 1: Ollama Offline

**What Happens:**
1. User starts interview
2. Connection to Ollama fails
3. OLLAMA_OFFLINE error is raised
4. Automatic retry attempts (3x with backoff)
5. User sees: "OpenTalent service is offline..."

**Resolution Steps:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Scenario 2: Model Not Found

**What Happens:**
1. User selects a model that doesn't exist
2. API returns 404 error
3. MODEL_NOT_FOUND error is raised
4. No retry (non-retryable)
5. User sees: "AI model is not available..."

**Resolution Steps:**
1. Check available models in UI
2. Download desired model: `ollama pull modelname`
3. Retry interview

### Scenario 3: Timeout During Interview

**What Happens:**
1. User response is sent
2. Server takes > 60 seconds to respond
3. TIMEOUT error is raised
4. Automatic retry (3x with exponential backoff)
5. User sees spinner with "Please wait..."

**Resolution Steps:**
1. Wait for retry to complete
2. If fails, check:
   - Internet connection
   - Model performance
   - System resources

### Scenario 4: Invalid User Input

**What Happens:**
1. User sends empty response
2. Validation fails
3. INVALID_INPUT error is raised
4. No retry (user error)
5. User sees: "Response should be at least 10 characters..."

**Resolution Steps:**
1. Read error message
2. Provide valid input
3. Retry

---

## Error Logging

All errors are logged for debugging and monitoring:

```typescript
// Automatic logging in error handler
ErrorHandler.logError(appError, 'Operation context');

// Output includes:
// {
//   timestamp: "2025-12-14T10:00:00.000Z",
//   type: "TIMEOUT",
//   message: "Request timeout...",
//   statusCode: undefined,
//   retryable: true,
//   context: "Send response",
//   originalError: { ... }
// }
```

In production, logs should be sent to error tracking service (e.g., Sentry, LogRocket).

---

## Testing Error Handling

### Test Network Errors

```typescript
// Simulate Ollama offline
// Stop Ollama: killall ollama
// Application should show error message
// Automatic retry should attempt 3 times
// User can manually retry
```

### Test Timeout Errors

```typescript
// Simulate slow response
// Use network throttling in DevTools
// Response should timeout after 60s
// Automatic retry should trigger
```

### Test Validation Errors

```typescript
// Test empty response: ""
// Test short response: "Hi"
// Test long response: > 2000 chars
// Test special characters: "!@#$%^&*()"
// Each should show validation error
```

### Test Invalid Input

```typescript
// Test invalid role: "Physicist"
// Test invalid questions: 0, 21, "abc"
// Test invalid model: "nonexistent"
// Each should show clear error message
```

---

## Support

If you encounter an error that doesn't match any of these types or scenarios:

1. **Check the error message** - It should tell you what went wrong
2. **Review the logs** - Technical details help debugging
3. **Restart the application** - Fixes temporary issues
4. **Restart Ollama** - Fixes Ollama-related issues
5. **Check system resources** - Free up RAM/CPU if exhausted
6. **Contact support** - Include error details and logs

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 14, 2025 | Initial implementation with 9 error types, retry logic, validation |

---

**For more information, see:**
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- [API_REFERENCE.md](./API_REFERENCE.md)
- [README.md](../README.md)
