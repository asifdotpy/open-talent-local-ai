# Modularization Quick Start Guide

> **Goal:** Transform desktop app into highly modular architecture in 3-4 days  
> **Timeline:** Dec 12-15 (aligns with SelectUSA Days 3-6)  
> **Status:** 🟢 Ready to Start

---

## 📊 Current State Assessment

### ✅ What's Already Good
- Clear directory structure (main/renderer/services)
- TypeScript with strong typing
- Centralized error handling
- IPC communication well-defined

### ❌ What Needs Fixing
- **Hard-coded dependencies** - Services directly instantiated (e.g., `new InterviewService()`)
- **No dependency injection** - Cannot swap implementations for testing
- **Scattered configuration** - URLs, timeouts hard-coded
- **Tight coupling** - Components depend on concrete classes, not interfaces

---

## 🎯 Modular Architecture Goals

### Before (Current)
```typescript
// ❌ Hard-coded dependency
const service = new InterviewService();
service.startInterview('Software Engineer');
```

### After (Modular)
```typescript
// ✅ Dependency injection
const interviewModule = container.resolve<InterviewModule>('InterviewModule');
interviewModule.startInterview('Software Engineer');

// ✅ Easy to swap for testing
container.register('AIProvider', () => new MockAIProvider()); // No Ollama needed!
```

---

## 🚀 Implementation Phases

### Phase 1: Core Infrastructure (4 hours) - Dec 12 AM
**What:** Build foundation (DI Container, Config Manager, Event Bus)

**Files to Create:**
```
src/core/di-container.ts          # Dependency injection
src/core/config-manager.ts        # Centralized config
src/core/config-schema.ts         # Zod validation
src/core/event-bus.ts             # Event system
```

**Quick Start:**
```bash
# 1. Create directories
mkdir -p src/core src/core/__tests__

# 2. Install dependencies
npm install zod

# 3. Start coding
# Copy code from MODULAR_ARCHITECTURE_PLAN.md Phase 1
```

**Test:**
```bash
npm test src/core/__tests__/di-container.test.ts
```

---

### Phase 2: Provider Interfaces (4 hours) - Dec 12 PM
**What:** Abstract Ollama, Storage, Voice behind interfaces

**Files to Create:**
```
src/providers/ai/ai-provider.interface.ts
src/providers/ai/ollama-provider.ts
src/providers/ai/mock-provider.ts
```

**Quick Start:**
```bash
# 1. Create directories
mkdir -p src/providers/ai src/providers/storage src/providers/voice

# 2. Define interfaces
# Copy AIProvider interface from plan

# 3. Refactor Ollama code
# Move from interview-service.ts to ollama-provider.ts
```

**Test:**
```bash
npm test src/providers/__tests__/ollama-provider.test.ts
```

---

### Phase 3: Refactor Services (6 hours) - Dec 13
**What:** Convert services to modules with DI

**Files to Refactor:**
```
src/services/interview-service.ts → src/modules/interview/interview.module.ts
src/services/testimonial-database.ts → src/modules/testimonial/testimonial.module.ts
```

**Quick Start:**
```bash
# 1. Create module directories
mkdir -p src/modules/interview src/modules/testimonial

# 2. Refactor InterviewService
# Remove hard-coded dependencies
# Inject AIProvider via constructor
```

**Before:**
```typescript
export class InterviewService {
  constructor(baseURL = 'http://localhost:11434') {
    this.client = axios.create({ baseURL });
  }
}
```

**After:**
```typescript
export class InterviewModule {
  constructor(
    private aiProvider: AIProvider,
    private config: ConfigManager
  ) {}
  
  async startInterview(role: string) {
    const response = await this.aiProvider.chat(messages, model);
    // ...
  }
}
```

---

### Phase 4: App Bootstrap (2 hours) - Dec 13 PM
**What:** Create app.ts to wire everything together

**Files to Create:**
```
src/app.ts  # Main application class
```

**Code:**
```typescript
export class Application {
  public container = new DIContainer();
  public config = new ConfigManager();
  public eventBus = new EventBus();
  
  constructor() {
    this.registerCore();
    this.registerProviders();
    this.registerModules();
  }
  
  private registerProviders() {
    this.container.register('AIProvider', () => 
      new OllamaProvider(this.config.get('ai').ollama)
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
}
```

---

### Phase 5: React Integration (4 hours) - Dec 14 AM
**What:** Update React components to use DI

**Files to Create:**
```
src/renderer/AppContext.tsx
src/renderer/hooks/useInterview.ts
```

