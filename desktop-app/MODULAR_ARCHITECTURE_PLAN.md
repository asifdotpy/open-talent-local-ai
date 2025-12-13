# Desktop App Modular Architecture Plan

> **Version:** 1.0  
> **Date:** December 12, 2025  
> **Goal:** Transform OpenTalent Desktop into a highly modular, maintainable, and scalable architecture

---

## 📋 Executive Summary

**Current State:** The desktop app has a decent foundation with separated concerns (main/renderer/services), but lacks true modularity. Services are tightly coupled, configuration is scattered, and there's no clear plugin architecture.

**Target State:** A fully modular architecture with:
- ✅ Dependency Injection (DI) container
- ✅ Plugin system for extensibility
- ✅ Clear module boundaries with interfaces
- ✅ Centralized configuration management
- ✅ Event-driven communication between modules
- ✅ Testable, swappable components

**Timeline:** 3-4 days (Dec 12-15) - Fits perfectly into Day 3-4 & Day 5-6 of SelectUSA sprint

---

## 🎯 Modularity Assessment (Current State)

### ✅ What's Good

| Component | Status | Notes |
|-----------|--------|-------|
| **Directory Structure** | ✅ Good | Clear separation: main/, renderer/, services/, utils/ |
| **Service Layer** | ⚠️ Partial | Services exist but are tightly coupled |
| **Error Handling** | ✅ Good | Centralized ErrorHandler, AppError classes |
| **Validation** | ✅ Good | InputValidator utility with clear interfaces |
| **IPC Communication** | ✅ Good | Well-defined IPC handlers in main.ts |
| **TypeScript** | ✅ Excellent | Strong typing throughout |

### ❌ What Needs Improvement

| Issue | Impact | Priority |
|-------|--------|----------|
| **Hard-coded Dependencies** | High | 🔴 CRITICAL |
| **No DI Container** | High | 🔴 CRITICAL |
| **Singleton Services** | Medium | 🟡 HIGH |
| **Scattered Configuration** | Medium | 🟡 HIGH |
| **No Plugin System** | Low | 🟢 MEDIUM |
| **Tight Coupling** | High | 🔴 CRITICAL |

**Examples of Tight Coupling:**
```typescript
// ❌ BAD: Hard-coded dependency in InterviewApp.tsx
const service = new InterviewService(); // <-- Direct instantiation

// ❌ BAD: Hard-coded Ollama URL in interview-service.ts
constructor(baseURL = 'http://localhost:11434') {
  this.baseURL = baseURL; // <-- Configuration hard-coded
}

// ❌ BAD: No way to swap implementations
// What if we want MockInterviewService for testing?
```

---

## 🏗️ Target Modular Architecture

### 1. Core Principles

#### 1.1 SOLID Principles
- **S**ingle Responsibility: Each module does ONE thing
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Interfaces are swappable
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concrete implementations

#### 1.2 Module Boundaries
```
┌─────────────────────────────────────────────────────────────┐
│                     Desktop Application                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Presentation (React Components)                   │
│  ├─ Interview UI                                            │
│  ├─ Testimonial Form                                        │
│  └─ Settings UI                                             │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Application Services (Business Logic)             │
│  ├─ InterviewModule (orchestrates interview flow)           │
│  ├─ TestimonialModule (manages testimonials)                │
│  ├─ SettingsModule (configuration management)               │
│  └─ AvatarModule (avatar rendering & animation)             │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Infrastructure (External Integrations)            │
│  ├─ AIProvider (Ollama adapter)                             │
│  ├─ StorageProvider (database/filesystem)                   │
│  ├─ VoiceProvider (microphone/TTS)                          │
│  └─ TranscriptionProvider (speech-to-text)                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Core Utilities                                    │
│  ├─ DI Container (dependency injection)                     │
│  ├─ Event Bus (inter-module communication)                  │
│  ├─ Config Manager (centralized configuration)              │
│  └─ Logger (structured logging)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Module Specifications

### Module 1: Core DI Container

**Purpose:** Centralized dependency management and inversion of control.

**New Files:**
```
src/core/
├── di-container.ts          # Dependency injection container
├── interfaces.ts            # Core interfaces for all modules
├── types.ts                 # Shared types
└── __tests__/
    └── di-container.test.ts
