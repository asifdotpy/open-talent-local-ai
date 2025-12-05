/**
 * AudioVisualization.js
 *
 * Audio waveform visualization component for audio-only interviews
 * Shows real-time audio amplitude and frequency analysis
 */

export class AudioVisualization {
  constructor(container, audioElement) {
    this.container = container;
    this.audioElement = audioElement;
    this.canvas = null;
    this.ctx = null;
    this.animationId = null;
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
    this.isActive = false;

    this.width = 800;
    this.height = 400;
    this.barWidth = 2;
    this.barGap = 1;
    this.barCount = Math.floor(this.width / (this.barWidth + this.barGap));

    this.colors = {
      background: '#0a0e27',
      bars: '#667eea',
      barsActive: '#34d399',
      grid: '#2a3a5a',
      text: '#e0e0e0'
    };
  }

  useMediaStream(stream) {
    // Switch visualization source to MediaStream (e.g., remote WebRTC track)
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    const source = this.audioContext.createMediaStreamSource(stream);
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 256;
    this.analyser.smoothingTimeConstant = 0.8;
    source.connect(this.analyser);
    this.analyser.connect(this.audioContext.destination);
    this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    this.waveformArray = new Uint8Array(this.analyser.fftSize);
    this.barCount = Math.min(this.barCount, this.dataArray.length);
    return true;
  }

  async initialize() {
    try {
      // Create canvas
      this.canvas = document.createElement('canvas');
      this.canvas.width = this.width;
      this.canvas.height = this.height;
      this.canvas.style.border = '2px solid #2a3a5a';
      this.canvas.style.borderRadius = '8px';
      this.canvas.style.backgroundColor = this.colors.background;

      // Add to container
      this.container.appendChild(this.canvas);
      this.ctx = this.canvas.getContext('2d');

      // Initialize Web Audio API
      await this.initializeAudioContext();

      console.log('[AudioVisualization] Initialized successfully');
      return true;
    } catch (error) {
      console.error('[AudioVisualization] Failed to initialize:', error);
      return false;
    }
  }

  async initializeAudioContext() {
    try {
      // Create audio context
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

      // Create analyser node
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      this.analyser.smoothingTimeConstant = 0.8;

      // Connect audio element to analyser
      const source = this.audioContext.createMediaElementSource(this.audioElement);
      source.connect(this.analyser);
      this.analyser.connect(this.audioContext.destination);

      // Create data arrays for frequency and waveform data
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
      this.waveformArray = new Uint8Array(this.analyser.fftSize);

      // Limit bar count to available frequency bins to avoid step=0
      this.barCount = Math.min(this.barCount, this.dataArray.length);
      if (this.barCount <= 0) {
        this.barCount = this.dataArray.length;
      }

      // Expose context for external reuse (e.g., GUIManager)
      this.audioElement._audioContext = this.audioContext;

      console.log('[AudioVisualization] Audio context initialized');
    } catch (error) {
      console.error('[AudioVisualization] Failed to initialize audio context:', error);
      throw error;
    }
  }

  start() {
    if (!this.isActive && this.analyser) {
      this.isActive = true;
      
      // Resume audio context if suspended (required by browser autoplay policies)
      if (this.audioContext && this.audioContext.state === 'suspended') {
        this.audioContext.resume().then(() => {
          console.log('[AudioVisualization] Audio context resumed');
        }).catch(error => {
          console.error('[AudioVisualization] Failed to resume audio context:', error);
        });
      }
      
      this.animate();
      console.log('[AudioVisualization] Started visualization');
    }
  }

  stop() {
    this.isActive = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    console.log('[AudioVisualization] Stopped visualization');
  }

  animate() {
    if (!this.isActive) return;

    this.animationId = requestAnimationFrame(() => this.animate());

    // Get frequency and waveform data
    this.analyser.getByteFrequencyData(this.dataArray);
    this.analyser.getByteTimeDomainData(this.waveformArray);

    // Clear canvas
    this.ctx.fillStyle = this.colors.background;
    this.ctx.fillRect(0, 0, this.width, this.height);

    // Draw grid
    this.drawGrid();

    // Draw frequency bars
    this.drawFrequencyBars();

    // Draw waveform overlay
    this.drawWaveform();

    // Draw labels
    this.drawLabels();
  }

  drawGrid() {
    this.ctx.strokeStyle = this.colors.grid;
    this.ctx.lineWidth = 1;

    // Horizontal lines
    for (let y = 0; y < this.height; y += 50) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.width, y);
      this.ctx.stroke();
    }

    // Vertical lines
    for (let x = 0; x < this.width; x += 100) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, this.height);
      this.ctx.stroke();
    }
  }

  drawFrequencyBars() {
    const barWidth = (this.width - (this.barCount - 1) * this.barGap) / this.barCount;
    for (let i = 0; i < this.barCount; i++) {
      const value = this.dataArray[i] || 0; // Single bin per bar
      const barHeight = (value / 255) * this.height;
      const isActive = value > 50;
      this.ctx.fillStyle = isActive ? this.colors.barsActive : this.colors.bars;
      const x = i * (barWidth + this.barGap);
      const y = this.height - barHeight;
      this.ctx.fillRect(x, y, barWidth, barHeight);
      if (isActive) {
        this.ctx.shadowColor = this.colors.barsActive;
        this.ctx.shadowBlur = 8;
        this.ctx.fillRect(x, y, barWidth, barHeight);
        this.ctx.shadowBlur = 0;
      }
    }
  }

  drawWaveform() {
    if (!this.waveformArray) return;
    this.ctx.lineWidth = 2;
    this.ctx.strokeStyle = '#ffb347';
    this.ctx.beginPath();
    const sliceWidth = this.width / this.waveformArray.length;
    let x = 0;
    for (let i = 0; i < this.waveformArray.length; i++) {
      const v = this.waveformArray[i] / 128.0; // Normalize around center
      const y = v * this.height / 2;
      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
      x += sliceWidth;
    }
    this.ctx.lineTo(this.width, this.height / 2);
    this.ctx.stroke();
  }

  drawLabels() {
    this.ctx.fillStyle = this.colors.text;
    this.ctx.font = '14px monospace';
    this.ctx.textAlign = 'left';

    // Title
    this.ctx.fillText('Audio Frequency Analysis', 20, 30);

    // Instructions
    this.ctx.font = '12px monospace';
    this.ctx.fillText('Real-time audio visualization', 20, this.height - 40);
    this.ctx.fillText('Green bars indicate active frequencies', 20, this.height - 20);
  }

  dispose() {
    this.stop();

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }

    if (this.canvas && this.canvas.parentNode) {
      this.canvas.parentNode.removeChild(this.canvas);
    }

    console.log('[AudioVisualization] Disposed');
  }
}