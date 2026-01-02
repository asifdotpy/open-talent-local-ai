'use client'

import { OrbitControls, useGLTF } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'

// Phoneme mapping for lip-sync
const PHONEMES = {
  A: 'A',
  E: 'E',
  I: 'I',
  O: 'O',
  U: 'U',
  REST: null
} as const

type Phoneme = keyof typeof PHONEMES

function FaceModel({ currentPhoneme }: { currentPhoneme: Phoneme }) {
  const meshRef = useRef<THREE.Mesh | null>(null)
  const { scene, nodes, materials } = useGLTF('/models/face.glb')

  // Clone the scene to avoid modifying the original
  const clonedScene = scene.clone()

  useEffect(() => {
    if (!meshRef.current) return

    // Reset all morph targets
    if (meshRef.current.morphTargetInfluences) {
      meshRef.current.morphTargetInfluences.fill(0)
    }

    // Apply current phoneme morph target
    if (currentPhoneme !== 'REST' && meshRef.current.morphTargetDictionary) {
      const targetName = PHONEMES[currentPhoneme]
      const targetIndex = meshRef.current.morphTargetDictionary[targetName]

      if (targetIndex !== undefined) {
        meshRef.current.morphTargetInfluences![targetIndex] = 1.0
        console.log(`Applied phoneme: ${targetName} (index: ${targetIndex})`)
      } else {
        console.warn(`Phoneme morph target not found: ${targetName}`)
      }
    }
  }, [currentPhoneme])

  // Find the face mesh in the cloned scene
  useEffect(() => {
    clonedScene.traverse((child) => {
      if (child instanceof THREE.Mesh && child.morphTargetInfluences) {
        meshRef.current = child
        console.log('Found face mesh with morph targets:', child.morphTargetDictionary)
      }
    })
  }, [clonedScene])

  return (
    <primitive
      ref={meshRef}
      object={clonedScene}
      scale={[1, 1, 1]}
      position={[0, 0, 0]}
    />
  )
}

function PhonemeControls({
  currentPhoneme,
  onPhonemeChange
}: {
  currentPhoneme: Phoneme
  onPhonemeChange: (phoneme: Phoneme) => void
}) {
  return (
    <div style={{
      position: 'absolute',
      top: '20px',
      right: '20px',
      background: 'rgba(0,0,0,0.8)',
      padding: '15px',
      borderRadius: '8px',
      color: 'white',
      fontFamily: 'monospace'
    }}>
      <h3 style={{ margin: '0 0 10px 0', fontSize: '16px' }}>🎭 Phoneme Controls</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
        {(Object.keys(PHONEMES) as Phoneme[]).map((phoneme) => (
          <button
            key={phoneme}
            onClick={() => onPhonemeChange(phoneme)}
            style={{
              padding: '8px 12px',
              background: currentPhoneme === phoneme ? '#007bff' : '#333',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold'
            }}
          >
            {phoneme}
          </button>
        ))}
      </div>
      <div style={{ marginTop: '10px', fontSize: '12px', color: '#ccc' }}>
        Current: <strong>{currentPhoneme}</strong>
      </div>
    </div>
  )
}

export default function FaceRenderer() {
  const [currentPhoneme, setCurrentPhoneme] = useState<Phoneme>('REST')
  const [status, setStatus] = useState('Loading...')

  useEffect(() => {
    // Update status element
    const statusElement = document.getElementById('status')
    if (statusElement) {
      statusElement.textContent = status
    }
  }, [status])

  const handlePhonemeChange = (phoneme: Phoneme) => {
    setCurrentPhoneme(phoneme)
    setStatus(`Phoneme: ${phoneme}`)
  }

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <Canvas
        camera={{ position: [0, 0, 2], fov: 50 }}
        style={{ background: '#1a1a1a' }}
        onCreated={({ gl }) => {
          gl.setClearColor('#1a1a1a')
          setStatus('3D Scene Ready')
        }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />

        {/* Face Model */}
        <FaceModel currentPhoneme={currentPhoneme} />

        {/* Camera Controls */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={1}
          maxDistance={5}
        />
      </Canvas>

      {/* UI Controls */}
      <PhonemeControls
        currentPhoneme={currentPhoneme}
        onPhonemeChange={handlePhonemeChange}
      />

      {/* Instructions */}
      <div style={{
        position: 'absolute',
        bottom: '80px',
        left: '20px',
        background: 'rgba(0,0,0,0.8)',
        padding: '15px',
        borderRadius: '8px',
        color: 'white',
        maxWidth: '300px',
        fontSize: '14px'
      }}>
        <h4 style={{ margin: '0 0 8px 0' }}>📋 Instructions</h4>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          <li>Use mouse to orbit around the face</li>
          <li>Click phoneme buttons to test lip-sync</li>
          <li>Scroll to zoom in/out</li>
          <li>Check console for morph target details</li>
        </ul>
      </div>
    </div>
  )
}

// Preload the GLTF model
useGLTF.preload('/models/face.glb')