```

**Implementation:**
```typescript
// src/core/di-container.ts
export class DIContainer {
  private services = new Map<string, any>();
  private factories = new Map<string, () => any>();
  
  register<T>(key: string, factory: () => T): void {
    this.factories.set(key, factory);
  }
  
  registerSingleton<T>(key: string, instance: T): void {
    this.services.set(key, instance);
  }
  
  resolve<T>(key: string): T {
    if (this.services.has(key)) {
      return this.services.get(key);
    }
    
    const factory = this.factories.get(key);
    if (!factory) {
      throw new Error(`Service not registered: ${key}`);
    }
    
    const instance = factory();
    this.services.set(key, instance);
    return instance;
  }
  
  clear(): void {
    this.services.clear();
    this.factories.clear();
  }
}

export const container = new DIContainer();
```

**Usage:**
```typescript
// Register services at app startup
container.register('AIProvider', () => new OllamaProvider(config));
container.register('InterviewService', () => 
  new InterviewService(container.resolve('AIProvider'))
);

// Resolve in components
const interviewService = container.resolve<InterviewService>('InterviewService');
```

---

### Module 2: Configuration Management

**Purpose:** Centralized, type-safe configuration for all modules.

**New Files:**
```
src/core/
├── config-manager.ts        # Configuration management
├── config-schema.ts         # Zod schemas for validation
└── __tests__/
    └── config-manager.test.ts
```

**Implementation:**
```typescript
// src/core/config-schema.ts
import { z } from 'zod';

export const AppConfigSchema = z.object({
  ai: z.object({
    provider: z.enum(['ollama', 'openai', 'mock']),
    ollama: z.object({
      baseURL: z.string().url(),
      defaultModel: z.string(),
      timeout: z.number().positive(),
    }),
  }),
  storage: z.object({
    provider: z.enum(['sqlite', 'indexeddb']),
    path: z.string().optional(),
  }),
  voice: z.object({
    enabled: z.boolean(),
    sampleRate: z.number().positive(),
  }),
  avatar: z.object({
    enabled: z.boolean(),
    quality: z.enum(['low', 'medium', 'high']),
  }),
  interview: z.object({
    defaultRole: z.string(),
    defaultQuestions: z.number().int().positive(),
  }),
});

export type AppConfig = z.infer<typeof AppConfigSchema>;
```

```typescript
// src/core/config-manager.ts
import { AppConfig, AppConfigSchema } from './config-schema';

export class ConfigManager {
  private config: AppConfig;
  
  constructor(initialConfig: Partial<AppConfig> = {}) {
    const defaultConfig = this.getDefaultConfig();
    const merged = { ...defaultConfig, ...initialConfig };
    this.config = AppConfigSchema.parse(merged);
  }
  
  get<K extends keyof AppConfig>(key: K): AppConfig[K] {
    return this.config[key];
  }
  
  set<K extends keyof AppConfig>(key: K, value: AppConfig[K]): void {
    this.config[key] = value;
  }
  
  getAll(): AppConfig {
    return { ...this.config };
  }
  
