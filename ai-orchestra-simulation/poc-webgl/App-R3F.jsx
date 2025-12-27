/**
 * OpenTalent React Three Fiber Avatar POC - Professional Interviewer Interface
 *
 * TRANSFORMATION: From interactive 3D demo to professional interviewer interface
 *
 * Key Changes:
 * - Fixed camera position (no OrbitControls) for headshot-style view
 * - Professional UI with centered bottom controls
 * - Studio lighting setup for professional appearance
 * - Avatar positioned for direct front view like an interviewer
 * - Light background and refined styling
 *
 * Reference: Professional headshot style with approachable, confident presentation
 *
 * Integrates:
 * - React Three Fiber (declarative 3D)
 * - Ready Player Me (avatars with ARKit blend shapes)
 * - Drei (helper components)
 * - Zustand (state management)
 * - Leva (dev controls - disabled in production)
 *
 * Architecture:
 * - Leverages existing avatar-renderer-v2.js modular structure
 * - Client-side GPU rendering (60 FPS)
 * - Server-side TTS + phoneme extraction
 * - Real-time lip-sync with ARKit morph targets
 */

import { ContactShadows, Environment, useGLTF } from '@react-three/drei';
import { Canvas, useFrame } from '@react-three/fiber';
import { useControls } from 'leva';
import { Suspense, useEffect, useRef, useState } from 'react';
import create from 'zustand';

// ============================================================================
// ZUSTAND STORE - Global State Management
// ============================================================================

const useInterviewStore = create((set, get) => ({
  // State
  currentQuestion: null,
  isAvatarSpeaking: false,
  phonemes: [],
  audioData: null,
  audioTime: 0,
  duration: 0,

  // Actions
  setPhonemes: (phonemes) => set({ phonemes }),
  setAudioData: (audioData) => set({ audioData }),
  setAudioTime: (time) => set({ audioTime: time }),
  setDuration: (duration) => set({ duration }),

  speakQuestion: async (text) => {
    set({ isAvatarSpeaking: true, currentQuestion: text });

    try {
      const response = await fetch('http://localhost:8002/voice/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          voice: 'en-US',
          extract_phonemes: true
        })
      });

      if (!response.ok) {
        throw new Error(`Voice service error: ${response.status}`);
      }

      const data = await response.json();

      set({
        phonemes: data.phonemes,
        audioData: data.audio_data,
        duration: data.duration
      });

      return data;
    } catch (error) {
      console.error('Failed to generate speech:', error);
      set({ isAvatarSpeaking: false });
      throw error;
    }
  },

  stopSpeaking: () => set({
    isAvatarSpeaking: false,
    audioTime: 0,
    currentQuestion: null
  }),
}));

// ============================================================================
// PHONEME TO ARKIT VISEME MAPPING
// ============================================================================

/**
 * Maps CMU phonemes to ARKit blend shapes (52 morph targets)
 * Ready Player Me avatars use ARKit standard
 */
