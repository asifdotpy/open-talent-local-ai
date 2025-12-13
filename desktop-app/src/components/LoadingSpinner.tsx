/**
 * Loading Spinner Component
 * Displays loading state with spinner and progress information
 */

import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
  isLoading: boolean;
  message?: string;
  progress?: number; // 0-100
  cancelable?: boolean;
  onCancel?: () => void;
  size?: 'small' | 'medium' | 'large';
  overlay?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  isLoading,
  message = 'Loading...',
  progress,
  cancelable = false,
  onCancel,
  size = 'medium',
  overlay = false,
}) => {
  if (!isLoading) {
    return null;
  }

  const containerClass = `loading-spinner-container ${
    overlay ? 'overlay' : ''
  }`;
  const spinnerClass = `spinner ${size}`;

  return (
    <div className={containerClass}>
      <div className="spinner-content">
        <div className={spinnerClass}>
          <div className="spinner-circle"></div>
        </div>

        {message && <p className="spinner-message">{message}</p>}

        {progress !== undefined && (
          <div className="progress-container">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${Math.min(progress, 100)}%` }}
              ></div>
            </div>
            <p className="progress-text">{Math.round(progress)}%</p>
          </div>
        )}

        {cancelable && onCancel && (
          <button className="cancel-button" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * Loading Skeleton Component
 * Shows skeleton placeholders while loading
 */

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
  count?: number;
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '20px',
  borderRadius = '4px',
  count = 1,
  className = '',
}) => {
  return (
    <div className={`skeleton-wrapper ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="skeleton"
          style={{
            width,
            height,
            borderRadius,
            marginBottom: i < count - 1 ? '12px' : 0,
          }}
        ></div>
      ))}
    </div>
  );
};

/**
 * Loading Overlay Component
 * Full-screen loading overlay
 */

interface LoadingOverlayProps {
  isVisible: boolean;
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isVisible,
  message = 'Loading...',
}) => {
  if (!isVisible) {
    return null;
  }

  return (
    <div className="loading-overlay">
      <div className="overlay-content">
        <div className="spinner medium">
          <div className="spinner-circle"></div>
        </div>
        {message && <p className="overlay-message">{message}</p>}
      </div>
    </div>
  );
};

export default LoadingSpinner;