  private getDefaultConfig(): AppConfig {
    return {
      ai: {
        provider: 'ollama',
        ollama: {
          baseURL: 'http://localhost:11434',
          defaultModel: 'granite-code:3b',
          timeout: 60000,
        },
      },
      storage: {
        provider: 'sqlite',
      },
      voice: {
        enabled: true,
        sampleRate: 16000,
      },
      avatar: {
        enabled: true,
        quality: 'medium',
      },
      interview: {
        defaultRole: 'Software Engineer',
        defaultQuestions: 5,
      },
    };
  }
}
```

---

### Module 3: Interface-Based Providers

**Purpose:** Abstract external dependencies with interfaces.

**New Files:**
```
src/providers/
├── interfaces.ts            # Provider interfaces
├── ai/
│   ├── ai-provider.interface.ts
│   ├── ollama-provider.ts   # Ollama implementation
│   ├── mock-provider.ts     # Mock for testing
│   └── __tests__/
│       └── ollama-provider.test.ts
├── storage/
│   ├── storage-provider.interface.ts
│   ├── sqlite-provider.ts
│   └── indexeddb-provider.ts
├── voice/
│   ├── voice-provider.interface.ts
│   └── web-audio-provider.ts
└── transcription/
    ├── transcription-provider.interface.ts
    └── whisper-provider.ts
```

**AI Provider Interface:**
```typescript
// src/providers/ai/ai-provider.interface.ts
export interface AIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface AIResponse {
  message: AIMessage;
  model: string;
  metadata?: {
    tokens?: number;
    latency?: number;
  };
}

export interface AIProvider {
  /**
   * Send a chat completion request
   */
  chat(messages: AIMessage[], model: string): Promise<AIResponse>;
  
  /**
   * List available models
   */
  listModels(): Promise<string[]>;
  
  /**
   * Check if the provider is healthy
   */
  checkHealth(): Promise<boolean>;
  
  /**
   * Get provider name
   */
  getName(): string;
}
```

**Ollama Provider Implementation:**
```typescript
// src/providers/ai/ollama-provider.ts
import axios, { AxiosInstance } from 'axios';
import { AIProvider, AIMessage, AIResponse } from './ai-provider.interface';

export interface OllamaConfig {
  baseURL: string;
  timeout: number;
}

export class OllamaProvider implements AIProvider {
  private client: AxiosInstance;
  private config: OllamaConfig;
  
  constructor(config: OllamaConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
    });
  }
  
  async chat(messages: AIMessage[], model: string): Promise<AIResponse> {
    const response = await this.client.post('/api/chat', {
      model,
      messages,
      stream: false,
    });
    
    return {
      message: response.data.message,
      model,
      metadata: {
        tokens: response.data.eval_count,
        latency: response.data.total_duration,
      },
    };
  }
  
  async listModels(): Promise<string[]> {
    const response = await this.client.get('/api/tags');
    return response.data.models?.map((m: any) => m.name) || [];
  }
  
  async checkHealth(): Promise<boolean> {
    try {
      await this.client.get('/api/tags');
      return true;
    } catch {
      return false;
    }
  }
  
  getName(): string {
    return 'Ollama';
  }
}
```

**Mock Provider (for testing):**
```typescript
// src/providers/ai/mock-provider.ts
export class MockAIProvider implements AIProvider {
  async chat(messages: AIMessage[]): Promise<AIResponse> {
    return {
      message: {
        role: 'assistant',
        content: 'Mock response for testing',
      },
      model: 'mock-model',
    };
  }
  
  async listModels(): Promise<string[]> {
    return ['mock-model-1', 'mock-model-2'];
  }
  
  async checkHealth(): Promise<boolean> {
    return true;
  }
  
  getName(): string {
    return 'Mock';
  }
}
```

---

### Module 4: Application Modules

**Purpose:** High-level business logic modules that orchestrate providers.

**New Files:**
```
src/modules/
├── interview/
│   ├── interview.module.ts      # Interview orchestration
│   ├── interview.service.ts     # Refactored service
│   ├── interview.types.ts       # Types
│   └── __tests__/
│       └── interview.module.test.ts
├── testimonial/
│   ├── testimonial.module.ts
│   ├── testimonial.service.ts
│   └── testimonial.types.ts
├── settings/
│   ├── settings.module.ts
│   └── settings.service.ts
└── avatar/
    ├── avatar.module.ts
    └── avatar.service.ts
```

**Interview Module:**
```typescript
// src/modules/interview/interview.module.ts
import { AIProvider } from '../../providers/ai/ai-provider.interface';
import { ConfigManager } from '../../core/config-manager';
import { EventBus } from '../../core/event-bus';

