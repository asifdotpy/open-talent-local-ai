// WebRTCClient.js
// Minimal WebRTC client for mic-to-service and service-to-browser audio

import { AppConfig } from '../config/AppConfig.js';

export class WebRTCClient {
  constructor({ sessionId, onRemoteAudio, onDataMessage, log = console }) {
    this.config = AppConfig.get();
    this.sessionId = sessionId || `session-${Date.now()}`;
    this.pc = null;
    this.ws = null;
    this.log = log;
    this.onRemoteAudio = onRemoteAudio;
    this.onDataMessage = onDataMessage;
    this.localStream = null;
    this.dataChannel = null;
    this.registered = false;
  }

  async start() {
    await this._connectSignaling();
    await this._registerPeer();

    const { iceServers } = this.config.webrtc || { iceServers: [] };
    this.pc = new RTCPeerConnection({ iceServers });

    this.pc.onicecandidate = (e) => {
      if (e.candidate) {
        this._send({ 
          type: 'ice_candidate', 
          candidate: {
            candidate: e.candidate.candidate,
            sdpMid: e.candidate.sdpMid,
            sdpMLineIndex: e.candidate.sdpMLineIndex
          }
        });
      }
    };

    this.pc.ontrack = (e) => {
      // First audio track from service (TTS/processed audio)
      if (this.onRemoteAudio) {
        this.onRemoteAudio(e.streams[0]);
      }
    };

    this.pc.ondatachannel = (e) => {
      const channel = e.channel;
      channel.onmessage = (msg) => {
        try {
          const json = JSON.parse(msg.data);
          this.onDataMessage && this.onDataMessage(json);
        } catch (_) {
          this.onDataMessage && this.onDataMessage({ type: 'text', data: msg.data });
        }
      };
    };

    // Create our outbound data channel for control/transcripts
    this.dataChannel = this.pc.createDataChannel('talentai');

    // Check if microphone capture is enabled (for lip-sync testing, we may not need it)
    const enableMicrophone = this.config.features?.enableMicrophoneCapture !== false;

    if (enableMicrophone) {
      // Capture microphone for bidirectional audio
      this.localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      for (const track of this.localStream.getAudioTracks()) {
        this.pc.addTrack(track, this.localStream);
      }
      this.log.info('Microphone access granted for WebRTC');
    } else {
      // Create offer without local audio tracks (receive-only mode for lip-sync testing)
      this.log.info('Microphone capture disabled - receive-only WebRTC mode for lip-sync testing');
    }

    const offer = await this.pc.createOffer({ offerToReceiveAudio: true, offerToReceiveVideo: false });
    await this.pc.setLocalDescription(offer);
    this._send({ type: 'offer', sdp: offer.sdp });
  }

  async _registerPeer() {
    // Register as client peer with session ID
    this._send({
      type: 'register',
      peer_type: 'client',
      session_id: this.sessionId,
      metadata: {
        userAgent: navigator.userAgent,
        timestamp: Date.now()
      }
    });

    // Wait for registration confirmation
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Registration timeout'));
      }, 5000);

      const originalOnMessage = this.ws.onmessage;
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'registered') {
          clearTimeout(timeout);
          this.registered = true;
          this.log.info('WebRTC client registered:', msg);
          this.ws.onmessage = originalOnMessage;
          resolve();
        } else if (msg.type === 'error') {
          clearTimeout(timeout);
          reject(new Error(msg.message));
        }
      };
    });
  }

  async stop() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.pc) {
      this.pc.close();
      this.pc = null;
    }
    if (this.localStream) {
      this.localStream.getTracks().forEach((t) => t.stop());
      this.localStream = null;
    }
  }

  async _connectSignaling() {
    const url = (this.config.webrtc && this.config.webrtc.signalingUrl) || 'ws://localhost:8004/webrtc/signal';
    this.ws = new WebSocket(url);
    this.ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'answer') {
        await this.pc.setRemoteDescription({ type: 'answer', sdp: msg.sdp });
      } else if (msg.type === 'ice_candidate') {
        const candidate = new RTCIceCandidate({
          candidate: msg.candidate.candidate,
          sdpMid: msg.candidate.sdpMid,
          sdpMLineIndex: msg.candidate.sdpMLineIndex
        });
        await this.pc.addIceCandidate(candidate);
      } else if (msg.type === 'message') {
        this.onDataMessage && this.onDataMessage(msg.payload);
      }
    };
    await new Promise((resolve) => (this.ws.onopen = resolve));
  }

  _send(obj) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(obj));
    }
  }

  sendData(payload) {
    if (this.dataChannel && this.dataChannel.readyState === 'open') {
      this.dataChannel.send(JSON.stringify(payload));
    }
  }
}