const PHONEME_TO_ARKIT_VISEME = {
  // Silence
  'sil': null,

  // Vowels → ARKit jaw/mouth shapes
  'AA': { jawOpen: 0.7, mouthOpen: 0.6 },              // "father"
  'AE': { jawOpen: 0.5, mouthOpen: 0.5 },              // "cat"
  'AH': { jawOpen: 0.4, mouthOpen: 0.4 },              // "but"
  'AO': { mouthFunnel: 0.6, jawOpen: 0.3 },            // "caught"
  'AW': { mouthFunnel: 0.5, jawOpen: 0.4 },            // "cow"
  'AY': { jawOpen: 0.6, mouthOpen: 0.5 },              // "hide"
  'EH': { mouthOpen: 0.4, mouthSmileLeft: 0.3, mouthSmileRight: 0.3 }, // "red"
  'ER': { mouthFunnel: 0.3, jawOpen: 0.2 },            // "her"
  'EY': { mouthSmileLeft: 0.5, mouthSmileRight: 0.5 }, // "ate"
  'IH': { mouthSmileLeft: 0.4, mouthSmileRight: 0.4 }, // "it"
  'IY': { mouthSmileLeft: 0.6, mouthSmileRight: 0.6 }, // "feet"
  'OW': { mouthFunnel: 0.7 },                          // "go"
  'OY': { mouthFunnel: 0.6, jawOpen: 0.3 },            // "boy"
  'UH': { mouthPucker: 0.4 },                          // "book"
  'UW': { mouthPucker: 0.7, mouthFunnel: 0.5 },        // "boot"

  // Consonants - Bilabials (lips together)
  'B': { mouthClose: 1.0 },                            // "bat"
  'P': { mouthClose: 1.0 },                            // "pat"
  'M': { mouthClose: 1.0 },                            // "mat"

  // Consonants - Labiodentals (lip to teeth)
  'F': { mouthRollLower: 0.6, mouthUpperUpLeft: 0.3, mouthUpperUpRight: 0.3 }, // "fat"
  'V': { mouthRollLower: 0.6, mouthUpperUpLeft: 0.3, mouthUpperUpRight: 0.3 }, // "vat"

  // Consonants - Dental (tongue to teeth)
  'TH': { tongueOut: 0.5, mouthOpen: 0.3 },            // "thin"
  'DH': { tongueOut: 0.5, mouthOpen: 0.3 },            // "this"

  // Consonants - Alveolar
  'T': { mouthOpen: 0.2 },                             // "top"
  'D': { mouthOpen: 0.2 },                             // "dog"
  'N': { mouthOpen: 0.2 },                             // "no"
  'L': { mouthOpen: 0.3 },                             // "let"
  'S': { mouthFunnel: 0.3, mouthPucker: 0.2 },         // "sit"
  'Z': { mouthFunnel: 0.3, mouthPucker: 0.2 },         // "zoo"

  // Consonants - Postalveolar
  'SH': { mouthPucker: 0.5, mouthFunnel: 0.4 },        // "she"
  'ZH': { mouthPucker: 0.5, mouthFunnel: 0.4 },        // "measure"
  'CH': { mouthPucker: 0.6 },                          // "church"
  'JH': { mouthPucker: 0.6 },                          // "judge"

  // Consonants - Velar
  'K': { mouthOpen: 0.2 },                             // "cat"
  'G': { mouthOpen: 0.2 },                             // "go"
  'NG': { mouthOpen: 0.2 },                            // "sing"

  // Consonants - Other
  'HH': { mouthOpen: 0.3 },                            // "hat"
  'R': { mouthPucker: 0.3 },                           // "red"
  'W': { mouthPucker: 0.5, mouthFunnel: 0.3 },         // "wet"
  'Y': { mouthSmileLeft: 0.4, mouthSmileRight: 0.4 }, // "yes"
};

/**
 * Get ARKit blend shape weights for a phoneme
 */
function getVisemeWeights(phoneme) {
  if (!phoneme) return {};
  return PHONEME_TO_ARKIT_VISEME[phoneme.toUpperCase()] || {};
}

// ============================================================================
// AVATAR COMPONENT - Professional Interview Avatar
// ============================================================================