**Quick Start:**
```typescript
// AppContext.tsx
const AppContext = createContext<Application | null>(null);

export function AppProvider({ children }) {
  const app = useMemo(() => new Application(), []);
  return <AppContext.Provider value={app}>{children}</AppContext.Provider>;
}

export function useInterview() {
  const app = useContext(AppContext);
  return app.container.resolve<InterviewModule>('InterviewModule');
}
```

**Refactor InterviewApp.tsx:**
```typescript
// Before
const service = new InterviewService();

// After
const interviewModule = useInterview();
```

---

### Phase 6: Testing (4 hours) - Dec 14 PM
**What:** Verify everything works, write tests

**Tasks:**
- [ ] Run full test suite
- [ ] Fix any regressions
- [ ] Write E2E tests
- [ ] Document architecture

---

## 📁 Final Directory Structure

```
src/
├── core/                    # ⭐ NEW: Core infrastructure
│   ├── di-container.ts
│   ├── config-manager.ts
│   ├── event-bus.ts
│   └── __tests__/
├── providers/              # ⭐ NEW: External integrations
│   ├── ai/
│   │   ├── ai-provider.interface.ts
│   │   ├── ollama-provider.ts
│   │   └── mock-provider.ts
│   ├── storage/
│   └── voice/
├── modules/                # ⭐ NEW: Business logic
│   ├── interview/
│   │   └── interview.module.ts
│   ├── testimonial/
│   └── avatar/
├── renderer/
│   ├── AppContext.tsx      # ⭐ NEW: DI Context
│   ├── hooks/              # ⭐ NEW: Custom hooks
│   └── InterviewApp.tsx    # 🔄 REFACTORED
├── main/                   # ✅ Minimal changes
├── services/               # ⚠️ DEPRECATED (move to modules/)
└── app.ts                  # ⭐ NEW: App bootstrap
```

---

## 🎯 Key Benefits

### Testability
```typescript
// Before: Can't test without running Ollama
const service = new InterviewService();
await service.startInterview('Software Engineer'); // ❌ Requires Ollama

// After: Easy mocking
container.register('AIProvider', () => new MockAIProvider());
const module = container.resolve<InterviewModule>('InterviewModule');
await module.startInterview('Software Engineer'); // ✅ Works offline!
```

### Flexibility
```typescript
// Switch AI providers without changing code
if (isDevelopment) {
  container.register('AIProvider', () => new MockAIProvider());
} else {
  container.register('AIProvider', () => new OllamaProvider(config));
}
```

### Configuration
```typescript
// Before: Hard-coded everywhere
const client = axios.create({ baseURL: 'http://localhost:11434' });

// After: Centralized
const config = configManager.get('ai').ollama.baseURL;
```

---

## ✅ Success Checklist

### Phase 1 ✓
- [ ] DI Container implemented and tested
- [ ] Config Manager with Zod validation
- [ ] Event Bus working

### Phase 2 ✓
- [ ] AIProvider interface defined
- [ ] OllamaProvider implemented
- [ ] MockAIProvider for testing

### Phase 3 ✓
- [ ] InterviewService → InterviewModule
- [ ] No hard-coded dependencies
- [ ] All services use DI

### Phase 4 ✓
- [ ] app.ts created
- [ ] All modules registered
- [ ] App starts successfully

### Phase 5 ✓
- [ ] React Context created
- [ ] Custom hooks implemented
- [ ] Components refactored

### Phase 6 ✓
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Zero regressions

---

## 🚨 Common Pitfalls

### Pitfall 1: Over-engineering
**Symptom:** Spending too much time on abstractions  
**Solution:** Keep it simple - DI + Interfaces = 80% of benefits

### Pitfall 2: Breaking existing features
**Symptom:** App doesn't start after refactoring  
**Solution:** Refactor incrementally, test after each change

### Pitfall 3: Not testing enough
**Symptom:** Bugs appear after modularization  
**Solution:** Write tests FIRST, then refactor

---

## 📚 Resources

- **Full Plan:** [MODULAR_ARCHITECTURE_PLAN.md](MODULAR_ARCHITECTURE_PLAN.md)
- **DI Pattern:** Martin Fowler's "Inversion of Control Containers"
- **Event Bus:** Observer pattern (Gang of Four)
- **Config Management:** 12-Factor App methodology

---

## 🏁 Getting Started NOW

```bash
# 1. Review this guide
cat MODULARIZATION_QUICKSTART.md

# 2. Review full plan
cat MODULAR_ARCHITECTURE_PLAN.md

# 3. Start Phase 1
mkdir -p src/core src/core/__tests__
npm install zod

# 4. Copy code from plan and start coding!
```

**Next File to Create:** `src/core/di-container.ts`

---

**Let's make OpenTalent world-class! 🚀**
