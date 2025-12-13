/**
 * Avatar Display Component
 * React wrapper for Three.js avatar renderer with customization
 * Part of Day 5-6 implementation
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  avatarRenderer,
  AvatarGender,
  AvatarSkinTone,
  AvatarConfig,
  PhonemeFrame,
} from '../services/avatar-renderer';
import './AvatarDisplay.css';

interface AvatarDisplayProps {
  /**
   * Avatar configuration (gender, skin tone, etc.)
   */
  config?: Partial<AvatarConfig>;

  /**
   * Show customization controls
   */
  showControls?: boolean;

  /**
   * Callback when avatar is customized
   */
  onCustomize?: (config: AvatarConfig) => void;

  /**
   * Callback for recording status
   */
  recordingStatus?: 'idle' | 'recording' | 'transcribing' | 'playback';

  /**
   * Phoneme frames for lip-sync animation
   */
  phonemeFrames?: PhonemeFrame[];

  /**
   * Auto-start playback after rendering
   */
  autoPlay?: boolean;

  /**
   * Show waveform visualization during recording
   */
  showWaveform?: boolean;

  /**
   * Audio level (0-100) for visualization
   */
  audioLevel?: number;
}

const GENDER_OPTIONS = [
  { value: AvatarGender.MALE, label: '👨 Male' },
  { value: AvatarGender.FEMALE, label: '👩 Female' },
  { value: AvatarGender.NEUTRAL, label: '🧑 Neutral' },
];

const SKIN_TONE_OPTIONS = [
  { value: AvatarSkinTone.LIGHT, label: 'Light' },
  { value: AvatarSkinTone.MEDIUM, label: 'Medium' },
  { value: AvatarSkinTone.DARK, label: 'Dark' },
  { value: AvatarSkinTone.VERY_DARK, label: 'Very Dark' },
];

