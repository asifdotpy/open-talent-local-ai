# API Reference

**Version:** 1.0  
**Date:** December 14, 2025  
**Status:** Phase 8 Implementation

---

## Overview

This document describes all public APIs for OpenTalent services. All services run locally and communicate through HTTP/WebSocket.

---

## Interview Service

**File:** `src/services/interview-service.ts`  
**Purpose:** Orchestrates AI interview sessions with Ollama

### `checkStatus(): Promise<ServiceStatus>`

Check if Ollama service is running and responding.

**Parameters:** None

**Returns:**
```typescript
{
  status: 'online' | 'offline',
  version?: string,
  models?: string[],
  timestamp: number
}
```

**Example:**
```typescript
const status = await interviewService.checkStatus();
console.log(status.status); // 'online' or 'offline'
```

**Error Handling:**
- Retries 3 times with exponential backoff
- Throws `OLLAMA_OFFLINE` if all retries fail

### `listModels(): Promise<Model[]>`

Get list of available AI models.

**Parameters:** None

**Returns:**
```typescript
{
  name: string;
  version: string;
  size: number;  // bytes
  quantization: '4bit' | '8bit';
  parameters: number;  // 350M, 2B, 8B
}[]
```

**Example:**
```typescript
const models = await interviewService.listModels();
models.forEach(model => {
  console.log(`${model.name}: ${model.parameters} parameters`);
});
```

**Error Handling:**
- Returns empty array `[]` on failure
- Logs error but doesn't throw

### `startInterview(role: string, model: string, totalQuestions: number): Promise<InterviewSession>`

Start new interview session.

**Parameters:**
- `role: string` - One of: "Software Engineer", "Product Manager", "Data Analyst"
- `model: string` - Model name from `listModels()`
- `totalQuestions: number` - Number of questions (1-20)

**Returns:**
```typescript
{
  sessionId: string;  // UUID
  role: string;
  model: string;
  questions: Question[];
  currentQuestion: number;  // 0-indexed
  startTime: number;  // timestamp
  responses: string[];  // user responses
  scores: number[];  // interview scores
  status: 'active' | 'completed' | 'paused';
  avatarState: AvatarState;  // current avatar config
}
```

**Example:**
```typescript
const session = await interviewService.startInterview(
  'Software Engineer',
  'granite2b',
  5
);
console.log(`Question 1: ${session.questions[0].text}`);
```

**Validation:**
- Role must be exactly one of the 3 valid roles
- Model must exist in `listModels()`
- totalQuestions must be 1-20

**Error Handling:**
- Throws `INVALID_INPUT` if validation fails
- Throws `MODEL_NOT_FOUND` if model unavailable
- Throws `OLLAMA_OFFLINE` if service offline
- Retries 3 times with exponential backoff

### `sendResponse(sessionId: string, response: string): Promise<InterviewResponse>`

Send user response to current question.

**Parameters:**
- `sessionId: string` - From `startInterview()` return
- `response: string` - User's spoken response (10-2000 chars)

**Returns:**
```typescript
{
  questionIndex: number;
  response: string;  // user's response
  feedback: string;  // AI feedback
  score: number;  // 0-100
  nextQuestion?: Question;  // null if interview complete
  sessionState: InterviewSession;
}
```

**Example:**
```typescript
const result = await interviewService.sendResponse(
  sessionId,
  "I would start by understanding the requirements..."
);
console.log(`Score: ${result.score}/100`);
console.log(`Next: ${result.nextQuestion?.text}`);
```

**Validation:**
- Response must be 10-2000 characters
- Response cannot be empty/whitespace only
- Response cannot have > 30% special characters
- Session ID must be valid

**Error Handling:**
- Throws `INVALID_INPUT` if validation fails
- Throws `TIMEOUT` if server takes >60s
- Retries 3 times with exponential backoff

### `endInterview(sessionId: string): Promise<InterviewSummary>`

End interview and get summary.

**Parameters:**
- `sessionId: string` - From `startInterview()` return

**Returns:**
```typescript
{
  sessionId: string;
  role: string;
  totalQuestions: number;
  answeredQuestions: number;
  averageScore: number;  // 0-100
  scores: number[];
  feedback: string[];
  duration: number;  // seconds
  timestamp: number;
}
```

**Example:**
```typescript
const summary = await interviewService.endInterview(sessionId);
console.log(`Average Score: ${summary.averageScore}`);
```

**Error Handling:**
- Throws `INVALID_INPUT` if session ID invalid
- Returns summary even if Ollama offline (uses cached results)

---

## Validation Utility

