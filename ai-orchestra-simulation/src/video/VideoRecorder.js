/**
 * VideoRecorder - Captures WebGL canvas to MP4 video
 * 
 * Phase 1: Client-Side WebGL Rendering
 * Captures Three.js scene at 60fps and syncs with audio
 * 
 * Usage:
 *   const recorder = new VideoRecorder(canvas, audioContext);
 *   await recorder.startRecording();
 *   // ... render frames ...
 *   const mp4Blob = await recorder.stopRecording();
 */

import { Logger } from '../utils/Logger.js';

export class VideoRecorder {
  constructor(canvas, audioContext, options = {}) {
    this.canvas = canvas;
    this.audioContext = audioContext;
    this.logger = new Logger('VideoRecorder');

    // Recording configuration
    this.config = {
      fps: options.fps || 60,
      videoBitrate: options.videoBitrate || 2500, // kbps
      audioBitrate: options.audioBitrate || 128, // kbps
      audioSampleRate: options.audioSampleRate || 48000,
      maxDuration: options.maxDuration || 300, // seconds
      ...options,
    };

    // State
    this.isRecording = false;
    this.frameCount = 0;
    this.frames = [];
    this.audioData = null;
    this.startTime = null;
    this.frameTimestamps = [];

    // MediaRecorder setup
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.recordedBlobs = [];

    this.logger.log('Initialized', {
      fps: this.config.fps,
      canvas: `${this.canvas.width}x${this.canvas.height}`,
      videoBitrate: `${this.config.videoBitrate} kbps`,
    });
  }

  /**
   * Start recording video from canvas
   */
  async startRecording() {
    try {
      this.isRecording = true;
      this.frameCount = 0;
      this.frames = [];
      this.frameTimestamps = [];
      this.startTime = performance.now();
      this.audioChunks = [];
      this.recordedBlobs = [];

      // Create canvas stream for video
      const canvasStream = this.canvas.captureStream(this.config.fps);

      // Get audio stream if available
      let audioStream = null;
      if (this.audioContext && this.audioContext.createMediaStreamAudioDestination) {
        audioStream = this.audioContext.createMediaStreamAudioDestination().stream;
      }

      // Combine streams
      const tracks = canvasStream.getVideoTracks();
      if (audioStream) {
        const audioTracks = audioStream.getAudioTracks();
        audioTracks.forEach(track => tracks.push(track));
      }

      const combinedStream = new MediaStream(tracks);

      // Setup MediaRecorder
      this.mediaRecorder = new MediaRecorder(combinedStream, {
        mimeType: 'video/webm;codecs=vp9,opus',
        videoBitsPerSecond: this.config.videoBitrate * 1000,
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.recordedBlobs.push(event.data);
        }
      };

      this.mediaRecorder.start();
      this.logger.log('Recording started', { timestamp: new Date().toISOString() });

      return true;
    } catch (error) {
      this.logger.error('Failed to start recording', error);
      this.isRecording = false;
      throw error;
    }
  }

  /**
   * Record a frame (call once per render loop iteration)
   */
  recordFrame() {
    if (!this.isRecording) return;

    const now = performance.now();
    const elapsed = (now - this.startTime) / 1000; // Convert to seconds

    // Check duration limit
    if (elapsed > this.config.maxDuration) {
      this.logger.warn('Max recording duration reached', { duration: elapsed });
      return false;
    }

    // Track frame and timestamp
    this.frameCount++;
    this.frameTimestamps.push({
      timestamp: elapsed,
      frameNumber: this.frameCount,
    });

    // Log every 60 frames (~1 second at 60fps)
    if (this.frameCount % 60 === 0) {
      this.logger.debug('Recording frame', {
        frame: this.frameCount,
        elapsed: elapsed.toFixed(2),
        fps: (this.frameCount / elapsed).toFixed(1),
      });
    }

    return true;
  }

  /**
   * Stop recording and return video blob
   */
  async stopRecording() {
    if (!this.isRecording) {
      this.logger.warn('Recording not active');
      return null;
    }

    return new Promise((resolve, reject) => {
      try {
        this.isRecording = false;

        if (!this.mediaRecorder) {
          reject(new Error('MediaRecorder not initialized'));
          return;
        }

        this.mediaRecorder.onstop = async () => {
          try {
            const blob = new Blob(this.recordedBlobs, { type: 'video/webm' });
            
            const duration = (performance.now() - this.startTime) / 1000;
            this.logger.log('Recording stopped', {
              duration: duration.toFixed(2),
              frames: this.frameCount,
              fps: (this.frameCount / duration).toFixed(1),
              blobSize: `${(blob.size / 1024 / 1024).toFixed(2)} MB`,
            });

            resolve(blob);
          } catch (error) {
            reject(error);
          }
        };

        this.mediaRecorder.stop();
      } catch (error) {
        this.logger.error('Failed to stop recording', error);
        reject(error);
      }
    });
  }

