const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('ollama', {
  checkStatus: () => ipcRenderer.invoke('ollama:check-status'),
  listModels: () => ipcRenderer.invoke('ollama:list-models'),
  sendMessage: (message, model, conversationHistory) => 
    ipcRenderer.invoke('ollama:send-message', { message, model, conversationHistory }),
  startInterview: (role, model) => 
    ipcRenderer.invoke('ollama:start-interview', { role, model })
});
