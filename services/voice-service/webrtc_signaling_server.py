#!/usr/bin/env python3
"""Simple WebRTC Signaling Server for Voice Service Testing
Provides WebSocket signaling for WebRTC connections during testing.
"""

import logging
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebRTC Signaling Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected clients by session_id and peer_type
connected_clients: dict[str, dict[str, WebSocket]] = {}


@app.websocket("/webrtc/signal")
async def signaling_endpoint(websocket: WebSocket):
    """WebRTC signaling endpoint for peer-to-peer connections."""
    await websocket.accept()

    session_id = None
    peer_type = None

    try:
        # Wait for registration message
        registration_msg = await websocket.receive_json()
        if registration_msg.get("type") != "register":
            await websocket.send_json({"type": "error", "message": "Must register first"})
            return

        session_id = registration_msg.get("session_id")
        peer_type = registration_msg.get("peer_type")

        if not session_id or not peer_type:
            await websocket.send_json({"type": "error", "message": "Missing session_id or peer_type"})
            return

        # Register client
        if session_id not in connected_clients:
            connected_clients[session_id] = {}

        connected_clients[session_id][peer_type] = websocket

        # Send registration acknowledgment
        await websocket.send_json({"type": "registered", "session_id": session_id, "peer_type": peer_type})

        logger.info(f"Client registered: session={session_id}, type={peer_type}")

        # Check if we have both client and voice peers for this session
        if len(connected_clients[session_id]) >= 2:
            logger.info(f"Both peers connected for session {session_id}")

        # Handle signaling messages
        while True:
            try:
                message = await websocket.receive_json()
                await handle_signaling_message(session_id, peer_type, message)
            except WebSocketDisconnect:
                break

    except Exception as e:
        logger.error(f"Signaling error: {e}")
    finally:
        # Clean up on disconnect
        if session_id and peer_type:
            if session_id in connected_clients and peer_type in connected_clients[session_id]:
                del connected_clients[session_id][peer_type]
                if not connected_clients[session_id]:
                    del connected_clients[session_id]
                logger.info(f"Client disconnected: session={session_id}, type={peer_type}")


async def handle_signaling_message(session_id: str, sender_type: str, message: dict):
    """Forward signaling messages between peers."""
    try:
        msg_type = message.get("type")

        # Determine recipient type
        if sender_type == "client":
            recipient_type = "voice"
        elif sender_type == "voice":
            recipient_type = "client"
        else:
            logger.warning(f"Unknown sender type: {sender_type}")
            return

        # Check if recipient exists
        if session_id not in connected_clients or recipient_type not in connected_clients[session_id]:
            logger.warning(f"No recipient found for session {session_id}, type {recipient_type}")
            return

        recipient_ws = connected_clients[session_id][recipient_type]

        # Forward the message
        await recipient_ws.send_json(message)

        logger.debug(f"Forwarded {msg_type} from {sender_type} to {recipient_type} for session {session_id}")

    except Exception as e:
        logger.error(f"Error handling signaling message: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "webrtc-signaling",
        "active_sessions": len(connected_clients),
        "total_clients": sum(len(clients) for clients in connected_clients.values()),
    }


@app.get("/sessions")
async def list_sessions():
    """List active sessions."""
    return {
        "sessions": [
            {"session_id": session_id, "clients": list(clients.keys()), "count": len(clients)}
            for session_id, clients in connected_clients.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("SIGNALING_PORT", "8005"))
    host = os.getenv("SIGNALING_HOST", "0.0.0.0")

    logger.info(f"Starting WebRTC Signaling Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
