import os from 'os';
import path from 'path';
import { promises as fs } from 'fs';
import { loadConfigFile, saveConfigFile } from './config';

describe('config file helpers', () => {
  const tmpDir = path.join(os.tmpdir(), `opentalent-config-test-${Date.now()}-${Math.random()}`);
  const cfgPath = path.join(tmpDir, 'config.json');

  afterAll(async () => {
    try {
      await fs.rm(tmpDir, { recursive: true, force: true });
    } catch {
      // ignore
    }
  });

  it('returns null when file does not exist', async () => {
    const cfg = await loadConfigFile(cfgPath);
    expect(cfg).toBeNull();
  });

  it('saves and loads config', async () => {
    const sample = { selectedModel: 'granite-2b', hardwareProfile: { ramGb: 8 } };
    const saved = await saveConfigFile(cfgPath, sample);
    expect(saved).toBe(true);

    const loaded = await loadConfigFile<typeof sample.hardwareProfile>(cfgPath);
    expect(loaded?.selectedModel).toBe('granite-2b');
    expect(loaded?.hardwareProfile?.ramGb).toBe(8);
  });
});
