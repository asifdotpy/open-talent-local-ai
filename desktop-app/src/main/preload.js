const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Hardware detection
  detectHardware: () => ipcRenderer.invoke('detect-hardware'),
  recommendModel: (ramGb) => ipcRenderer.invoke('recommend-model', ramGb),
  
  // Config management
  loadConfig: () => ipcRenderer.invoke('load-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  
  // Voice permissions and state
  voice: {
    checkPermission: () => ipcRenderer.invoke('voice:checkPermission'),
    requestPermission: () => ipcRenderer.invoke('voice:requestPermission'),
  },
  
  // Avatar state
  avatar: {
    getState: () => ipcRenderer.invoke('avatar:getState'),
  }
});

// Legacy Ollama API for backward compatibility
contextBridge.exposeInMainWorld('ollama', {
  checkStatus: () => ipcRenderer.invoke('ollama:check-status'),
  listModels: () => ipcRenderer.invoke('ollama:list-models'),
  sendMessage: (message, model, conversationHistory) => 
    ipcRenderer.invoke('ollama:send-message', { message, model, conversationHistory }),
  startInterview: (role, model) => 
    ipcRenderer.invoke('ollama:start-interview', { role, model })
});
