import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import isDev from 'electron-is-dev';
import { detectHardware, HardwareInfo } from './hardware';
import { recommendModel } from './recommender';
import { loadConfigFile, saveConfigFile } from './config';

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      // Preload lives in dist/preload when compiled
      preload: path.join(__dirname, '../preload/preload.js'),
      sandbox: true
    }
  });

  const forceProd = process.env.FORCE_PROD === '1';
  const useProd = forceProd || app.isPackaged || !isDev;

  const startUrl = useProd
    ? `file://${path.join(__dirname, '../../build/index.html')}`
    : 'http://localhost:3000';

  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Handle hardware detection from renderer
ipcMain.handle('detect-hardware', () => {
  return detectHardware();
});

// Handle model recommendation from renderer
ipcMain.handle('recommend-model', (_, ramGb: number) => {
  return recommendModel(ramGb);
});

// Handle config save/load
const configDir = path.join(app.getPath('appData'), 'opentalent');
const configPath = path.join(configDir, 'config.json');

ipcMain.handle('load-config', async () => {
  return loadConfigFile<HardwareInfo>(configPath);
});

ipcMain.handle('save-config', async (_, config) => {
  return saveConfigFile(configPath, config as { selectedModel?: string; hardwareProfile?: HardwareInfo });
});