**File:** `src/utils/validation.ts`  
**Purpose:** Input validation and data sanitization

### `InputValidator.validateInterviewResponse(response: string): ValidationResult`

Validate user's interview response.

**Parameters:**
- `response: string` - User's spoken response

**Returns:**
```typescript
{
  valid: boolean;
  error?: string;  // Error message if invalid
  message?: string;  // Help message
}
```

**Validation Rules:**
- Length must be 10-2000 characters
- Cannot be empty or whitespace-only
- Cannot have > 30% special characters
- Cannot contain null bytes

**Example:**
```typescript
const result = InputValidator.validateInterviewResponse("Too short");
if (!result.valid) {
  console.error(result.error);  // "Response should be at least 10 characters"
}
```

### `InputValidator.validateRole(role: string): ValidationResult`

Validate interview role.

**Parameters:**
- `role: string` - Interview role

**Returns:**
```typescript
{
  valid: boolean;
  error?: string;
}
```

**Valid Roles:**
- "Software Engineer"
- "Product Manager"
- "Data Analyst"

**Example:**
```typescript
const result = InputValidator.validateRole("Software Engineer");
// { valid: true }
```

### `InputValidator.validateModel(model: string, availableModels: string[]): ValidationResult`

Validate model name.

**Parameters:**
- `model: string` - Model name
- `availableModels: string[]` - Available models from `listModels()`

**Returns:**
```typescript
{
  valid: boolean;
  error?: string;
}
```

**Example:**
```typescript
const models = await interviewService.listModels();
const result = InputValidator.validateModel("granite2b", models.map(m => m.name));
```

### `InputValidator.validateTotalQuestions(count: number): ValidationResult`

Validate number of questions.

**Parameters:**
- `count: number` - Total questions requested

**Returns:**
```typescript
{
  valid: boolean;
  error?: string;
}
```

**Valid Range:** 1-20

**Example:**
```typescript
const result = InputValidator.validateTotalQuestions(5);
// { valid: true }
```

### `InputValidator.validateBatch(validations: [string, ValidationResult][]): BatchValidationResult`

Validate multiple fields at once.

**Parameters:**
- `validations: [string, ValidationResult][]` - Array of [fieldName, validationResult] pairs

**Returns:**
```typescript
{
  valid: boolean;  // true only if all valid
  errors: Record<string, string>;  // field -> error message
}
```

**Example:**
```typescript
const results = InputValidator.validateBatch([
  ['role', InputValidator.validateRole(role)],
  ['response', InputValidator.validateInterviewResponse(response)],
  ['questions', InputValidator.validateTotalQuestions(5)]
]);

if (!results.valid) {
  console.error(results.errors);
  // { role: 'Invalid role', response: 'Too short', ... }
}
```

### `InputValidator.sanitizeInput(input: string): string`

Sanitize user input by removing dangerous characters.

**Parameters:**
- `input: string` - User input

**Returns:**
- `string` - Sanitized input

**Sanitization:**
- Removes null bytes
- Removes control characters
- Trims whitespace
- Preserves regular characters

**Example:**
```typescript
const clean = InputValidator.sanitizeInput("  Hello\\x00World  ");
// Returns: "HelloWorld"
```

### `InputValidator.escapeHTML(input: string): string`

Escape HTML characters to prevent XSS.

**Parameters:**
- `input: string` - User input with HTML characters

**Returns:**
- `string` - Escaped HTML

**Escaping:**
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&quot;`
- `'` → `&#39;`

**Example:**
```typescript
const safe = InputValidator.escapeHTML("<script>alert('xss')</script>");
// Returns: "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;"
```

### `DataSanitizer.sanitizeJSON(data: any): any`

Recursively sanitize JSON object.

**Parameters:**
- `data: any` - Object to sanitize

**Returns:**
- `any` - Sanitized object

**Sanitization:**
- Removes null bytes from strings
- Removes control characters
- Recursively sanitizes nested objects
- Preserves structure

**Example:**
```typescript
const data = {
  name: "John\\x00Doe",
  email: "john@example.com",
  nested: { value: "test\\x00" }
};
const clean = DataSanitizer.sanitizeJSON(data);
// { name: "JohnDoe", email: "john@example.com", nested: { value: "test" } }
```

### `DataSanitizer.removeSensitiveData(data: any): any`

Remove sensitive information from object.

**Parameters:**
- `data: any` - Object to clean

**Returns:**
- `any` - Object with sensitive data removed

**Redacted Fields:**
- password, pwd, secret, token, apiKey, api_key
- creditCard, ccNumber, cc_number
- ssn, socialSecurity, socialSecurityNumber
- bankAccount, accountNumber, account_number

