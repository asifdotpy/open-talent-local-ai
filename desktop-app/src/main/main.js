const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const OllamaService = require('../services/ollama-service');

let mainWindow;
let ollamaService;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    icon: path.join(__dirname, '../../resources/icon.png')
  });

  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

  // Open DevTools in development mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  // Initialize Ollama service
  ollamaService = new OllamaService();

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers for Ollama communication
ipcMain.handle('ollama:check-status', async () => {
  try {
    const isRunning = await ollamaService.checkStatus();
    return { success: true, isRunning };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('ollama:list-models', async () => {
  try {
    const models = await ollamaService.listModels();
    return { success: true, models };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('ollama:send-message', async (event, { message, model, conversationHistory }) => {
  try {
    const response = await ollamaService.sendMessage(message, model, conversationHistory);
    return { success: true, response };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('ollama:start-interview', async (event, { role, model }) => {
  try {
    const response = await ollamaService.startInterview(role, model);
    return { success: true, response };
  } catch (error) {
    return { success: false, error: error.message };
  }
});
