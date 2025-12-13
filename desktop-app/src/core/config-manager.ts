import { AppConfig, AppConfigSchema } from './config-schema';

function isPlainObject(value: unknown): value is Record<string, any> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function deepMerge<T extends Record<string, any>>(base: T, override: Partial<T>): T {
  const result: Record<string, any> = { ...base };
  for (const key of Object.keys(override)) {
    const oVal = (override as any)[key];
    const bVal = (base as any)[key];
    if (isPlainObject(bVal) && isPlainObject(oVal)) {
      result[key] = deepMerge(bVal, oVal);
    } else if (oVal !== undefined) {
      result[key] = oVal;
    }
  }
  return result as T;
}

export class ConfigManager {
  private config: AppConfig;

  constructor(initialConfig: Partial<AppConfig> = {}) {
    const defaults = this.getDefaultConfig();
    const merged = deepMerge(defaults, initialConfig);
    this.config = AppConfigSchema.parse(merged);
  }

  get<K extends keyof AppConfig>(key: K): AppConfig[K] {
    return this.config[key];
  }

  set<K extends keyof AppConfig>(key: K, value: AppConfig[K]): void {
    (this.config as any)[key] = value;
  }

  getAll(): AppConfig {
    return JSON.parse(JSON.stringify(this.config));
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