**Example:**
```typescript
const user = {
  name: "John",
  password: "secret123",
  apiKey: "sk-1234567890"
};
const clean = DataSanitizer.removeSensitiveData(user);
// { name: "John", password: "***REDACTED***", apiKey: "***REDACTED***" }
```

---

## Error Handler Utility

**File:** `src/utils/error-handler.ts`  
**Purpose:** Centralized error handling and retry logic

### `ErrorHandler.handleError(error: any, context?: string): AppError`

Categorize and handle error.

**Parameters:**
- `error: any` - Error object from try-catch
- `context?: string` - Operation context for debugging

**Returns:**
```typescript
AppError {
  type: ErrorType;  // OLLAMA_OFFLINE, TIMEOUT, etc.
  message: string;
  statusCode?: number;
  retryable: boolean;
  context?: string;
  originalError?: any;
  
  getUserMessage(): string;  // User-friendly message
  getTechnicalDetails(): string;  // Technical debugging info
}
```

**Example:**
```typescript
try {
  await interviewService.sendResponse(sessionId, response);
} catch (error) {
  const appError = ErrorHandler.handleError(error, 'Send response');
  console.log(appError.getUserMessage());  // Show to user
}
```

### `ErrorHandler.retryWithBackoff<T>(fn: () => Promise<T>, attempts?: number, delay?: number, context?: string): Promise<T>`

Execute function with automatic retry.

**Parameters:**
- `fn: () => Promise<T>` - Async function to execute
- `attempts?: number` - Number of attempts (default: 3)
- `delay?: number` - Initial delay in ms (default: 1000)
- `context?: string` - Operation context

**Returns:**
- `Promise<T>` - Result of successful function call

**Retry Strategy:**
- Exponential backoff: delay * 2^(attempt-1)
- Attempt 1: delay
- Attempt 2: delay * 2
- Attempt 3: delay * 4
- Non-retryable errors thrown immediately

**Example:**
```typescript
const result = await ErrorHandler.retryWithBackoff(
  () => interviewService.sendResponse(sessionId, response),
  3,      // attempts
  1000,   // initial delay
  'Send response'
);
```

### `HealthChecker.startHealthChecks(checkFn: () => Promise<boolean>, onStatusChange?: (isHealthy: boolean) => void): void`

Start continuous health checks.

**Parameters:**
- `checkFn: () => Promise<boolean>` - Function that returns true if service healthy
- `onStatusChange?: (isHealthy: boolean) => void` - Called when health status changes

**Returns:** None

**Health Check Frequency:** Every 30 seconds

**Example:**
```typescript
HealthChecker.startHealthChecks(
  () => interviewService.checkStatus().then(s => s.status === 'online'),
  (isHealthy) => {
    if (!isHealthy) {
      console.log('Service went offline');
    }
  }
);
```

### `HealthChecker.isServiceHealthy(): boolean`

Get current service health status.

**Parameters:** None

**Returns:**
- `boolean` - true if service is healthy, false otherwise

**Example:**
```typescript
if (HealthChecker.isServiceHealthy()) {
  await interviewService.sendResponse(sessionId, response);
} else {
  console.log('Service is offline, trying to recover...');
}
```

### `HealthChecker.getLastHealthCheck(): { timestamp: number, isHealthy: boolean } | null`

Get last health check result.

**Parameters:** None

**Returns:**
```typescript
{
  timestamp: number;  // Date.now()
  isHealthy: boolean;
} | null  // null if no checks performed yet
```

**Example:**
```typescript
const lastCheck = HealthChecker.getLastHealthCheck();
if (lastCheck) {
  console.log(`Service healthy as of ${new Date(lastCheck.timestamp)}`);
}
```

---

## React Components

### ErrorBoundary

**File:** `src/components/ErrorBoundary.tsx`  
**Purpose:** React error boundary for catching component errors

**Props:**
```typescript
{
  children: ReactNode;
  onError?: (error: AppError, errorInfo: ErrorInfo) => void;
  fallback?: (error: AppError, reset: () => void) => ReactNode;
}
```

**Example:**
```typescript
<ErrorBoundary
  onError={(error) => {
    console.error('Component error:', error);
  }}
  fallback={(error, reset) => (
    <div>
      <h1>Something went wrong</h1>
      <p>{error.getUserMessage()}</p>
      <button onClick={reset}>Try Again</button>
    </div>
  )}
>
  <InterviewApp />
</ErrorBoundary>
```

### LoadingSpinner