function Avatar({ avatarUrl }) {
  const { scene, nodes } = useGLTF(avatarUrl);
  const audioTime = useInterviewStore(state => state.audioTime);
  const phonemes = useInterviewStore(state => state.phonemes);

  // Find face mesh with morph targets (ARKit blend shapes)
  const faceMesh = useRef(null);

  useEffect(() => {
    // Find mesh with morphTargetDictionary
    Object.values(nodes).forEach(node => {
      if (node.morphTargetDictionary) {
        console.log('✅ Found face mesh:', node.name);
        console.log('📊 Morph targets:', Object.keys(node.morphTargetDictionary).length);
        faceMesh.current = node;
      }
    });
  }, [nodes]);

  // Update lip-sync on every frame
  useFrame(() => {
    if (!faceMesh.current) return;

    // Find current phoneme based on audio time
    const currentPhoneme = phonemes.find(
      p => audioTime >= p.start && audioTime < p.end
    );

    // Reset all morph targets to 0
    const influences = faceMesh.current.morphTargetInfluences;
    if (influences) {
      for (let i = 0; i < influences.length; i++) {
        influences[i] = 0;
      }
    }

    // Apply current viseme weights
    if (currentPhoneme) {
      const weights = getVisemeWeights(currentPhoneme.phoneme);

      Object.entries(weights).forEach(([morphName, weight]) => {
        const index = faceMesh.current.morphTargetDictionary[morphName];
        if (index !== undefined && influences) {
          // Smooth blending with professional timing
          const current = influences[index];
          influences[index] = current + (weight - current) * 0.25; // Slower blending for natural look
        }
      });
    }
  });

  return (
    <group>
      {/* Professional avatar positioning and scaling */}
      <primitive
        object={scene}
        scale={[1.0, 1.0, 1.0]} // Natural scale for headshot
        position={[0, 0, 0]} // Centered position
        rotation={[0, 0, 0]} // No rotation for direct front view
      />
    </group>
  );
}

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
// CONTROLS - Professional Interview Interface
// ============================================================================