export class InterviewModule {
  constructor(
    private aiProvider: AIProvider,
    private config: ConfigManager,
    private eventBus: EventBus
  ) {}
  
  async startInterview(role: string, model?: string): Promise<InterviewSession> {
    // Emit event
    this.eventBus.emit('interview:started', { role, model });
    
    // Use config for defaults
    const interviewModel = model || this.config.get('interview').defaultRole;
    
    // Delegate to AI provider
    const response = await this.aiProvider.chat(
      [
        { role: 'system', content: this.getPrompt(role) },
        { role: 'user', content: 'Start interview' }
      ],
      interviewModel
    );
    
    return {
      role,
      model: interviewModel,
      messages: [response.message],
      currentQuestion: 1,
      isComplete: false,
    };
  }
  
  private getPrompt(role: string): string {
    // Prompt logic here
  }
}
```

---

### Module 5: Event Bus

**Purpose:** Decouple modules via event-driven communication.

**New Files:**
```
src/core/
├── event-bus.ts
├── event-types.ts
└── __tests__/
    └── event-bus.test.ts
```

**Implementation:**
```typescript
// src/core/event-types.ts
export interface EventMap {
  'interview:started': { role: string; model: string };
  'interview:question-answered': { question: number; answer: string };
  'interview:completed': { totalQuestions: number };
  'ai:error': { error: Error; context: string };
  'config:updated': { key: string; value: any };
}

// src/core/event-bus.ts
export class EventBus {
  private listeners = new Map<string, Array<(data: any) => void>>();
  
  on<K extends keyof EventMap>(event: K, listener: (data: EventMap[K]) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(listener);
  }
  
  emit<K extends keyof EventMap>(event: K, data: EventMap[K]): void {
    const handlers = this.listeners.get(event) || [];
    handlers.forEach(handler => handler(data));
  }
  
  off<K extends keyof EventMap>(event: K, listener: (data: EventMap[K]) => void): void {
    const handlers = this.listeners.get(event) || [];
    this.listeners.set(
      event,
      handlers.filter(h => h !== listener)
    );
  }
}
```

---

### Module 6: Plugin System (Optional)

**Purpose:** Allow third-party extensions and custom modules.

**New Files:**
```
src/core/
├── plugin-manager.ts
├── plugin.interface.ts
└── __tests__/
    └── plugin-manager.test.ts
```

**Plugin Interface:**
```typescript
// src/core/plugin.interface.ts
export interface Plugin {
  name: string;
  version: string;
  
  /**
   * Called when plugin is loaded
   */
  onLoad(app: Application): void;
  
  /**
   * Called when plugin is unloaded
   */
  onUnload(): void;
}

// Example: Custom AI provider plugin
export class CustomAIPlugin implements Plugin {
  name = 'custom-ai-provider';
  version = '1.0.0';
  
  onLoad(app: Application) {
    app.container.register('AIProvider', () => new CustomAIProvider());
  }
  
  onUnload() {
    // Cleanup
  }
}
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Infrastructure (Day 1 - 4 hours)
**Target:** December 12, Morning

**Tasks:**
- [ ] Create `src/core/` directory
- [ ] Implement DI Container (`di-container.ts`)
- [ ] Write tests for DI Container
- [ ] Implement Config Manager (`config-manager.ts`)
- [ ] Create config schemas with Zod
- [ ] Write tests for Config Manager
- [ ] Implement Event Bus (`event-bus.ts`)
- [ ] Write tests for Event Bus

**Deliverables:**
- ✅ DI Container working with registration/resolution
- ✅ Config Manager with type-safe configuration
- ✅ Event Bus for inter-module communication
- ✅ 100% test coverage for core utilities

**Verification:**
```bash
npm test src/core/__tests__
```

---

### Phase 2: Provider Interfaces (Day 1 - 4 hours)
**Target:** December 12, Afternoon

