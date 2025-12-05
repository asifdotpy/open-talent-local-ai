import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Face R3F PoC - Phase 2',
  description: 'React Three Fiber proof-of-concept for face.glb lip-sync',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, background: '#111' }}>
        {children}
      </body>
    </html>
  )
}