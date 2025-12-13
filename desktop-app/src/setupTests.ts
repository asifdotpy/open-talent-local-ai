/**
 * Jest Setup File
 * Configures test environment and global mocks
 */

import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock canvas context
HTMLCanvasElement.prototype.getContext = jest.fn((contextType) => {
  if (contextType === 'webgl' || contextType === 'webgl2') {
    return {
      // WebGL context methods
      useProgram: jest.fn(),
      createProgram: jest.fn(() => ({})),
      createShader: jest.fn(() => ({})),
      shaderSource: jest.fn(),
      compileShader: jest.fn(),
      attachShader: jest.fn(),
      linkProgram: jest.fn(),
      viewport: jest.fn(),
      clear: jest.fn(),
      drawArrays: jest.fn(),
      drawElements: jest.fn(),
      getExtension: jest.fn((name) => {
        // Return mock extensions
        if (name === 'WEBGL_lose_context') {
          return { loseContext: jest.fn(), restoreContext: jest.fn() };
        }
        if (name === 'OES_vertex_array_object') {
          return { createVertexArrayOES: jest.fn(() => ({})), bindVertexArrayOES: jest.fn() };
        }
        return {};
      }),
      getParameter: jest.fn(() => 1),
      createTexture: jest.fn(() => ({})),
      bindTexture: jest.fn(),
      texImage2D: jest.fn(),
      createBuffer: jest.fn(() => ({})),
      bindBuffer: jest.fn(),
      bufferData: jest.fn(),
      createFramebuffer: jest.fn(() => ({})),
      bindFramebuffer: jest.fn(),
      framebufferTexture2D: jest.fn(),
      blendFunc: jest.fn(),
      enable: jest.fn(),
      disable: jest.fn(),
      getUniformLocation: jest.fn(() => ({})),
      uniform1f: jest.fn(),
      uniform3fv: jest.fn(),
      uniform4fv: jest.fn(),
      uniformMatrix4fv: jest.fn(),
      getAttribLocation: jest.fn(() => 0),
      vertexAttribPointer: jest.fn(),
      enableVertexAttribArray: jest.fn(),
      activeTexture: jest.fn(),
      pixelStorei: jest.fn(),
      canvas: { width: 800, height: 600 },
      drawingBufferWidth: 800,
      drawingBufferHeight: 600,
    };
  }
  
  // Default 2D context mock
  return {
    fillRect: jest.fn(),
    clearRect: jest.fn(),
    getImageData: jest.fn(() => ({ data: [] })),
    putImageData: jest.fn(),
    createImageData: jest.fn(() => []),
    setTransform: jest.fn(),
    drawImage: jest.fn(),
    save: jest.fn(),
    fillText: jest.fn(),
    restore: jest.fn(),
    beginPath: jest.fn(),
    moveTo: jest.fn(),
    lineTo: jest.fn(),
    closePath: jest.fn(),
    stroke: jest.fn(),
    translate: jest.fn(),
    scale: jest.fn(),
    rotate: jest.fn(),
    arc: jest.fn(),
    fill: jest.fn(),
    measureText: jest.fn(() => ({ width: 0 })),
    transform: jest.fn(),
    rect: jest.fn(),
    clip: jest.fn(),
    createLinearGradient: jest.fn(() => ({
      addColorStop: jest.fn(),
    })),
  };
}) as any;

// Mock AudioContext
(window as any).AudioContext = jest.fn(() => ({
  createMediaStreamSource: jest.fn(),
  createAnalyser: jest.fn(),
  createGain: jest.fn(),
  createOscillator: jest.fn(),
  destination: {},
  resume: jest.fn(),
}));

(window as any).webkitAudioContext = (window as any).AudioContext;

// Mock WebGL
(window as any).WebGLRenderingContext = jest.fn(() => ({
  useProgram: jest.fn(),
  createProgram: jest.fn(),
  createShader: jest.fn(),
  shaderSource: jest.fn(),
  compileShader: jest.fn(),
  attachShader: jest.fn(),
  linkProgram: jest.fn(),
  viewport: jest.fn(),
  clear: jest.fn(),
  drawArrays: jest.fn(),
}));

// Mock MediaRecorder
(window as any).MediaRecorder = jest.fn(() => ({
  start: jest.fn(),
  stop: jest.fn(),
  pause: jest.fn(),
  resume: jest.fn(),
  ondataavailable: null,
  onstop: null,
  onerror: null,
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Suppress console errors in tests (optional)
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