**Tasks:**
- [ ] Create `src/providers/` directory structure
- [ ] Define AI Provider interface
- [ ] Refactor Ollama integration to OllamaProvider
- [ ] Create MockAIProvider for testing
- [ ] Define Storage Provider interface
- [ ] Implement SQLite Provider
- [ ] Define Voice Provider interface
- [ ] Write tests for all providers

**Deliverables:**
- ✅ `AIProvider` interface with Ollama + Mock implementations
- ✅ `StorageProvider` interface with SQLite implementation
- ✅ `VoiceProvider` interface with WebAudio implementation
- ✅ 90%+ test coverage for providers

**Verification:**
```bash
npm test src/providers/__tests__
```

---

### Phase 3: Module Refactoring (Day 2 - 6 hours)
**Target:** December 13, Full Day

**Tasks:**
- [ ] Create `src/modules/` directory
- [ ] Refactor InterviewService → InterviewModule
  - [ ] Remove hard-coded dependencies
  - [ ] Inject AIProvider via constructor
  - [ ] Use ConfigManager for configuration
  - [ ] Emit events via EventBus
- [ ] Refactor TestimonialDatabase → TestimonialModule
- [ ] Refactor AvatarRenderer → AvatarModule
- [ ] Create SettingsModule for configuration UI
- [ ] Write integration tests for modules

**Deliverables:**
- ✅ All services refactored to use DI
- ✅ No hard-coded dependencies
- ✅ Event-driven communication between modules
- ✅ Integration tests passing

**Verification:**
```bash
npm test src/modules/__tests__
npm run test:integration
```

---

### Phase 4: Application Bootstrap (Day 2 - 2 hours)
**Target:** December 13, Evening

**Tasks:**
- [ ] Create `src/app.ts` (application entry point)
- [ ] Register all services in DI container
- [ ] Load configuration from file/environment
- [ ] Initialize all modules
- [ ] Set up event listeners
- [ ] Update main.ts to use app.ts
- [ ] Update renderer to use DI container

**Deliverables:**
- ✅ `src/app.ts` with complete application setup
- ✅ All modules initialized via DI
- ✅ Configuration loaded from file
- ✅ Application starts successfully

**Code Example:**
```typescript
// src/app.ts
export class Application {
  public container: DIContainer;
  public config: ConfigManager;
  public eventBus: EventBus;
  
  constructor() {
    this.container = new DIContainer();
    this.config = new ConfigManager();
    this.eventBus = new EventBus();
    
    this.registerCore();
    this.registerProviders();
    this.registerModules();
    this.setupEventListeners();
  }
  
  private registerCore() {
    this.container.registerSingleton('ConfigManager', this.config);
    this.container.registerSingleton('EventBus', this.eventBus);
  }
  
  private registerProviders() {
    const aiConfig = this.config.get('ai').ollama;
    this.container.register('AIProvider', () => 
      new OllamaProvider(aiConfig)
    );
    
    this.container.register('StorageProvider', () =>
      new SQLiteProvider(this.config.get('storage'))
    );
  }
  
  private registerModules() {
    this.container.register('InterviewModule', () =>
      new InterviewModule(
        this.container.resolve('AIProvider'),
        this.config,
        this.eventBus
      )
    );
  }
  
  private setupEventListeners() {
    this.eventBus.on('ai:error', (data) => {
      console.error('[AI Error]', data.error);
    });
  }
}
```

---

### Phase 5: UI Integration (Day 3 - 4 hours)
**Target:** December 14, Morning

**Tasks:**
- [ ] Create React Context for DI Container
- [ ] Create custom hooks for services
  - [ ] `useInterview()` → resolves InterviewModule
  - [ ] `useTestimonial()` → resolves TestimonialModule
  - [ ] `useConfig()` → resolves ConfigManager
- [ ] Refactor InterviewApp.tsx to use hooks
- [ ] Refactor TestimonialForm.tsx to use hooks
- [ ] Remove all hard-coded service instantiation

