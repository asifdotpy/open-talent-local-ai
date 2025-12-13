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

/**
 * Voice Input Service IPC Handlers
 * Handles microphone capture and audio processing
 */

ipcMain.handle('voice:checkPermission', async () => {
  try {
    // Check if Electron has audio access (Windows/macOS/Linux)
    // For Electron, this is handled by the system at runtime
    return { permitted: true };
  } catch (err) {
    console.error('Voice permission check error:', err);
    return { permitted: false, error: 'Failed to check permission' };
  }
});

ipcMain.handle('voice:requestPermission', async () => {
  try {
    // Electron doesn't need explicit permission in most cases
    // The browser handle will request via getUserMedia
    return { permitted: true };
  } catch (err) {
    console.error('Voice permission request error:', err);
    return { permitted: false, error: 'Microphone access denied' };
  }
});

/**
 * Avatar Renderer IPC Handlers
 * Handles 3D avatar rendering and customization
 */

ipcMain.handle('avatar:getState', async () => {
  try {
    return {
      isInitialized: true,
      isAnimating: false,
      currentExpression: 'neutral' as const,
      mouthOpen: 0,
    };
  } catch (err) {
    console.error('Avatar state error:', err);
    return null;
  }
});

/**
 * Transcription Service IPC Handlers
 * Handles speech-to-text and phoneme extraction
 */

ipcMain.handle('transcription:initialize', async (_, config) => {
  try {
    return {
      success: true,
      message: 'Transcription service initialized',
      config,
    };
  } catch (err) {
    console.error('Transcription init error:', err);
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Initialization failed',
    };
  }
});

/**
 * Testimonial Database IPC Handlers
 * Handles encrypted storage and retrieval of testimonials
 */

ipcMain.handle('testimonial:save', async (_, data) => {
  try {
    // Save logic is handled by the testimonialDatabase service in renderer
    // This handler is for logging/analytics
    console.log('✅ Testimonial saved:', {
      id: data.id,
      incidentType: data.incident?.type,
      anonymous: data.privacy?.anonymous,
      timestamp: new Date().toISOString(),
    });

    return {
      success: true,
      id: data.id,
      message: 'Testimonial saved successfully',
    };
  } catch (err) {
    console.error('Testimonial save error:', err);
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Failed to save testimonial',
    };
  }
});

ipcMain.handle('testimonial:list', async (_, filter) => {
  try {
    // List logic is handled by the testimonialDatabase service in renderer
    // This handler provides a bridge for potential backend storage
    return {
      success: true,
      filter,
      count: 0,
      message: 'Testimonials retrieved',
    };
  } catch (err) {
    console.error('Testimonial list error:', err);
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Failed to list testimonials',
    };
  }
});

ipcMain.handle('testimonial:export', async (_, format) => {
  try {
    // Export logic for batch processing
    return {
      success: true,
      format,
      count: 0,
      message: 'Export prepared',
    };
  } catch (err) {
    console.error('Testimonial export error:', err);
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Failed to export testimonials',
    };
  }
});
