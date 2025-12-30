import { useEffect, useRef } from 'react';

const WS_URL = process.env.REACT_APP_SCOUT_COORDINATOR_WS_URL || 'ws://localhost:8090/ws';

export function useWebSocket(onMessage: (message: any) => void) {
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        const connect = () => {
            console.log('Connecting to WebSocket...');
            ws.current = new WebSocket(WS_URL);

            ws.current.onopen = () => {
                console.log('WebSocket connected');
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    onMessage(data);
                } catch (error) {
                    console.error('WebSocket message parsing error:', error);
                }
            };

            ws.current.onclose = () => {
                console.log('WebSocket disconnected. Retrying in 5s...');
                setTimeout(connect, 5000);
            };

            ws.current.onerror = (error) => {
                console.error('WebSocket error:', error);
                ws.current?.close();
            };
        };

        connect();

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [onMessage]);

    return ws.current;
}
