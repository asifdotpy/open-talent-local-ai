/**
 * Error Boundary Component
 * Catches React errors and displays user-friendly error UI
 */

import React, { ReactNode } from 'react';
import { AppError, ErrorHandler } from '../utils/error-handler';

interface Props {
  children: ReactNode;
  fallback?: (error: AppError, resetError: () => void) => ReactNode;
  onError?: (error: AppError) => void;
}

interface State {
  error: AppError | null;
  errorInfo: React.ErrorInfo | null;
  hasError: boolean;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      error: null,
      errorInfo: null,
      hasError: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Handle error
    const appError = ErrorHandler.handleError(
      error,
      'React Error Boundary'
    );

    // Log error details
    ErrorHandler.logError(appError);

    // Call error callback if provided
    if (this.props.onError) {
      this.props.onError(appError);
    }

    // Update state
    this.setState({
      error: appError,
      errorInfo,
      hasError: true,
    });

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by Error Boundary:', error);
      console.error('Error Info:', errorInfo);
    }
  }

  resetError = () => {
    this.setState({
      error: null,
      errorInfo: null,
      hasError: false,
    });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.resetError);
      }

      // Default error UI
      return (
        <div style={styles.container}>
          <div style={styles.errorBox}>
            <h1 style={styles.title}>⚠️ Something went wrong</h1>
            <p style={styles.message}>
              {this.state.error.getUserMessage()}
            </p>

            {process.env.NODE_ENV === 'development' && (
              <details style={styles.details}>
                <summary style={styles.summary}>
                  Technical Details (Development Only)
                </summary>
                <pre style={styles.pre}>
                  {this.state.error.getTechnicalDetails()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            <div style={styles.buttons}>
              <button
                onClick={this.resetError}
                style={styles.primaryButton}
              >
                Try Again
              </button>
              <button
                onClick={() => window.location.reload()}
                style={styles.secondaryButton}
              >
                Reload Page
              </button>
            </div>

            <p style={styles.help}>
              If the problem persists, please try restarting the application or
              contact support.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '20px',
  },
  errorBox: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '32px',
    maxWidth: '600px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    textAlign: 'center',
  },
  title: {
    marginTop: 0,
    color: '#d32f2f',
    fontSize: '24px',
    fontWeight: 'bold',
  },
  message: {
    color: '#555',
    fontSize: '16px',
    lineHeight: '1.5',
    marginBottom: '24px',
  },
  details: {
    marginBottom: '24px',
    textAlign: 'left',
  },
  summary: {
    cursor: 'pointer',
    color: '#1976d2',
    fontSize: '14px',
    fontWeight: '500',
    padding: '8px',
    marginBottom: '8px',
    borderRadius: '4px',
    backgroundColor: '#f0f0f0',
  },
  pre: {
    backgroundColor: '#f5f5f5',
    padding: '12px',
    borderRadius: '4px',
    fontSize: '12px',
    overflow: 'auto',
    maxHeight: '200px',
    color: '#333',
  },
  buttons: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
    marginBottom: '20px',
  },
  primaryButton: {
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'background-color 0.3s',
  },
  secondaryButton: {
    backgroundColor: '#e0e0e0',
    color: '#333',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'background-color 0.3s',
  },
  help: {
    color: '#888',
    fontSize: '14px',
    fontStyle: 'italic',
    margin: '0',
  },
};

export default ErrorBoundary;
