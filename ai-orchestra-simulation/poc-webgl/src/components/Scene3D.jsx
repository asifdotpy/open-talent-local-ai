/**
 * Scene3D Component - Lazy-loaded 3D Scene
 * Contains all Three.js and R3F logic for code splitting
 */

import { ContactShadows, Environment, OrbitControls, Stage } from '@react-three/drei';
import { Canvas } from '@react-three/fiber';
import { useControls } from 'leva';
import { Suspense, useEffect, useRef, useState } from 'react';
import { RPMAvatar } from '../components/Avatar.jsx';
import { useInterviewStore } from '../stores/interviewStore';
import { PerformanceMonitor, PerformanceStats } from './PerformanceMonitor.jsx';

// ============================================================================
// AUDIO PLAYER - Synced with Avatar
// ============================================================================

function AudioPlayer() {
  const audioRef = useRef();
  const audioData = useInterviewStore(state => state.audioData);
  const setAudioTime = useInterviewStore(state => state.setAudioTime);
  const stopSpeaking = useInterviewStore(state => state.stopSpeaking);

  useEffect(() => {
    if (!audioData || !audioRef.current) return;

    // Convert base64 to blob
    const byteCharacters = atob(audioData);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'audio/wav' });
    const url = URL.createObjectURL(blob);

    audioRef.current.src = url;
    audioRef.current.play();

    return () => URL.revokeObjectURL(url);
  }, [audioData]);

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setAudioTime(audioRef.current.currentTime);
    }
  };

  const handleEnded = () => {
    stopSpeaking();
  };

  return (
    <audio
      ref={audioRef}
      onTimeUpdate={handleTimeUpdate}
      onEnded={handleEnded}
      style={{ display: 'none' }}
    />
  );
}

// ============================================================================
// 3D SCENE COMPONENT
// ============================================================================

export default function Scene3D() {
  // Get current avatar from store
  const currentAvatar = useInterviewStore(state => state.currentAvatar);

  // Performance monitoring state
  const [performance, setPerformance] = useState(null);

  // Dev controls (Leva) - removed avatarUrl since we use store now
  const { environmentPreset, intensity } = useControls({
    environmentPreset: {
      value: 'city',
      options: ['sunset', 'dawn', 'night', 'warehouse', 'forest', 'apartment', 'studio', 'city', 'park', 'lobby'],
      label: 'Environment'
    },
    intensity: { value: 0.6, min: 0, max: 2, step: 0.1, label: 'Light Intensity' }
  });

  // Extract status values to avoid calling hooks in JSX
  const isAvatarSpeaking = useInterviewStore(state => state.isAvatarSpeaking);
  const phonemesLength = useInterviewStore(state => state.phonemes.length);

  // Show loading state if no avatar is available yet
  if (!currentAvatar) {
    return (
      <div style={{
        width: '100vw',
        height: '100vh',
        background: '#1a1a1a',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '24px'
      }}>
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mb-4"></div>
        <p>Loading RPM Avatars...</p>
        <p className="text-sm text-gray-400 mt-2">Check console for initialization logs</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#1a1a1a' }}>
      <AudioPlayer />

      <Canvas shadows camera={{ position: [0, 1.5, 2.5], fov: 35 }}>
        <Suspense fallback={null}>
          {/* Performance monitoring */}
          <PerformanceMonitor onPerformanceUpdate={setPerformance} />

          {/* Environment lighting */}
          <Environment preset={environmentPreset} />

          {/* Stage with avatar */}
          <Stage intensity={intensity} shadows="contact">
            <RPMAvatar avatarUrl={currentAvatar.url} />
          </Stage>

          {/* Camera controls */}
          <OrbitControls
            enableZoom={true}
            enablePan={false}
            minDistance={1.5}
            maxDistance={5}
            target={[0, 1.5, 0]}
          />

          {/* Contact shadows for realism */}
          <ContactShadows
            position={[0, 0, 0]}
            opacity={0.4}
            scale={10}
            blur={2.5}
            far={4}
          />
        </Suspense>
      </Canvas>

      {/* Performance stats overlay */}
      <PerformanceStats performance={performance} />

      {/* Status indicator */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 20,
        background: 'rgba(0,0,0,0.8)',
        padding: '10px 15px',
        borderRadius: '8px',
        color: 'white',
        fontSize: '12px'
      }}>
        <div>Avatar: {currentAvatar.name}</div>
        <div>Status: {isAvatarSpeaking ? 'Speaking' : 'Idle'}</div>
        <div>Phonemes: {phonemesLength}</div>
      </div>
    </div>
  );
}

// Export AudioPlayer for use in main App
export { AudioPlayer };