**Deliverables:**
- ✅ React Context with DI Container
- ✅ Custom hooks for all modules
- ✅ All components use hooks instead of direct instantiation
- ✅ UI works end-to-end with new architecture

**Code Example:**
```typescript
// src/renderer/AppContext.tsx
const AppContext = createContext<Application | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const app = useMemo(() => new Application(), []);
  return <AppContext.Provider value={app}>{children}</AppContext.Provider>;
}

export function useApp(): Application {
  const app = useContext(AppContext);
  if (!app) throw new Error('useApp must be used within AppProvider');
  return app;
}

export function useInterview() {
  const app = useApp();
  return app.container.resolve<InterviewModule>('InterviewModule');
}
```

**Usage:**
```typescript
// src/renderer/InterviewApp.tsx (refactored)
function InterviewApp() {
  const interviewModule = useInterview();
  const [session, setSession] = useState<InterviewSession | null>(null);
  
  const startInterview = async () => {
    const newSession = await interviewModule.startInterview('Software Engineer');
    setSession(newSession);
  };
  
  // ... rest of component
}
```

---

### Phase 6: Testing & Documentation (Day 3 - 4 hours)
**Target:** December 14, Afternoon

**Tasks:**
- [ ] Write end-to-end tests with new architecture
- [ ] Update README.md with architecture diagram
- [ ] Create ARCHITECTURE.md documentation
- [ ] Document each module's purpose and API
- [ ] Create migration guide for developers
- [ ] Run full test suite
- [ ] Fix any regressions

**Deliverables:**
- ✅ E2E tests passing
- ✅ Architecture documentation complete
- ✅ All modules documented
- ✅ Migration guide for future developers
- ✅ Zero regressions from refactoring

---

### Phase 7: Plugin System (Optional - Day 4)
**Target:** December 15 (if time permits)

**Tasks:**
- [ ] Implement Plugin Manager
- [ ] Create plugin lifecycle hooks
- [ ] Create example plugin (custom AI provider)
- [ ] Document plugin development guide
- [ ] Test plugin loading/unloading

**Deliverables:**
- ✅ Plugin system working
- ✅ Example plugin demonstrating extensibility
- ✅ Plugin development guide

---

## 📁 Final Directory Structure

