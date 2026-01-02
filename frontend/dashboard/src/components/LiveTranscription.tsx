import { Mic, MicOff, Volume2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { TranscriptionSegment } from '../services/transcriptionWebSocket';
import { useTranscriptionWebSocket } from '../services/transcriptionWebSocket';

interface LiveTranscriptionProps {
  roomId: string;
  isRecording?: boolean;
  className?: string;
}

export const LiveTranscription = ({ roomId, isRecording = false, className = '' }: LiveTranscriptionProps) => {
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [isVisible, setIsVisible] = useState(true);
  const [lastActivity, setLastActivity] = useState<Date | null>(null);

  const {
    isConnected,
    isConnecting,
    segments,
    error,
    reconnect
  } = useTranscriptionWebSocket({
    roomId,
    onTranscriptionUpdate: (segment: TranscriptionSegment) => {
      setCurrentTranscript(segment.text);
      setLastActivity(new Date());

      // Auto-hide after 3 seconds of no activity if not recording
      if (!isRecording) {
        setTimeout(() => {
          const now = new Date();
          const timeSinceLastActivity = lastActivity ? now.getTime() - lastActivity.getTime() : 0;
          if (timeSinceLastActivity > 3000) {
            setCurrentTranscript('');
          }
        }, 3000);
      }
    },
    onConnectionEstablished: (connectionId: string) => {
      console.log('Transcription WebSocket connected:', connectionId);
    },
    onError: (event) => {
      console.error('Transcription WebSocket error:', event);
    },
    onClose: (event) => {
      console.log('Transcription WebSocket closed:', event.code);
    }
  });

  // Clear transcript when recording stops
  useEffect(() => {
    if (!isRecording) {
      const timeout = setTimeout(() => {
        setCurrentTranscript('');
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [isRecording]);

  // Auto-hide component after period of inactivity
  useEffect(() => {
    if (!currentTranscript && !isRecording) {
      const timeout = setTimeout(() => {
        setIsVisible(false);
      }, 1000);
      return () => clearTimeout(timeout);
    } else {
      setIsVisible(true);
    }
  }, [currentTranscript, isRecording]);

  if (!isVisible && !isRecording) {
    return null;
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {isRecording ? (
              <Mic className="h-5 w-5 text-white" />
            ) : (
              <Volume2 className="h-5 w-5 text-white opacity-75" />
            )}
            <h3 className="text-white font-semibold text-sm">
              {isRecording ? 'Live Transcription' : 'Speech Recognition'}
            </h3>
          </div>

          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {isConnecting && (
              <div className="flex items-center space-x-1">
                <div className="animate-spin rounded-full h-3 w-3 border border-white border-t-transparent"></div>
                <span className="text-white text-xs">Connecting...</span>
              </div>
            )}

            {isConnected && !isConnecting && (
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-white text-xs">Live</span>
              </div>
            )}

            {!isConnected && !isConnecting && (
              <button
                onClick={reconnect}
                className="text-white text-xs hover:text-blue-200 underline"
              >
                Reconnect
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-3">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Current Transcript */}
        <div className="min-h-[60px] flex items-center">
          {currentTranscript ? (
            <div className="flex-1">
              <p className="text-gray-800 text-lg leading-relaxed font-medium">
                {currentTranscript}
              </p>
              {isRecording && (
                <div className="flex items-center mt-2 text-blue-600">
                  <div className="animate-pulse w-2 h-2 bg-blue-600 rounded-full mr-2"></div>
                  <span className="text-sm">Listening...</span>
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              {isRecording ? (
                <div className="text-center">
                  <MicOff className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Start speaking to see live transcription</p>
                </div>
              ) : (
                <div className="text-center">
                  <Volume2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Transcription will appear here</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Recent Segments */}
        {segments.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Speech</h4>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {segments.slice(-3).map((segment, index) => (
                <div
                  key={`${segment.start_time}-${index}`}
                  className="bg-gray-50 rounded-md p-2 text-sm text-gray-600"
                >
                  <p className="font-medium">{segment.text}</p>
                  <div className="flex items-center justify-between mt-1 text-xs text-gray-400">
                    <span>{segment.confidence > 0.8 ? 'High confidence' : 'Medium confidence'}</span>
                    <span>{segment.end_time.toFixed(1)}s</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Connection Status Details */}
        {!isConnected && !isConnecting && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-yellow-800 text-sm">
              Not connected to transcription service.{' '}
              <button
                onClick={reconnect}
                className="text-yellow-700 underline hover:text-yellow-800"
              >
                Click to reconnect
              </button>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