function Controls() {
  const [questionText, setQuestionText] = useState(
    "Welcome to your AI interview. Please tell me about your background and experience."
  );
  const isAvatarSpeaking = useInterviewStore(state => state.isAvatarSpeaking);
  const speakQuestion = useInterviewStore(state => state.speakQuestion);
  const stopSpeaking = useInterviewStore(state => state.stopSpeaking);

  const handleSpeak = async () => {
    try {
      await speakQuestion(questionText);
    } catch (error) {
      alert('Voice service unavailable. Please ensure the voice service is running on port 8002.');
    }
  };

  return (
    <div style={{
      position: 'absolute',
      bottom: 30,
      left: '50%',
      transform: 'translateX(-50%)',
      background: 'rgba(255,255,255,0.95)',
      padding: '24px 32px',
      borderRadius: '16px',
      color: '#1a1a1a',
      zIndex: 1000,
      boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
      border: '1px solid #e1e5e9',
      backdropFilter: 'blur(10px)',
      maxWidth: '600px',
      width: '90%'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '18px'
        }}>
          🎤
        </div>
        <div>
          <h3 style={{
            margin: '0 0 4px 0',
            fontSize: '18px',
            fontWeight: '600',
            color: '#1a1a1a'
          }}>
            AI Interviewer
          </h3>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: '#6b7280'
          }}>
            Professional avatar interview assistant
          </p>
        </div>
      </div>

      <textarea
        value={questionText}
        onChange={(e) => setQuestionText(e.target.value)}
        disabled={isAvatarSpeaking}
        placeholder="Enter your interview question..."
        style={{
          width: '100%',
          minHeight: '80px',
          padding: '16px',
          marginBottom: '16px',
          borderRadius: '12px',
          background: '#ffffff',
          color: '#1a1a1a',
          border: '2px solid #e1e5e9',
          fontSize: '15px',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          resize: 'vertical',
          outline: 'none',
          transition: 'border-color 0.2s ease',
          ':focus': {
            borderColor: '#667eea'
          }
        }}
        onFocus={(e) => e.target.style.borderColor = '#667eea'}
        onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
      />

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
        <button
          onClick={handleSpeak}
          disabled={isAvatarSpeaking}
          style={{
            padding: '14px 28px',
            background: isAvatarSpeaking
              ? '#f3f4f6'
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: isAvatarSpeaking ? '#9ca3af' : 'white',
            border: 'none',
            borderRadius: '12px',
            cursor: isAvatarSpeaking ? 'not-allowed' : 'pointer',
            fontSize: '15px',
            fontWeight: '600',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            transition: 'all 0.2s ease',
            boxShadow: isAvatarSpeaking ? 'none' : '0 4px 12px rgba(102, 126, 234, 0.3)',
            transform: 'translateY(0px)'
          }}
          onMouseEnter={(e) => {
            if (!isAvatarSpeaking) {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.4)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isAvatarSpeaking) {
              e.target.style.transform = 'translateY(0px)';
              e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
            }
          }}
        >
          {isAvatarSpeaking ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid #9ca3af',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
              Speaking...
            </span>
          ) : (
            '🎤 Start Interview'
          )}
        </button>

        <button
          onClick={stopSpeaking}
          disabled={!isAvatarSpeaking}
          style={{
            padding: '14px 24px',
            background: '#f9fafb',
            color: isAvatarSpeaking ? '#374151' : '#9ca3af',
            border: '2px solid #e5e7eb',
            borderRadius: '12px',
            cursor: isAvatarSpeaking ? 'pointer' : 'not-allowed',
            fontSize: '15px',
            fontWeight: '600',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            if (isAvatarSpeaking) {
              e.target.style.background = '#f3f4f6';
              e.target.style.borderColor = '#d1d5db';
            }
          }}
          onMouseLeave={(e) => {
            if (isAvatarSpeaking) {
              e.target.style.background = '#f9fafb';
              e.target.style.borderColor = '#e5e7eb';
            }
          }}
        >
          ⏹️ Stop
        </button>
      </div>

      {/* Add CSS animation for spinner */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// ============================================================================
// MAIN APP
// ============================================================================

export default function App() {
  // Dev controls (Leva) - disabled for production interviewer mode
  const { avatarUrl, environmentPreset, intensity } = useControls({
    avatarUrl: {
      value: 'https://models.readyplayer.me/64f1a5f0b0e9c3a1b0e9c3a1.glb', // Professional female avatar
      label: 'Avatar URL'
    },
    environmentPreset: {
      value: 'studio', // Changed to studio for professional lighting
      options: ['sunset', 'dawn', 'night', 'warehouse', 'forest', 'apartment', 'studio', 'city', 'park', 'lobby'],
      label: 'Environment'
    },
    intensity: { value: 1.2, min: 0, max: 2, step: 0.1, label: 'Light Intensity' }
  });

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#f8f9fa' }}>
      <Controls />
      <AudioPlayer />

      <Canvas
        shadows
        camera={{
          position: [0, 1.6, 1.8], // Fixed interviewer position - closer and higher
          fov: 28, // Narrower FOV for headshot effect
          near: 0.1,
          far: 100
        }}
        style={{ background: '#f8f9fa' }} // Light background for professional look
      >
        <Suspense fallback={null}>
          {/* Professional studio lighting */}
          <Environment preset={environmentPreset} />

          {/* Additional professional lighting setup */}
          <directionalLight
            position={[2, 2, 2]}
            intensity={1.5}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <directionalLight
            position={[-2, 1, 1]}
            intensity={0.8}
            color="#ffeaa7" // Warm fill light
          />

          {/* Avatar positioned for headshot - no Stage wrapper for direct control */}
          <group position={[0, 0, 0]} scale={[1.1, 1.1, 1.1]}>
            <Avatar avatarUrl={avatarUrl} />
          </group>

          {/* Fixed camera - no OrbitControls for interviewer mode */}
          {/* Contact shadows for professional depth */}
          <ContactShadows
            position={[0, -0.5, 0]}
            opacity={0.3}
            scale={8}
            blur={1.5}
            far={3}
          />
        </Suspense>
      </Canvas>

      {/* Professional status indicator */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        background: 'rgba(255,255,255,0.95)',
        padding: '12px 16px',
        borderRadius: '12px',
        color: '#333',
        fontSize: '13px',
        fontWeight: '500',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        border: '1px solid #e1e5e9'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: useInterviewStore(state => state.isAvatarSpeaking) ? '#10b981' : '#6b7280'
          }}></div>
          {useInterviewStore(state => state.isAvatarSpeaking) ? 'Speaking' : 'Ready'}
        </div>
        <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>
          Phonemes: {useInterviewStore(state => state.phonemes.length)}
        </div>
      </div>
    </div>
  );
}
