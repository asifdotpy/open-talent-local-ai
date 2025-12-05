/**
 * main.js
 * 
 * Main entry point for the AI Orchestra Simulation.
 * Orchestrates application initialization, asset loading, and event handling.
 * 
 * This modular implementation replaces the monolithic app.js with a clean
 * architecture that leverages the existing src/ module system.
 */

import { Application } from './src/core/Application.js';

/**
 * Create and display start button
 * @returns {HTMLButtonElement} The created button element
 */
function createStartButton() {
  const button = document.createElement('button');
  button.innerText = 'Click to Start';
  button.style.position = 'absolute';
  button.style.top = '50%';
  button.style.left = '50%';
  button.style.transform = 'translate(-50%, -50%)';
  button.style.padding = '20px';
  button.style.fontSize = '24px';
  button.style.cursor = 'pointer';
  button.style.backgroundColor = '#4a90e2';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '8px';
  button.style.cursor = 'pointer';
  button.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.3)';
  button.style.transition = 'all 0.3s ease';
  button.style.zIndex = '1000';
  
  button.addEventListener('mouseenter', () => {
    button.style.backgroundColor = '#357abd';
    button.style.transform = 'translate(-50%, -50%) scale(1.05)';
  });
  
  button.addEventListener('mouseleave', () => {
    button.style.backgroundColor = '#4a90e2';
    button.style.transform = 'translate(-50%, -50%) scale(1)';
  });
  
  document.body.appendChild(button);
  return button;
}

/**
 * Main application entry point
 */
async function main() {
  try {
    console.log('[MAIN] AI Orchestra Simulation starting...');

    // Create application instance
    const container = document.body;
    const app = new Application(container);

    // Create and configure start button
    const startButton = createStartButton();

    // Optional: WebRTC bootstrap when enabled
    let rtc = null;
    let captions = null;
    try {
      const { AppConfig } = await import('./src/config/AppConfig.js');
      const cfg = AppConfig.get();
      if (cfg.features.enableWebRTCStreaming) {
        // Initialize captions overlay
        const { CaptionsOverlay } = await import('./src/ui/CaptionsOverlay.js');
        captions = new CaptionsOverlay(container);
        
        const { WebRTCClient } = await import('./src/network/WebRTCClient.js');
        const sessionId = `interview-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        rtc = new WebRTCClient({
          sessionId,
          onRemoteAudio: (stream) => {
            const audio = document.getElementById('speech-audio');
            if (audio) {
              audio.srcObject = stream;
              audio.play().catch(() => {});
            }
            // If app initialized with visualization, try to hook the stream
            if (window.app && window.app.audioVisualization && window.app.audioVisualization.useMediaStream) {
              window.app.audioVisualization.useMediaStream(stream);
            }
          },
          onDataMessage: (msg) => {
            // Route transcript messages to captions UI
            if (msg.type && msg.type.startsWith('transcript.')) {
              if (captions) {
                captions.handleMessage(msg);
              }
            }
            console.log('[DataChannel]', msg);
          },
          log: console,
        });
        
        // Expose captions globally for toggle access
        window.captions = captions;
        
        console.log(`[MAIN] WebRTC client prepared with session: ${sessionId}`);
      }
    } catch (e) {
      console.warn('WebRTC init skipped:', e?.message || e);
    }

    startButton.addEventListener('click', async () => {
      try {
        console.log('[MAIN] Start button clicked, initializing application...');
        startButton.disabled = true;
        startButton.innerText = 'Loading...';
        startButton.style.cursor = 'wait';

        // If WebRTC is configured, start it first so remote audio can flow
        if (rtc) {
          try {
            await rtc.start();
          } catch (e) {
            console.warn('WebRTC start failed:', e?.message || e);
          }
        }

        // Initialize application (loads assets, sets up scene)
        await app.initialize();
        
        // Expose app globally for WebRTC hook
        window.app = app;

        // Hide start button
        startButton.style.display = 'none';
        
        // Start application loop (but not animation - user controls via GUI)
        app.start();
        
        console.log('[MAIN] Application started successfully (use GUI to control lip-sync)');
      } catch (error) {
        console.error('[MAIN] Failed to start application:', error);
        startButton.disabled = false;
        startButton.innerText = 'Click to Retry';
        startButton.style.cursor = 'pointer';
        startButton.style.backgroundColor = '#e74c3c';
        
        // Show error message to user
        alert(`Failed to start application: ${error.message}\n\nPlease check the console for details.`);
      }
    });

    // Window resize handler
    window.addEventListener('resize', () => {
      app.resize(window.innerWidth, window.innerHeight);
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      console.log('[MAIN] Cleaning up resources...');
      app.dispose();
    });

    console.log('[MAIN] Application initialized, waiting for user interaction...');

  } catch (error) {
    console.error('[MAIN] Fatal error during initialization:', error);
    alert(`Critical error: ${error.message}\n\nPlease refresh the page and try again.`);
  }
}

/**
 * Start application when DOM is ready
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', main);
} else {
  main();
}
