import { promises as fs } from 'fs';
import path from 'path';

export interface AppConfig<THardware = unknown> {
  selectedModel?: string;
  hardwareProfile?: THardware;
}

/**
 * Load config from a given path. Returns null if missing or unreadable.
 */
export async function loadConfigFile<T>(filePath: string): Promise<AppConfig<T> | null> {
  try {
    const data = await fs.readFile(filePath, 'utf8');
    return JSON.parse(data) as AppConfig<T>;
  } catch {
    return null;
  }
}

/**
 * Save config to a given path. Ensures parent directory exists.
 */
export async function saveConfigFile<T>(filePath: string, config: AppConfig<T>): Promise<boolean> {
  try {
    await fs.mkdir(path.dirname(filePath), { recursive: true });
    await fs.writeFile(filePath, JSON.stringify(config, null, 2), 'utf8');
    return true;
  } catch (error) {
    console.error('Config save error:', error);
    return false;
  }
}
