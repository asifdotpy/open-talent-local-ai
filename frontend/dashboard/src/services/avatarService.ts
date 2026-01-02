// Avatar service for managing avatar data and API calls
export interface Avatar {
  id: string;
  name: string;
  url: string;
  morphTargetType: 'ARKit' | 'Oculus' | 'RPM';
  hasFullLipSync: boolean;
  isLocal: boolean;
  thumbnail?: string;
}

export const avatarService = {
  // Initialize available avatars
  initializeAvatars: async (): Promise<Avatar[]> => {
    // Return dual avatars: ARKit face (primary) and RPM fallback
    return [
      {
        id: 'local-face-arkit',
        name: 'AI Interviewer (ARKit)',
        url: '/models/face.glb',
        morphTargetType: 'ARKit',
        hasFullLipSync: true,
        isLocal: true,
        thumbnail: '/models/face-thumbnail.jpg'
      },
      {
        id: 'rpm-fallback',
        name: 'AI Interviewer (RPM)',
        url: 'https://api.readyplayer.me/v1/avatars/6791b48e6b4c4a5e8f2b3c1d.glb',
        morphTargetType: 'RPM',
        hasFullLipSync: false,
        isLocal: false,
        thumbnail: 'https://api.readyplayer.me/v1/avatars/6791b48e6b4c4a5e8f2b3c1d/thumbnail.jpg'
      }
    ];
  },

  // Generate lip-sync data from text
  generateLipSync: async (text: string, avatarId: string = 'local-face-arkit'): Promise<{
    audioUrl: string;
    phonemes: Array<{ phoneme: string; timestamp: number; intensity: number }>;
  }> => {
    try {
      // Call voice service for TTS
      const response = await fetch('http://localhost:8002/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          voice: 'alloy',
          avatar_id: avatarId
        }),
      });

      if (!response.ok) {
        throw new Error(`Voice service error: ${response.status}`);
      }

      const data = await response.json();
      return {
        audioUrl: data.audio_url,
        phonemes: data.phonemes || []
      };
    } catch (error) {
      console.error('Failed to generate lip-sync:', error);
      throw error;
    }
  },

  // Get avatar model URL
  getAvatarUrl: (avatarId: string): string => {
    const avatars = [
      {
        id: 'local-face-arkit',
        url: '/models/face.glb'
      },
      {
        id: 'rpm-fallback',
        url: 'https://api.readyplayer.me/v1/avatars/6791b48e6b4c4a5e8f2b3c1d.glb'
      }
    ];

    const avatar = avatars.find(a => a.id === avatarId);
    return avatar?.url || '/models/face.glb';
  }
};
