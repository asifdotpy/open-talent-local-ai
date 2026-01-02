import { debugLog } from '../utils/logger.js';

// UI state
let controlsContainer = null;
let statusIndicators = {};
let controlButtons = {};
let sliders = {};
let isControlsVisible = true;

// Initialize UI controls
export function initUIControls() {
  createControlsContainer();
  createStatusIndicators();
  createControlButtons();
  createSliders();
  setupEventListeners();

  debugLog('UI', 'UI controls initialized');
}

// Create main controls container
function createControlsContainer() {
  controlsContainer = document.createElement('div');
  controlsContainer.id = 'avatar-controls';
  controlsContainer.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 15px;
    border-radius: 10px;
    font-family: Arial, sans-serif;
    font-size: 12px;
    z-index: 1000;
    min-width: 250px;
    backdrop-filter: blur(10px);
  `;

  document.body.appendChild(controlsContainer);
}

// Create status indicators
function createStatusIndicators() {
  const statusDiv = document.createElement('div');
  statusDiv.style.marginBottom = '15px';

  const statuses = [
    { id: 'websocket', label: 'WebSocket', color: '#ff4444' },
    { id: 'microphone', label: 'Microphone', color: '#ff4444' },
    { id: 'audio', label: 'Audio', color: '#ff4444' },
    { id: 'animation', label: 'Animation', color: '#ff4444' }
  ];

  statuses.forEach(status => {
    const indicator = document.createElement('div');
    indicator.style.display = 'flex';
    indicator.style.alignItems = 'center';
    indicator.style.marginBottom = '5px';

    const dot = document.createElement('div');
    dot.id = `status-${status.id}`;
    dot.style.cssText = `
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: ${status.color};
      margin-right: 8px;
      transition: background 0.3s ease;
    `;

    const label = document.createElement('span');
    label.textContent = status.label;

    indicator.appendChild(dot);
    indicator.appendChild(label);
    statusDiv.appendChild(indicator);

    statusIndicators[status.id] = dot;
  });

  controlsContainer.appendChild(statusDiv);
}

// Create control buttons
function createControlButtons() {
  const buttonsDiv = document.createElement('div');
  buttonsDiv.style.marginBottom = '15px';

  const buttons = [
    { id: 'record', label: '🎤 Record', action: 'toggleRecording' },
    { id: 'stream', label: '📡 Stream', action: 'toggleStreaming' },
    { id: 'reset', label: '🔄 Reset', action: 'resetAvatar' },
    { id: 'fullscreen', label: '⛶ Fullscreen', action: 'toggleFullscreen' }
  ];

  buttons.forEach(button => {
    const btn = document.createElement('button');
    btn.id = `btn-${button.id}`;
    btn.textContent = button.label;
    btn.dataset.action = button.action;
    btn.style.cssText = `
      background: #333;
      color: white;
      border: 1px solid #555;
      padding: 8px 12px;
      margin: 2px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 11px;
      transition: background 0.2s ease;
    `;

    btn.addEventListener('mouseenter', () => btn.style.background = '#555');
    btn.addEventListener('mouseleave', () => btn.style.background = '#333');

    buttonsDiv.appendChild(btn);
    controlButtons[button.id] = btn;
  });

  controlsContainer.appendChild(buttonsDiv);
}

// Create sliders for real-time control
function createSliders() {
  const slidersDiv = document.createElement('div');

  const sliderConfigs = [
    { id: 'volume', label: 'Volume', min: 0, max: 1, step: 0.1, value: 0.8 },
    { id: 'sensitivity', label: 'Mic Sensitivity', min: 0, max: 2, step: 0.1, value: 1.0 },
    { id: 'animationSpeed', label: 'Animation Speed', min: 0.1, max: 3, step: 0.1, value: 1.0 },
    { id: 'mouthAmplitude', label: 'Mouth Amplitude', min: 0, max: 2, step: 0.1, value: 1.0 }
  ];

  sliderConfigs.forEach(config => {
    const sliderContainer = document.createElement('div');
    sliderContainer.style.marginBottom = '10px';

    const label = document.createElement('label');
    label.textContent = config.label;
    label.style.display = 'block';
    label.style.marginBottom = '3px';
    label.style.fontSize = '11px';

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.id = `slider-${config.id}`;
    slider.min = config.min;
    slider.max = config.max;
    slider.step = config.step;
    slider.value = config.value;
    slider.style.cssText = `
      width: 100%;
      height: 4px;
      border-radius: 2px;
      background: #555;
      outline: none;
      -webkit-appearance: none;
    `;

    // Custom slider styling
    const style = document.createElement('style');
    style.textContent = `
      #slider-${config.id}::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #4CAF50;
        cursor: pointer;
      }
      #slider-${config.id}::-moz-range-thumb {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #4CAF50;
        cursor: pointer;
        border: none;
      }
    `;
    document.head.appendChild(style);

    const valueDisplay = document.createElement('span');
    valueDisplay.id = `value-${config.id}`;
    valueDisplay.textContent = config.value;
    valueDisplay.style.cssText = `
      float: right;
      font-size: 10px;
      color: #ccc;
    `;

    slider.addEventListener('input', (e) => {
      valueDisplay.textContent = e.target.value;
      handleSliderChange(config.id, parseFloat(e.target.value));
    });

    sliderContainer.appendChild(label);
    sliderContainer.appendChild(slider);
    sliderContainer.appendChild(valueDisplay);
    slidersDiv.appendChild(sliderContainer);

    sliders[config.id] = { slider, valueDisplay };
  });

  controlsContainer.appendChild(slidersDiv);
}

// Setup event listeners
function setupEventListeners() {
  // Button click handlers
  Object.entries(controlButtons).forEach(([id, button]) => {
    button.addEventListener('click', () => handleButtonClick(button.dataset.action));
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', handleKeyPress);
}

// Handle button clicks
function handleButtonClick(action) {
  debugLog('UI', `Button clicked: ${action}`);

  switch (action) {
    case 'toggleRecording':
      // To be implemented by audio system
      toggleButtonState('record');
      break;
    case 'toggleStreaming':
      // To be implemented by streaming system
      toggleButtonState('stream');
      break;
    case 'resetAvatar':
      resetAvatar();
      break;
    case 'toggleFullscreen':
      toggleFullscreen();
      break;
  }
}

// Handle slider changes
function handleSliderChange(sliderId, value) {
  debugLog('UI', `Slider ${sliderId} changed to ${value}`);

  // Emit events for other systems to handle
  const event = new CustomEvent('uiSliderChange', {
    detail: { sliderId, value }
  });
  document.dispatchEvent(event);
}

// Handle keyboard shortcuts
function handleKeyPress(event) {
  switch (event.key.toLowerCase()) {
    case 'r':
      if (event.ctrlKey) {
        event.preventDefault();
        handleButtonClick('toggleRecording');
      }
      break;
    case 's':
      if (event.ctrlKey) {
        event.preventDefault();
        handleButtonClick('toggleStreaming');
      }
      break;
    case 'f':
      if (event.ctrlKey) {
        event.preventDefault();
        handleButtonClick('toggleFullscreen');
      }
      break;
    case 'h':
      if (event.ctrlKey) {
        event.preventDefault();
        toggleControlsVisibility();
      }
      break;
  }
}

// Toggle button visual state
function toggleButtonState(buttonId) {
  const button = controlButtons[buttonId];
  if (!button) return;

  const isActive = button.classList.contains('active');
  if (isActive) {
    button.classList.remove('active');
    button.style.background = '#333';
  } else {
    button.classList.add('active');
    button.style.background = '#4CAF50';
  }
}

// Update status indicator
export function updateStatusIndicator(statusId, isActive) {
  const indicator = statusIndicators[statusId];
  if (!indicator) return;

  indicator.style.background = isActive ? '#4CAF50' : '#ff4444';
}

// Reset avatar to initial state
function resetAvatar() {
  debugLog('UI', 'Resetting avatar');

  // Reset all sliders to default values
  Object.entries(sliders).forEach(([id, { slider, valueDisplay }]) => {
    const defaultValue = slider.defaultValue || slider.min;
    slider.value = defaultValue;
    valueDisplay.textContent = defaultValue;
    handleSliderChange(id, parseFloat(defaultValue));
  });

  // Emit reset event
  const event = new CustomEvent('uiResetAvatar');
  document.dispatchEvent(event);
}

// Toggle fullscreen mode
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => {
      debugLog('ERROR', 'Failed to enter fullscreen:', err);
    });
  } else {
    document.exitFullscreen();
  }
}

// Toggle controls visibility
export function toggleControlsVisibility() {
  isControlsVisible = !isControlsVisible;
  controlsContainer.style.display = isControlsVisible ? 'block' : 'none';
  debugLog('UI', `Controls ${isControlsVisible ? 'shown' : 'hidden'}`);
}

// Show notification message
export function showNotification(message, type = 'info', duration = 3000) {
  const notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: ${type === 'error' ? '#ff4444' : type === 'success' ? '#4CAF50' : '#2196F3'};
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    z-index: 1001;
    opacity: 0;
    transition: opacity 0.3s ease;
  `;

  document.body.appendChild(notification);

  // Fade in
  setTimeout(() => notification.style.opacity = '1', 10);

  // Fade out and remove
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => document.body.removeChild(notification), 300);
  }, duration);
}

// Get current UI state
export function getUIState() {
  return {
    isControlsVisible,
    statusIndicators: Object.fromEntries(
      Object.entries(statusIndicators).map(([id, element]) => [
        id,
        element.style.background === 'rgb(76, 175, 80)' // #4CAF50
      ])
    ),
    sliderValues: Object.fromEntries(
      Object.entries(sliders).map(([id, { slider }]) => [
        id,
        parseFloat(slider.value)
      ])
    )
  };
}

// Cleanup UI resources
export function cleanupUI() {
  if (controlsContainer && controlsContainer.parentNode) {
    controlsContainer.parentNode.removeChild(controlsContainer);
  }

  statusIndicators = {};
  controlButtons = {};
  sliders = {};

  debugLog('UI', 'UI resources cleaned up');
}
