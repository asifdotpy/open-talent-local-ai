/**
 * CaptionsOverlay.js
 *
 * Real-time speech-to-text captions display for WebRTC audio streams.
 * Shows partial and final transcripts from DataChannel messages.
 */

export class CaptionsOverlay {
  constructor(container) {
    this.container = container;
    this.overlayElement = null;
    this.partialElement = null;
    this.finalElement = null;
    this.transcriptHistory = [];
    this.maxHistoryLines = 3;
    this.isVisible = false;

    this.init();
  }

  init() {
    // Create overlay container
    this.overlayElement = document.createElement('div');
    this.overlayElement.id = 'captions-overlay';
    this.overlayElement.style.cssText = `
      position: fixed;
      bottom: 80px;
      left: 50%;
      transform: translateX(-50%);
      width: 80%;
      max-width: 800px;
      padding: 20px;
      background: rgba(0, 0, 0, 0.85);
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
      z-index: 900;
      display: none;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    `;

    // Create final transcript section (history)
    this.finalElement = document.createElement('div');
    this.finalElement.id = 'captions-final';
    this.finalElement.style.cssText = `
      color: rgba(255, 255, 255, 0.7);
      font-size: 16px;
      line-height: 1.6;
      margin-bottom: 12px;
      max-height: 100px;
      overflow-y: auto;
      scrollbar-width: thin;
      scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
    `;

    // Create partial transcript section (current)
    this.partialElement = document.createElement('div');
    this.partialElement.id = 'captions-partial';
    this.partialElement.style.cssText = `
      color: #ffffff;
      font-size: 18px;
      font-weight: 500;
      line-height: 1.6;
      min-height: 30px;
      animation: pulse 2s ease-in-out infinite;
    `;

    // Add CSS for pulse animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
      }

      #captions-final::-webkit-scrollbar {
        width: 6px;
      }

      #captions-final::-webkit-scrollbar-track {
        background: transparent;
      }

      #captions-final::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 3px;
      }

      #captions-final::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
      }

      .caption-line {
        margin-bottom: 4px;
        transition: opacity 0.3s ease;
      }

      .caption-confidence-high { color: rgba(255, 255, 255, 0.9); }
      .caption-confidence-medium { color: rgba(255, 255, 255, 0.7); }
      .caption-confidence-low { color: rgba(255, 255, 255, 0.5); }
    `;
    document.head.appendChild(style);

    // Assemble overlay
    this.overlayElement.appendChild(this.finalElement);
    this.overlayElement.appendChild(this.partialElement);
    this.container.appendChild(this.overlayElement);

    console.log('[CaptionsOverlay] Initialized');
  }

  show() {
    this.isVisible = true;
    this.overlayElement.style.display = 'block';
    console.log('[CaptionsOverlay] Shown');
  }

  hide() {
    this.isVisible = false;
    this.overlayElement.style.display = 'none';
    console.log('[CaptionsOverlay] Hidden');
  }

  toggle() {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }

  /**
   * Handle incoming transcript message from DataChannel
   * @param {Object} message - Transcript message
   */
  handleMessage(message) {
    const { type, text, confidence } = message;

    if (type === 'transcript.partial') {
      this.updatePartial(text);
    } else if (type === 'transcript.final') {
      this.addFinal(text, confidence);
      this.clearPartial();
    }
  }

  /**
   * Update partial (in-progress) transcript
   * @param {string} text - Partial transcript text
   */
  updatePartial(text) {
    if (!text) {
      this.partialElement.textContent = '';
      return;
    }

    this.partialElement.textContent = text;
    this.show(); // Auto-show when receiving captions
  }

  /**
   * Add final transcript to history
   * @param {string} text - Final transcript text
   * @param {number} confidence - Confidence score (0-1)
   */
  addFinal(text, confidence = 1.0) {
    if (!text || text.trim().length === 0) {
      return;
    }

    // Add to history
    this.transcriptHistory.push({ text, confidence, timestamp: Date.now() });

    // Limit history size
    if (this.transcriptHistory.length > this.maxHistoryLines) {
      this.transcriptHistory.shift();
    }

    // Render history
    this.renderHistory();
  }

  /**
   * Clear partial transcript
   */
  clearPartial() {
    this.partialElement.textContent = '';
  }

  /**
   * Render transcript history
   */
  renderHistory() {
    this.finalElement.innerHTML = '';

    this.transcriptHistory.forEach((entry, index) => {
      const line = document.createElement('div');
      line.className = 'caption-line';

      // Apply confidence-based styling
      if (entry.confidence >= 0.85) {
        line.classList.add('caption-confidence-high');
      } else if (entry.confidence >= 0.7) {
        line.classList.add('caption-confidence-medium');
      } else {
        line.classList.add('caption-confidence-low');
      }

      line.textContent = entry.text;
      this.finalElement.appendChild(line);
    });

    // Auto-scroll to bottom
    this.finalElement.scrollTop = this.finalElement.scrollHeight;
  }

  /**
   * Clear all captions
   */
  clear() {
    this.transcriptHistory = [];
    this.finalElement.innerHTML = '';
    this.partialElement.textContent = '';
    console.log('[CaptionsOverlay] Cleared');
  }

  /**
   * Get full transcript text
   * @returns {string} Combined transcript
   */
  getFullTranscript() {
    return this.transcriptHistory.map(entry => entry.text).join(' ');
  }

  /**
   * Export transcript history
   * @returns {Array} Transcript entries
   */
  exportHistory() {
    return [...this.transcriptHistory];
  }

  /**
   * Destroy overlay
   */
  destroy() {
    if (this.overlayElement) {
      this.overlayElement.remove();
    }
    console.log('[CaptionsOverlay] Destroyed');
  }
}
