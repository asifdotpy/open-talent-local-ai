/**
 * VideoEncoder - FFmpeg-based video encoding service
 *
 * Handles conversion of frame sequences to video files with optional audio.
 * Supports multiple codecs and formats (WebM, MP4, etc.).
 */

import { spawn } from 'child_process';
import ffmpeg from 'ffmpeg-static';
import fs from 'fs';
import path from 'path';

export class VideoEncoder {
  constructor(config = {}) {
    this.config = {
      codec: 'libvpx-vp9', // VP9 for WebM
      format: 'webm',
      bitrate: '1M',
      audioCodec: 'libopus',
      ...config
    };

    this.logger = config.logger || console;
  }

  /**
   * Create video from frame directory
   * @param {string} frameDir - Directory containing frame images
   * @param {string} outputPath - Output video file path
   * @param {number} fps - Frames per second
   * @param {string|null} audioPath - Optional audio file path
   * @returns {Promise<void>}
   */
  async encodeFromFrames(frameDir, outputPath, fps, audioPath = null) {
    return new Promise((resolve, reject) => {
      const args = this.buildFFmpegArgs(frameDir, outputPath, fps, audioPath);

      this.logger.log('Starting video encoding', {
        frameDir,
        outputPath,
        fps,
        hasAudio: !!audioPath,
        codec: this.config.codec
      });

      const startTime = Date.now();
      const ffmpegProcess = spawn(ffmpeg, args);

      let stderr = '';

      ffmpegProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        // Log progress if needed
        if (this.config.verbose) {
          this.logger.log('FFmpeg:', data.toString().trim());
        }
      });

      ffmpegProcess.on('close', (code) => {
        const duration = Date.now() - startTime;

        if (code === 0) {
          this.logger.log('Video encoding completed', {
            outputPath,
            duration: `${duration}ms`,
            size: this.getFileSize(outputPath)
          });
          resolve();
        } else {
          this.logger.error('FFmpeg encoding failed', {
            exitCode: code,
            stderr: stderr.slice(-500) // Last 500 chars of error
          });
          reject(new Error(`FFmpeg failed with code ${code}: ${stderr.slice(-200)}`));
        }
      });

      ffmpegProcess.on('error', (error) => {
        this.logger.error('FFmpeg process error:', error);
        reject(error);
      });
    });
  }

  buildFFmpegArgs(frameDir, outputPath, fps, audioPath) {
    const args = [
      '-framerate', fps.toString(),
      '-i', path.join(frameDir, 'frame_%06d.png')
    ];

    // Add audio input if provided
    if (audioPath) {
      // Convert file:// URL to local path if needed
      const audioFile = audioPath.startsWith('file://')
        ? audioPath.substring(7)
        : audioPath;
      args.push('-i', audioFile);
    }

    // Video encoding options
    args.push(
      '-c:v', this.config.codec,
      '-b:v', this.config.bitrate
    );

    // VP9 specific options
    if (this.config.codec === 'libvpx-vp9') {
      args.push('-auto-alt-ref', '0');
    }

    // Audio encoding if audio was provided
    if (audioPath) {
      args.push('-c:a', this.config.audioCodec);
      // Sync video to audio length
      args.push('-shortest');
    }

    // Output options
    args.push(
      '-y', // Overwrite output file
      outputPath
    );

    return args;
  }

  /**
   * Create video from buffer array
   * @param {Buffer[]} frames - Array of frame buffers
   * @param {string} outputPath - Output video file path
   * @param {number} fps - Frames per second
   * @param {string|null} audioPath - Optional audio file path
   * @returns {Promise<void>}
   */
  async encodeFromBuffers(frames, outputPath, fps, audioPath = null) {
    // Create temporary directory for frames
    const tempDir = path.join(path.dirname(outputPath), `frames_${Date.now()}`);
    fs.mkdirSync(tempDir, { recursive: true });

    try {
      // Write frames to disk
      for (let i = 0; i < frames.length; i++) {
        const framePath = path.join(tempDir, `frame_${i.toString().padStart(6, '0')}.png`);
        fs.writeFileSync(framePath, frames[i]);
      }

      // Encode video
      await this.encodeFromFrames(tempDir, outputPath, fps, audioPath);

    } finally {
      // Cleanup temp directory
      this.cleanupDirectory(tempDir);
    }
  }

  /**
   * Get video codec options for specific formats
   * @param {string} format - Video format (webm, mp4, etc.)
   * @returns {Object} Codec configuration
   */
  static getCodecForFormat(format) {
    const codecs = {
      webm: { codec: 'libvpx-vp9', audioCodec: 'libopus' },
      mp4: { codec: 'libx264', audioCodec: 'aac' },
      avi: { codec: 'libx264', audioCodec: 'mp3' }
    };
    return codecs[format] || codecs.webm;
  }

  getFileSize(filePath) {
    try {
      const stats = fs.statSync(filePath);
      const sizeKB = (stats.size / 1024).toFixed(2);
      return `${sizeKB} KB`;
    } catch (error) {
      return 'unknown';
    }
  }

  cleanupDirectory(dirPath) {
    try {
      if (fs.existsSync(dirPath)) {
        fs.rmSync(dirPath, { recursive: true, force: true });
        this.logger.log('Cleaned up temporary directory:', dirPath);
      }
    } catch (error) {
      this.logger.warn('Failed to cleanup directory:', dirPath, error.message);
    }
  }
}

export default VideoEncoder;
