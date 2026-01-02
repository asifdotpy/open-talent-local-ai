'use client'

import FaceRenderer from '../components/FaceRenderer'

export default function Home() {
  return (
    <main style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#111'
    }}>
      <div style={{
        padding: '20px',
        background: '#222',
        color: 'white',
        borderBottom: '1px solid #333'
      }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>🎭 Face R3F Proof-of-Concept</h1>
        <p style={{ margin: '10px 0 0 0', color: '#ccc' }}>
          Phase 2: Testing face.glb model with phoneme-based lip-sync
        </p>
      </div>

      <div style={{ flex: 1, position: 'relative' }}>
        <FaceRenderer />
      </div>

      <div style={{
        padding: '15px',
        background: '#222',
        color: 'white',
        borderTop: '1px solid #333',
        fontSize: '14px'
      }}>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div>
            <strong>Controls:</strong> Click phoneme buttons to test lip-sync
          </div>
          <div>
            <strong>Status:</strong> <span id="status">Initializing...</span>
          </div>
        </div>
      </div>
    </main>
  )
}
