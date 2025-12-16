# Session-based FastAPI WebSocket signaling server for WebRTC
# Orchestrates browser <-> voice-service negotiation with targeted routing

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class PeerType(str, Enum):
    CLIENT = "client"          # Browser client
    VOICE_SERVICE = "voice"    # Voice processing service
    AVATAR_SERVICE = "avatar"  # Avatar rendering service (future)

@dataclass
class Peer:
    ws: WebSocket
    peer_type: PeerType
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# Session registry: session_id -> {client, voice_service, avatar_service}
sessions: Dict[str, Dict[PeerType, Peer]] = {}

# Peer lookup: ws object -> Peer
peers_by_ws: Dict[WebSocket, Peer] = {}

@app.get("/webrtc/info")
def info():
    """Return signaling server status and session count"""
    return {
        "status": "ok",
        "sessions": len(sessions),
        "total_peers": len(peers_by_ws)
    }

@app.websocket("/webrtc/signal")
async def websocket_endpoint(ws: WebSocket):
    """
    Main signaling endpoint with session-based routing.
    
    Expected first message: {"type": "register", "peer_type": "client"|"voice", "session_id": "...", ...}
    Subsequent messages are routed based on session and peer type.
    """
    await ws.accept()
    peer: Optional[Peer] = None
    
    try:
        # First message must be registration
        reg_msg = await ws.receive_json()
        
        if reg_msg.get("type") != "register":
            await ws.send_json({"type": "error", "message": "First message must be registration"})
            await ws.close()
            return
        
        peer_type_str = reg_msg.get("peer_type")
        session_id = reg_msg.get("session_id")
        
        if not peer_type_str or not session_id:
            await ws.send_json({"type": "error", "message": "Missing peer_type or session_id"})
            await ws.close()
            return
        
        try:
            peer_type = PeerType(peer_type_str)
        except ValueError:
            await ws.send_json({"type": "error", "message": f"Invalid peer_type: {peer_type_str}"})
            await ws.close()
            return
        
        # Create peer and register
        peer = Peer(
            ws=ws,
            peer_type=peer_type,
            session_id=session_id,
            metadata=reg_msg.get("metadata", {})
        )
        
        if session_id not in sessions:
            sessions[session_id] = {}
        
        sessions[session_id][peer_type] = peer
        peers_by_ws[ws] = peer
        
        logger.info(f"Peer registered: session={session_id}, type={peer_type}")
        
        # Acknowledge registration
        await ws.send_json({
            "type": "registered",
            "session_id": session_id,
            "peer_type": peer_type.value
        })
        
        # Main signaling loop
        while True:
            data = await ws.receive_json()
            await route_message(peer, data)
            
    except WebSocketDisconnect:
        logger.info(f"Peer disconnected: {peer.session_id if peer else 'unknown'}")
    except Exception as e:
        logger.error(f"Signaling error: {e}")
    finally:
        # Clean up peer
        if peer:
            peers_by_ws.pop(ws, None)
            if peer.session_id in sessions:
                sessions[peer.session_id].pop(peer.peer_type, None)
                if not sessions[peer.session_id]:
                    sessions.pop(peer.session_id)

async def route_message(sender: Peer, message: Dict[str, Any]):
    """
    Route signaling messages between peers in the same session.
    
    Client -> Voice Service: offer, ice_candidate
    Voice Service -> Client: answer, ice_candidate
    """
    msg_type = message.get("type")
    session = sessions.get(sender.session_id)
    
    if not session:
        logger.warning(f"No session found for {sender.session_id}")
        return
    
    # Determine target peer(s)
    targets = []
    
    if sender.peer_type == PeerType.CLIENT:
        # Client messages go to voice service (and potentially avatar service)
        if PeerType.VOICE_SERVICE in session:
            targets.append(session[PeerType.VOICE_SERVICE])
        # Future: add avatar service routing
        
    elif sender.peer_type == PeerType.VOICE_SERVICE:
        # Voice service messages go to client
        if PeerType.CLIENT in session:
            targets.append(session[PeerType.CLIENT])
    
    # Forward message to target(s)
    for target in targets:
        try:
            await target.ws.send_json(message)
            logger.debug(f"Routed {msg_type} from {sender.peer_type} to {target.peer_type}")
        except Exception as e:
            logger.error(f"Failed to route message: {e}")

# Production notes:
# - Add authentication/authorization before registration
# - Implement session timeout and cleanup
# - Add rate limiting per peer
# - Consider using Redis for multi-instance deployment
# - Add prometheus metrics for monitoring

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
