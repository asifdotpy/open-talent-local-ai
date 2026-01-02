import { useCallback, useEffect, useRef, useState } from 'react';

// Types for transcription
export interface TranscriptionSegment {
  text: string;
  start_time: number;
  end_time: number;
  confidence: number;
  speaker_id?: string;
  is_final: boolean;
  words?: Array<{
    word: string;
    start_time: number;
    end_time: number;
    confidence: number;
  }>;
}

export interface LiveTranscriptionUpdate {
  type: 'transcription_update';
  data: {
    room_id: string;
    session_id: string;
    participant_id: string;
    segment: TranscriptionSegment;
    timestamp: string;
  };
  timestamp: string;
}

export interface ConnectionMessage {
  type: 'connection_established';
  connection_id: string;
  room_id: string;
  timestamp: string;
}

export interface HistoryMessage {
  type: 'transcription_history';
  segments: TranscriptionSegment[];
  timestamp: string;
}

export interface PingMessage {
  type: 'ping';
  timestamp: string;
}

export interface PongMessage {
  type: 'pong';
  timestamp: string;
}

export type WebSocketMessage = LiveTranscriptionUpdate | ConnectionMessage | HistoryMessage | PingMessage | PongMessage;

export interface UseTranscriptionWebSocketOptions {
  roomId: string;
  onTranscriptionUpdate?: (segment: TranscriptionSegment) => void;
  onConnectionEstablished?: (connectionId: string) => void;
  onHistoryReceived?: (segments: TranscriptionSegment[]) => void;
  onError?: (error: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onReconnect?: () => void;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
}

export interface UseTranscriptionWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  connectionId: string | null;
  segments: TranscriptionSegment[];
  error: string | null;
  reconnect: () => void;
  sendMessage: (message: any) => void;
  close: () => void;
}

export const useTranscriptionWebSocket = ({
  roomId,
  onTranscriptionUpdate,
  onConnectionEstablished,
  onHistoryReceived,
  onError,
  onClose,
  onReconnect,
  maxReconnectAttempts = 5,
  reconnectInterval = 3000
}: UseTranscriptionWebSocketOptions): UseTranscriptionWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [segments, setSegments] = useState<TranscriptionSegment[]>([]);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    setIsConnecting(true);
    setError(null);

    try {
      const wsUrl = `ws://localhost:8004/ws/transcription/${roomId}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected for transcription:', roomId);
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttemptsRef.current = 0; // Reset reconnect attempts on successful connection
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          switch (message.type) {
            case 'connection_established':
              setConnectionId(message.connection_id);
              onConnectionEstablished?.(message.connection_id);
              break;

            case 'transcription_history':
              setSegments(message.segments);
              onHistoryReceived?.(message.segments);
              break;

            case 'transcription_update':
              const segment = message.data.segment;
              setSegments(prev => {
                // Add new segment if it's not already in the list
                const exists = prev.some(s =>
                  s.text === segment.text &&
                  Math.abs(s.start_time - segment.start_time) < 0.1
                );
                if (!exists) {
                  return [...prev, segment];
                }
                return prev;
              });
              onTranscriptionUpdate?.(segment);
              break;

            case 'ping':
              // Respond to ping with pong
              ws.send(JSON.stringify({
                type: 'pong',
                timestamp: new Date().toISOString()
              }));
              break;

            default:
              console.log('Unknown WebSocket message type:', message.type);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        setIsConnected(false);
        setIsConnecting(false);
        onError?.(event);
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        setIsConnecting(false);
        setConnectionId(null);
        wsRef.current = null;
        onClose?.(event);

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            onReconnect?.();
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
      setIsConnecting(false);
    }
  }, [roomId, onConnectionEstablished, onHistoryReceived, onTranscriptionUpdate, onError, onClose, onReconnect, maxReconnectAttempts, reconnectInterval]);

  const reconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    reconnectAttemptsRef.current = 0; // Reset attempts for manual reconnect
    if (wsRef.current) {
      wsRef.current.close();
    }
    connect();
  }, [connect]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected, cannot send message');
    }
  }, []);

  const close = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client closed connection');
    }
    setIsConnected(false);
    setIsConnecting(false);
    setConnectionId(null);
  }, []);

  // Connect when roomId changes
  useEffect(() => {
    if (roomId) {
      connect();
    }

    return () => {
      close();
    };
  }, [roomId, connect, close]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    isConnected,
    isConnecting,
    connectionId,
    segments,
    error,
    reconnect,
    sendMessage,
    close
  };
};