```
desktop-app/
├── src/
│   ├── core/                         # Core infrastructure
│   │   ├── di-container.ts           # Dependency injection
│   │   ├── config-manager.ts         # Configuration management
│   │   ├── config-schema.ts          # Zod schemas
│   │   ├── event-bus.ts              # Event-driven communication
│   │   ├── event-types.ts            # Type-safe events
│   │   ├── plugin-manager.ts         # Plugin system (optional)
│   │   ├── plugin.interface.ts       # Plugin interface
│   │   ├── logger.ts                 # Structured logging
│   │   └── __tests__/
│   │       ├── di-container.test.ts
│   │       ├── config-manager.test.ts
│   │       └── event-bus.test.ts
│   │
│   ├── providers/                    # External integrations (adapters)
│   │   ├── ai/
│   │   │   ├── ai-provider.interface.ts
│   │   │   ├── ollama-provider.ts    # Ollama implementation
│   │   │   ├── mock-provider.ts      # Mock for testing
│   │   │   └── __tests__/
│   │   ├── storage/
│   │   │   ├── storage-provider.interface.ts
│   │   │   ├── sqlite-provider.ts
│   │   │   ├── indexeddb-provider.ts
│   │   │   └── __tests__/
│   │   ├── voice/
│   │   │   ├── voice-provider.interface.ts
│   │   │   ├── web-audio-provider.ts
│   │   │   └── __tests__/
│   │   └── transcription/
│   │       ├── transcription-provider.interface.ts
│   │       ├── whisper-provider.ts
│   │       └── __tests__/
│   │
│   ├── modules/                      # Application modules (business logic)
│   │   ├── interview/
│   │   │   ├── interview.module.ts   # Main module
│   │   │   ├── interview.service.ts  # Refactored service
│   │   │   ├── interview.types.ts    # Types
│   │   │   ├── prompts.ts            # Interview prompts
│   │   │   └── __tests__/
│   │   ├── testimonial/
│   │   │   ├── testimonial.module.ts
│   │   │   ├── testimonial.service.ts
│   │   │   ├── testimonial.types.ts
│   │   │   └── __tests__/
│   │   ├── settings/
│   │   │   ├── settings.module.ts
│   │   │   ├── settings.service.ts
│   │   │   └── __tests__/
│   │   └── avatar/
│   │       ├── avatar.module.ts
│   │       ├── avatar.service.ts
│   │       └── __tests__/
│   │
│   ├── main/                         # Electron main process
│   │   ├── main.ts                   # Main entry point
│   │   ├── hardware.ts               # Hardware detection
│   │   ├── recommender.ts            # Model recommendation
│   │   └── config.ts                 # Config file I/O
│   │
│   ├── preload/                      # Electron preload
│   │   └── preload.ts                # IPC bridge
│   │
│   ├── renderer/                     # React UI
│   │   ├── App.tsx                   # Root component
│   │   ├── AppContext.tsx            # DI Context for React
│   │   ├── InterviewApp.tsx          # Interview UI (refactored)
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useInterview.ts
│   │   │   ├── useTestimonial.ts
│   │   │   ├── useConfig.ts
│   │   │   └── useAvatar.ts
│   │   └── ui/                       # UI components
│   │
│   ├── components/                   # Shared React components
│   │   ├── AvatarDisplay.tsx
│   │   ├── TestimonialForm.tsx       # (refactored)
│   │   ├── ErrorBoundary.tsx
│   │   └── LoadingSpinner.tsx
│   │
│   ├── utils/                        # Utilities (unchanged)
│   │   ├── error-handler.ts
│   │   └── validation.ts
│   │
│   ├── app.ts                        # Application bootstrap
│   └── index.tsx                     # React entry point
│
├── config/                           # Configuration files
│   ├── default.json                  # Default config
│   ├── development.json              # Dev overrides
│   └── production.json               # Prod overrides
│
├── ARCHITECTURE.md                   # Architecture documentation
├── MODULAR_ARCHITECTURE_PLAN.md      # This file
└── package.json
```

---

## 🧪 Testing Strategy

### Unit Tests
**Target Coverage:** 90%+

```typescript
// Example: DI Container test
describe('DIContainer', () => {
  it('should resolve registered services', () => {
    const container = new DIContainer();
    container.register('TestService', () => ({ name: 'test' }));
    
    const service = container.resolve('TestService');
    expect(service.name).toBe('test');
  });
  
  it('should throw error for unregistered services', () => {
    const container = new DIContainer();
    expect(() => container.resolve('Unknown')).toThrow();
  });
});
```

### Integration Tests
```typescript
// Example: Interview Module integration test
describe('InterviewModule Integration', () => {
  let app: Application;
  
  beforeEach(() => {
    app = new Application();
    // Use mock provider for testing
    app.container.register('AIProvider', () => new MockAIProvider());
  });
  
  it('should start interview with AI provider', async () => {
    const interviewModule = app.container.resolve<InterviewModule>('InterviewModule');
    const session = await interviewModule.startInterview('Software Engineer');
    
    expect(session.role).toBe('Software Engineer');
    expect(session.messages.length).toBeGreaterThan(0);
  });
});
```

### E2E Tests
```typescript
// Example: Full interview flow
describe('Interview E2E', () => {
  it('should complete full interview flow', async () => {
    const app = new Application();
    const interviewModule = app.container.resolve<InterviewModule>('InterviewModule');
    
    // Start interview
    const session = await interviewModule.startInterview('Software Engineer');
    expect(session.currentQuestion).toBe(1);
    
    // Answer questions
    let updatedSession = session;
    for (let i = 0; i < 5; i++) {
      updatedSession = await interviewModule.sendResponse(
        updatedSession,
        'Sample answer'
      );
    }
    
    expect(updatedSession.isComplete).toBe(true);
  });
});
```