export const AvatarDisplay: React.FC<AvatarDisplayProps> = ({
  config: externalConfig,
  showControls = true,
  onCustomize,
  recordingStatus = 'idle',
  phonemeFrames,
  autoPlay = false,
  showWaveform = true,
  audioLevel = 0,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [initialized, setInitialized] = useState(false);
  const [config, setConfig] = useState<AvatarConfig>({
    gender: AvatarGender.FEMALE,
    skinTone: AvatarSkinTone.MEDIUM,
    ...externalConfig,
  });
  const [isAnimating, setIsAnimating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize avatar renderer
  useEffect(() => {
    const initializeAvatar = async () => {
      try {
        if (!canvasRef.current) {
          throw new Error('Canvas element not found');
        }

        // Initialize renderer
        await avatarRenderer.initialize(config);
        setInitialized(true);
        setError(null);

        console.log('✅ Avatar initialized:', config);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to initialize avatar';
        setError(errorMsg);
        console.error('Avatar initialization error:', err);
      }
    };

    initializeAvatar();

    // Cleanup
    return () => {
      try {
        avatarRenderer.dispose();
      } catch (err) {
        console.error('Avatar cleanup error:', err);
      }
    };
  }, []);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (!canvasRef.current || !containerRef.current) return;

      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;

      canvasRef.current.width = width;
      canvasRef.current.height = height;
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Update avatar configuration
  useEffect(() => {
    if (!initialized) return;

    const updateConfig = async () => {
      try {
        // Re-initialize with new config
        await avatarRenderer.initialize(config);
        onCustomize?.(config);
        console.log('✅ Avatar updated:', config);
      } catch (err) {
        console.error('Avatar update error:', err);
      }
    };

    updateConfig();
  }, [config]);

  // Handle lip-sync animation with phoneme frames
  useEffect(() => {
    if (!initialized || !phonemeFrames || phonemeFrames.length === 0) return;

    const playLipSync = async () => {
      try {
        setIsAnimating(true);
        await avatarRenderer.playLipSyncAnimation(phonemeFrames);
        setIsAnimating(false);
      } catch (err) {
        console.error('Lip-sync error:', err);
        setIsAnimating(false);
      }
    };

    if (autoPlay) {
      playLipSync();
    }
  }, [phonemeFrames, autoPlay, initialized]);

  // Animate based on recording status
  useEffect(() => {
    if (!initialized) return;

    const updateExpression = async () => {
      try {
        // Avatar rendering updates automatically based on playback
        // No expression update needed
      } catch (err) {
        console.error('Expression update error:', err);
      }
    };

    updateExpression();
  }, [recordingStatus, initialized]);

  const handleGenderChange = (gender: AvatarGender) => {
    setConfig((prev) => ({
      ...prev,
      gender,
    }));
  };

  const handleSkinToneChange = (skinTone: AvatarSkinTone) => {
    setConfig((prev) => ({
      ...prev,
      skinTone,
    }));
  };

  const handleHeadScaleChange = (scale: number) => {
    // Not implemented in current avatar renderer
    // Can be extended in future versions
  };

  const handleResetAvatar = async () => {
    try {
      setConfig({
        gender: AvatarGender.FEMALE,
        skinTone: AvatarSkinTone.MEDIUM,
      });
      setError(null);
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  return (
    <div className="avatar-display">
      {error && (
        <div className="avatar-error">
          <p>❌ {error}</p>
        </div>
      )}

      <div className="avatar-container" ref={containerRef}>
        <canvas
          ref={canvasRef}
          className="avatar-canvas"
          style={{
            width: '100%',
            height: '100%',
            display: initialized ? 'block' : 'none',
          }}
        />

        {!initialized && (
          <div className="avatar-loading">
            <div className="spinner"></div>
            <p>Loading Avatar...</p>
          </div>
        )}

        {showWaveform && recordingStatus !== 'idle' && (
          <div className="waveform-overlay">
            <div className="waveform-bars">
              {Array.from({ length: 12 }).map((_, i) => (
                <div
                  key={i}
                  className="waveform-bar"
                  style={{
                    height: `${Math.max(10, (audioLevel * (i + 1)) / 12)}%`,
                    animation: `pulse-bar 0.1s ease-out ${i * 0.05}s`,
                  }}
                />
              ))}
            </div>

            <div className="recording-badge">
              {recordingStatus === 'recording' && (
                <>
                  <span className="pulse-dot"></span>
                  Recording...
                </>
              )}
              {recordingStatus === 'transcribing' && (
                <>
                  <span className="spinner-small"></span>
                  Transcribing...
                </>
              )}
              {recordingStatus === 'playback' && (
                <>
                  <span className="play-indicator">▶</span>
                  Playing Back...
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Customization Controls */}
      {showControls && initialized && (
        <div className="avatar-controls">
          <div className="control-group">
            <label>Avatar Gender:</label>
            <div className="gender-selector">
              {GENDER_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  className={`gender-btn ${config.gender === option.value ? 'active' : ''}`}
                  onClick={() => handleGenderChange(option.value)}
                  title={option.label}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div className="control-group">
            <label>Skin Tone:</label>
            <div className="skin-tone-selector">
              {SKIN_TONE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  className={`skin-tone-btn ${config.skinTone === option.value ? 'active' : ''}`}
                  onClick={() => handleSkinToneChange(option.value)}
                  style={{
                    backgroundColor: getSkinTonePreviewColor(option.value),
                  }}
                  title={option.label}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div className="control-group">
            <label>Head Size:</label>
            <div className="scale-slider">
              <input
                type="range"
                min="0.8"
                max="1.2"
                step="0.1"
                value={1}
                onChange={(e) => handleHeadScaleChange(parseFloat(e.target.value))}
                disabled
              />
              <span className="scale-value">1.0x</span>
            </div>
            <small>(Fixed in current version)</small>
          </div>

          <div className="control-group">
            <button className="btn-reset" onClick={handleResetAvatar}>
              🔄 Reset Avatar
            </button>
          </div>

          {isAnimating && (
            <div className="animation-indicator">
              <span className="pulse-dot"></span>
              Animating...
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * Get preview color for skin tone
 */
function getSkinTonePreviewColor(skinTone: AvatarSkinTone): string {
  const toneMap: Record<AvatarSkinTone, string> = {
    [AvatarSkinTone.LIGHT]: '#f4a882',
    [AvatarSkinTone.MEDIUM]: '#c68642',
    [AvatarSkinTone.DARK]: '#8b6914',
    [AvatarSkinTone.VERY_DARK]: '#4a3728',
  };
  return toneMap[skinTone] || '#c68642';
}

export default AvatarDisplay;