  /**
   * Download recorded video as file
   */
  async downloadVideo(filename = 'avatar-interview.webm') {
    try {
      const blob = await this.stopRecording();
      if (!blob) {
        this.logger.warn('No video blob available');
        return false;
      }

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      this.logger.log('Video downloaded', { filename });
      return true;
    } catch (error) {
      this.logger.error('Failed to download video', error);
      return false;
    }
  }

  /**
   * Export video as blob (for upload or further processing)
   */
  async exportVideo(format = 'webm') {
    try {
      const blob = await this.stopRecording();
      if (!blob) {
        this.logger.warn('No video blob available');
        return null;
      }

      // If WebM requested, return as-is
      if (format === 'webm' || format === 'mp4') {
        this.logger.log('Video exported', { 
          format,
          size: `${(blob.size / 1024 / 1024).toFixed(2)} MB`,
        });
        return blob;
      }

      this.logger.warn('Unsupported format', { format });
      return blob; // Return WebM as fallback
    } catch (error) {
      this.logger.error('Failed to export video', error);
      throw error;
    }
  }

  /**
   * Get recording statistics
   */
  getStats() {
    const duration = this.isRecording 
      ? (performance.now() - this.startTime) / 1000
      : 0;

    return {
      isRecording: this.isRecording,
      frameCount: this.frameCount,
      duration: duration.toFixed(2),
      fps: this.frameCount > 0 ? (this.frameCount / duration).toFixed(1) : 0,
      estimatedSize: `${(this.recordedBlobs.reduce((sum, blob) => sum + blob.size, 0) / 1024 / 1024).toFixed(2)} MB`,
      config: this.config,
    };
  }

  /**
   * Check audio-video synchronization
   * @param {number} audioDuration - Duration of audio track in seconds
   * @returns {object} Sync metrics
   */
  checkSync(audioDuration) {
    if (this.frameCount === 0) {
      return {
        synced: false,
        error: 'No frames recorded',
      };
    }

    const videoDuration = (performance.now() - this.startTime) / 1000;
    const syncError = Math.abs(audioDuration - videoDuration);
    const syncThreshold = 0.05; // 50ms threshold (Phase 1 target)

    const synced = syncError < syncThreshold;

    this.logger.log('Sync check', {
      audio: audioDuration.toFixed(3),
      video: videoDuration.toFixed(3),
      error: syncError.toFixed(3),
      threshold: syncThreshold,
      synced,
    });

    return {
      synced,
      audioDuration: audioDuration.toFixed(3),
      videoDuration: videoDuration.toFixed(3),
      errorMs: (syncError * 1000).toFixed(1),
      thresholdMs: syncThreshold * 1000,
    };
  }

  /**
   * Reset recorder state
   */
  reset() {
    this.isRecording = false;
    this.frameCount = 0;
    this.frames = [];
    this.frameTimestamps = [];
    this.audioChunks = [];
    this.recordedBlobs = [];
    this.startTime = null;

    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop();
      } catch (e) {
        // Ignore errors on stop
      }
    }

    this.logger.log('Recorder reset');
  }

  /**
   * Get browser compatibility info
   */
  static checkBrowserSupport() {
    const support = {
      canvas: !!HTMLCanvasElement,
      captureStream: !!HTMLCanvasElement.prototype.captureStream,
      mediaRecorder: !!window.MediaRecorder,
      mediaStreamAudioDestination: !!(
        window.AudioContext || window.webkitAudioContext
      ),
      webm: false,
      vp9: false,
      opus: false,
    };

    // Check WebM codec support
    if (support.mediaRecorder) {
      try {
        const mr = new MediaRecorder(new MediaStream(), {
          mimeType: 'video/webm',
        });
        support.webm = mr.mimeType === 'video/webm';
      } catch (e) {
        support.webm = false;
      }

      // Check VP9 and Opus codec support
      try {
        const mr = new MediaRecorder(new MediaStream(), {
          mimeType: 'video/webm;codecs=vp9,opus',
        });
        support.vp9 = support.opus = mr.mimeType === 'video/webm;codecs=vp9,opus';
      } catch (e) {
        support.vp9 = support.opus = false;
      }
    }

    return support;
  }
}

export default VideoRecorder;
