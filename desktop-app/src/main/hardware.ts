export interface HardwareInfo {
  ramGb: number;
  ramAvailable: number;
  cpuCores: number;
  cpuModel: string;
  platform: 'linux' | 'darwin' | 'win32';
}

export function detectHardware(): HardwareInfo {
  const os = require('os');

  const totalMemBytes = os.totalmem();
  const freeMemBytes = os.freemem();

  const ramGb = Math.round(totalMemBytes / (1024 ** 3));
  const ramAvailable = Math.round(freeMemBytes / (1024 ** 3));

  const cpus = os.cpus();
  const cpuCores = cpus.length;
  const cpuModel = cpus[0]?.model || 'Unknown';

  return {
    ramGb,
    ramAvailable,
    cpuCores,
    cpuModel,
    platform: process.platform as 'linux' | 'darwin' | 'win32'
  };
}