**File:** `src/components/LoadingSpinner.tsx`  
**Purpose:** Animated loading indicator

**Props:**
```typescript
{
  isLoading: boolean;
  message?: string;
  progress?: number;  // 0-100
  size?: 'small' | 'medium' | 'large';  // default: 'medium'
  cancelable?: boolean;
  onCancel?: () => void;
  overlay?: boolean;  // Show as full-screen overlay
}
```

**Example:**
```typescript
<LoadingSpinner
  isLoading={loading}
  message="Starting interview..."
  progress={0}
  size="medium"
  cancelable={true}
  onCancel={() => handleCancel()}
/>
```

### Skeleton

**File:** `src/components/LoadingSpinner.tsx`  
**Purpose:** Skeleton placeholder for data loading

**Props:**
```typescript
{
  width?: string;  // CSS width, default: '100%'
  height?: string;  // CSS height, default: '1rem'
  count?: number;  // Number of skeleton lines, default: 1
  circle?: boolean;  // Circular skeleton
}
```

**Example:**
```typescript
<Skeleton width="100%" height="2rem" count={3} />
```

### LoadingOverlay

**File:** `src/components/LoadingSpinner.tsx`  
**Purpose:** Full-screen loading overlay

**Props:**
```typescript
{
  isVisible: boolean;
  message?: string;
}
```

**Example:**
```typescript
<LoadingOverlay
  isVisible={loading}
  message="Downloading AI model..."
/>
```

---

## Type Definitions

### ServiceStatus

```typescript
interface ServiceStatus {
  status: 'online' | 'offline';
  version?: string;
  models?: string[];
  timestamp: number;
}
```

### Model

```typescript
interface Model {
  name: string;
  version: string;
  size: number;  // bytes
  quantization: '4bit' | '8bit';
  parameters: number;  // 350M, 2B, 8B
}
```

### InterviewSession

```typescript
interface InterviewSession {
  sessionId: string;
  role: string;
  model: string;
  questions: Question[];
  currentQuestion: number;
  startTime: number;
  responses: string[];
  scores: number[];
  status: 'active' | 'completed' | 'paused';
  avatarState: AvatarState;
}
```

### Question

```typescript
interface Question {
  id: string;
  index: number;
  text: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  followUp?: string;
}
```

### InterviewResponse

```typescript
interface InterviewResponse {
  questionIndex: number;
  response: string;
  feedback: string;
  score: number;
  nextQuestion?: Question;
  sessionState: InterviewSession;
}
```

### ValidationResult

```typescript
interface ValidationResult {
  valid: boolean;
  error?: string;
  message?: string;
}
```

### BatchValidationResult

```typescript
interface BatchValidationResult {
  valid: boolean;
  errors: Record<string, string>;
}
```

---

## Constants

### Interview Constants

```typescript
// Interview configuration
const INTERVIEW_CONFIG = {
  MIN_RESPONSE_LENGTH: 10,      // characters
  MAX_RESPONSE_LENGTH: 2000,    // characters
  MIN_QUESTIONS: 1,
  MAX_QUESTIONS: 20,
  RESPONSE_TIMEOUT: 60000,      // 60 seconds
  MAX_SPECIAL_CHAR_RATIO: 0.30, // 30%
};

// Valid roles
const VALID_ROLES = [
  'Software Engineer',
  'Product Manager',
  'Data Analyst'
];
```

### Error Constants

```typescript
// Error types
enum ErrorType {
  OLLAMA_OFFLINE = 'OLLAMA_OFFLINE',
  MODEL_NOT_FOUND = 'MODEL_NOT_FOUND',
  TIMEOUT = 'TIMEOUT',
  INVALID_INPUT = 'INVALID_INPUT',
  NETWORK_ERROR = 'NETWORK_ERROR',
  API_ERROR = 'API_ERROR',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  RESOURCE_EXHAUSTED = 'RESOURCE_EXHAUSTED',
  UNKNOWN = 'UNKNOWN'
}

// Retry configuration
const RETRY_CONFIG = {
  MAX_ATTEMPTS: 3,
  INITIAL_DELAY: 1000,  // ms
  BACKOFF_MULTIPLIER: 2,
};

// Health check configuration
const HEALTH_CHECK_CONFIG = {
  INTERVAL: 30000,  // 30 seconds
  TIMEOUT: 5000,    // 5 seconds
};
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 14, 2025 | Initial API reference with services, utilities, components |

---

**For more information, see:**
- [ERROR_HANDLING.md](./ERROR_HANDLING.md)
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- [README.md](../README.md)
