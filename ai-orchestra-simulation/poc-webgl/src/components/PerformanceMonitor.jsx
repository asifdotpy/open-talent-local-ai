import { useFrame, useThree } from '@react-three/fiber'
import { useRef, useState } from 'react'

export function PerformanceMonitor({ onPerformanceUpdate }) {
  const { gl, scene, camera } = useThree()
  const [fps, setFps] = useState(60)
  const [frameTime, setFrameTime] = useState(16.67)
  const frameCount = useRef(0)
  const lastTime = useRef(performance.now())
  const fpsHistory = useRef([])

  useFrame(() => {
    frameCount.current++
    const currentTime = performance.now()
    const deltaTime = currentTime - lastTime.current

    if (deltaTime >= 1000) { // Update every second
      const currentFps = Math.round((frameCount.current * 1000) / deltaTime)
      const currentFrameTime = deltaTime / frameCount.current

      setFps(currentFps)
      setFrameTime(currentFrameTime)

      // Keep last 10 FPS readings for averaging
      fpsHistory.current.push(currentFps)
      if (fpsHistory.current.length > 10) {
        fpsHistory.current.shift()
      }

      const avgFps = fpsHistory.current.reduce((a, b) => a + b, 0) / fpsHistory.current.length

      onPerformanceUpdate?.({
        fps: currentFps,
        avgFps: Math.round(avgFps),
        frameTime: currentFrameTime,
        triangles: gl.info.render.triangles,
        drawCalls: gl.info.render.calls,
        geometries: scene.children.length
      })

      frameCount.current = 0
      lastTime.current = currentTime
    }
  })

  return null
}

export function PerformanceStats({ performance }) {
  if (!performance) return null

  const getFpsColor = (fps) => {
    if (fps >= 55) return 'text-green-400'
    if (fps >= 30) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className="absolute top-4 right-4 bg-black/80 text-white p-3 rounded-lg font-mono text-sm">
      <div className={`text-lg font-bold ${getFpsColor(performance.fps)}`}>
        {performance.fps} FPS
      </div>
      <div className="text-gray-300">
        Avg: {performance.avgFps} FPS
      </div>
      <div className="text-gray-400 text-xs mt-1">
        Frame: {performance.frameTime.toFixed(1)}ms
      </div>
      <div className="text-gray-400 text-xs">
        Tris: {performance.triangles?.toLocaleString()}
      </div>
      <div className="text-gray-400 text-xs">
        Calls: {performance.drawCalls}
      </div>
    </div>
  )
}