---

## 📊 Benefits of Modular Architecture

### For Development

| Benefit | Before | After |
|---------|--------|-------|
| **Testability** | Hard to mock dependencies | Easy to inject mocks |
| **Maintainability** | Scattered logic | Clear module boundaries |
| **Extensibility** | Hard-coded integrations | Plugin system |
| **Onboarding** | Unclear architecture | Well-documented modules |
| **Debugging** | Tight coupling | Isolated modules |

### For Business

| Benefit | Impact |
|---------|--------|
| **Faster Feature Development** | New features = new modules, no refactoring |
| **Easier Testing** | 90%+ coverage → fewer bugs → happier users |
| **Third-Party Integrations** | Plugin system → community contributions |
| **Technical Debt Reduction** | Clean architecture → sustainable growth |
| **Hiring** | Well-structured code → easier to onboard developers |

---

## 🚨 Risk Mitigation

### Risk 1: Breaking Changes During Refactoring
**Mitigation:**
- Comprehensive test suite before refactoring
- Parallel implementation (keep old code until new code verified)
- Feature flags for gradual rollout

### Risk 2: Over-Engineering
**Mitigation:**
- Only implement what's needed for current requirements
- Skip plugin system if not needed immediately
- Keep it simple: DI + Interfaces + Modules = 80% of benefits

### Risk 3: Timeline Pressure (SelectUSA Deadline)
**Mitigation:**
- Focus on Phases 1-4 (critical)
- Phase 5 (UI) can be iterative
- Phase 6 (docs) can be done post-demo
- Phase 7 (plugins) is optional

---

## ✅ Success Criteria

### Technical Metrics
- [ ] 90%+ test coverage
- [ ] Zero hard-coded dependencies
- [ ] All services use DI container
- [ ] All external integrations use interfaces
- [ ] Event-driven communication between modules
- [ ] Configuration centralized and type-safe

### Functional Metrics
- [ ] App starts successfully with new architecture
- [ ] All existing features work (interview, testimonials, avatar)
- [ ] UI integration complete (React Context + hooks)
- [ ] No performance regression (latency, memory usage)

### Documentation Metrics
- [ ] ARCHITECTURE.md complete
- [ ] All modules documented
- [ ] Migration guide for developers
- [ ] Plugin development guide (if Phase 7 complete)

---

## 📅 Timeline Summary

| Phase | Date | Duration | Status |
|-------|------|----------|--------|
| Phase 1: Core Infrastructure | Dec 12 AM | 4 hours | ⏳ NEXT |
| Phase 2: Provider Interfaces | Dec 12 PM | 4 hours | ⏳ NEXT |
| Phase 3: Module Refactoring | Dec 13 | 6 hours | 📋 PLANNED |
| Phase 4: Application Bootstrap | Dec 13 PM | 2 hours | 📋 PLANNED |
| Phase 5: UI Integration | Dec 14 AM | 4 hours | 📋 PLANNED |
| Phase 6: Testing & Docs | Dec 14 PM | 4 hours | 📋 PLANNED |
| Phase 7: Plugin System | Dec 15 | 8 hours | 🟢 OPTIONAL |

**Total Time:** 24-32 hours (3-4 days)  
**Deadline:** December 15 (aligns with SelectUSA Days 3-6)

---

## 🎯 Next Steps

**Immediate Actions (Next 1 Hour):**
1. ✅ Review this plan with team
2. ✅ Create `src/core/` directory
3. ✅ Install dependencies: `npm install zod` (for config validation)
4. ✅ Start Phase 1: Implement DI Container
5. ✅ Write first test for DI Container

**Commands to Execute:**
```bash
# Create directory structure
mkdir -p src/core src/core/__tests__
mkdir -p src/providers/ai src/providers/storage src/providers/voice
mkdir -p src/modules/interview src/modules/testimonial

# Install dependencies
npm install zod  # For config validation

# Start development
npm run dev
```

---

**Let's build a world-class modular architecture! 🚀**

