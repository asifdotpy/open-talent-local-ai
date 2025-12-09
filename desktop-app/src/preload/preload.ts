import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  detectHardware: () => ipcRenderer.invoke('detect-hardware'),  recommendModel: (ramGb: number) => ipcRenderer.invoke('recommend-model', ramGb),  loadConfig: () => ipcRenderer.invoke('load-config'),
  saveConfig: (config: any) => ipcRenderer.invoke('save-config', config)
});
