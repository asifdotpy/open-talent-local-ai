/**
 * OpenTalent React Three Fiber Avatar POC
 *
 * Integrates:
 * - React Three Fiber (declarative 3D)
 * - Ready Player Me (avatars with ARKit blend shapes)
 * - Drei (helper components)
 * - Zustand (state management)
 * - Leva (dev controls)
 *
 * Architecture:
 * - Leverages existing avatar-renderer-v2.js modular structure
 * - Client-side GPU rendering (60 FPS)
 * - Server-side TTS + phoneme extraction
 * - Real-time lip-sync with ARKit morph targets
 */

import { lazy, Suspense, useEffect, useState } from 'react';
import { AvatarSelector } from './components/AvatarSelector.jsx';
import { useInterviewStore } from './stores/interviewStore';

// Lazy load the 3D scene to enable code splitting
const Scene3D = lazy(() => import('./components/Scene3D.jsx'));

// ============================================================================
// CONTROLS - Interview Interface
// ============================================================================

function Controls() {
  const [questionText, setQuestionText] = useState(
    "Tell me about your experience with JavaScript and React. What projects have you worked on recently?"
  );
  const isAvatarSpeaking = useInterviewStore(state => state.isAvatarSpeaking);
  const speakQuestion = useInterviewStore(state => state.speakQuestion);
  const stopSpeaking = useInterviewStore(state => state.stopSpeaking);

  const handleSpeak = async () => {
    try {
      await speakQuestion(questionText);
    } catch (error) {
      alert('Failed to generate speech. Make sure voice service is running on port 8002.');
    }
  };

  return (
    <div style={{
      position: 'absolute',
      top: 20,
      left: 20,
      right: 20,
      background: 'rgba(0,0,0,0.8)',
      padding: '20px',
      borderRadius: '12px',
      color: 'white',
      zIndex: 1000,
      maxHeight: '80vh',
      overflowY: 'auto'
    }}>
      <h2 style={{ margin: '0 0 15px 0', fontSize: '24px' }}>
        OpenTalent Interview Avatar
      </h2>

      {/* Avatar Selector */}
      <div style={{ marginBottom: '20px' }}>
        <AvatarSelector />
      </div>

      <textarea
        value={questionText}
        onChange={(e) => setQuestionText(e.target.value)}
        disabled={isAvatarSpeaking}
        style={{
          width: '100%',
          minHeight: '80px',
          padding: '10px',
          marginBottom: '10px',
          borderRadius: '6px',
          background: '#1a1a1a',
          color: 'white',
          border: '1px solid #444',
          fontSize: '14px',
          fontFamily: 'inherit',
          resize: 'vertical'
        }}
      />

      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={handleSpeak}
          disabled={isAvatarSpeaking}
          style={{
            padding: '12px 24px',
            background: isAvatarSpeaking
              ? '#444'
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isAvatarSpeaking ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '600'
          }}
        >
          {isAvatarSpeaking ? '🎤 Speaking...' : '🎤 Speak Question'}
        </button>

        <button
          onClick={stopSpeaking}
          disabled={!isAvatarSpeaking}
          style={{
            padding: '12px 24px',
            background: '#444',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: !isAvatarSpeaking ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '600'
          }}
        >
          ⏹️ Stop
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN APP
// ============================================================================

export default function App() {
  const connectWebSocket = useInterviewStore(state => state.connectWebSocket);

  // Initialize WebSocket connection on mount
  useEffect(() => {
    console.log('🚀 Initializing R3F Avatar App...');
    connectWebSocket();

    // Cleanup on unmount
    return () => {
      const disconnectWebSocket = useInterviewStore.getState().disconnectWebSocket;
      disconnectWebSocket();
    };
  }, [connectWebSocket]);

  return (
    <Suspense fallback={
      <div style={{
        width: '100vw',
        height: '100vh',
        background: '#1a1a1a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '24px'
      }}>
        Loading 3D Avatar System...
      </div>
    }>
      <Controls />
      <Scene3D />
    </Suspense>
  );
}
