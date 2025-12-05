/**
 * Ready Player Me API Service
 * Handles avatar creation and management via RPM API
 */

const RPM_API_BASE = 'https://api.readyplayer.me';
const RPM_MODELS_BASE = 'https://models.readyplayer.me';
const FALLBACK_THUMBNAIL_BASE =
  'https://render.readyplayer.me/render?scene=fullbody-portrait-v1&frame=0&blendShapes[Blink]=0&blendShapes[MouthOpen]=0&textureSize=512&background=ffffff&model=';
const FALLBACK_AVATAR_METADATA = [
  {
    id: 'fallback-marcus',
    name: 'Marcus',
    gender: 'male',
    style: 'professional',
    avatarId: '64bfa619f72e7b8e17f6b8c7'
  },
  {
    id: 'fallback-sarah',
    name: 'Sarah',
    gender: 'female',
    style: 'professional',
    avatarId: '64f1a5f0b0e9c3a1b0e9c3a1'
  },
  {
    id: 'fallback-alex',
    name: 'Alex',
    gender: 'male',
    style: 'casual',
    avatarId: '65a8dba831b23abb4f401bae'
  },
  {
    id: 'fallback-emma',
    name: 'Emma',
    gender: 'female',
    style: 'casual',
    avatarId: '65c5b45cb11d9c2d4a2c5ca7'
  }
];

class RPMService {
  constructor() {
    // No API key needed for direct URL access
    // Keeping for potential future API usage
    const isBrowser = typeof window !== 'undefined';

    if (isBrowser) {
      // Browser environment - use import.meta.env
      this.apiKey = import.meta.env.VITE_READY_PLAYER_ME_API_KEY || null;
      this.subdomain = import.meta.env.VITE_READY_PLAYER_ME_SUBDOMAIN || null;
    } else {
      // Node.js environment - use process.env
      this.apiKey = process.env.VITE_READY_PLAYER_ME_API_KEY || null;
      this.subdomain = process.env.VITE_READY_PLAYER_ME_SUBDOMAIN || null;
    }

    // Note: API key not required for current direct URL implementation
    if (!this.apiKey) {
      console.log('ℹ️ RPM API key not set - using direct URLs only');
    }
  }

  /**
   * Create an anonymous user
   * @returns {Promise<{userId: string, token: string}>}
   */
  async createAnonymousUser() {
    try {
      const response = await fetch(`${RPM_API_BASE}/v1/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.apiKey
        },
        body: JSON.stringify({
          data: {
            appName: this.getApplicationId()
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create user: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Created anonymous RPM user:', data.data.id);

      return {
        userId: data.data.id,
        token: data.data.token
      };
    } catch (error) {
      console.error('❌ Failed to create anonymous user:', error);
      throw error;
    }
  }

  /**
   * Get all available avatar templates
   * @param {string} token - User authentication token
   * @returns {Promise<Array>} - Array of template objects
   */
  async getTemplates(token) {
    try {
      const response = await fetch(`${RPM_API_BASE}/v2/avatars/templates`, {
        headers: {
          'x-api-key': this.apiKey
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get templates: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Retrieved RPM templates:', data.data.length);

      return data.data;
    } catch (error) {
      console.error('❌ Failed to get templates:', error);
      throw error;
    }
  }

  /**
   * Create a draft avatar from a template
   * @param {string} token - User authentication token
   * @param {string} templateId - Template ID to use
   * @param {string} bodyType - 'fullbody' or 'halfbody'
   * @returns {Promise<Object>} - Created avatar data
   */
  async createAvatarFromTemplate(token, templateId, bodyType = 'fullbody', userId) {
    try {
      const response = await fetch(`${RPM_API_BASE}/v2/avatars/templates/${templateId}`, {
        method: 'POST',
        headers: {
          'x-api-key': this.apiKey,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          data: {
            partner: this.getPartnerName(),
            bodyType: bodyType,
            userId: userId
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create avatar: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Created RPM avatar from template:', data.data.id);

      return data.data;
    } catch (error) {
      console.error('❌ Failed to create avatar from template:', error);
      throw error;
    }
  }

  /**
   * Save a draft avatar permanently
   * @param {string} token - User authentication token
   * @param {string} avatarId - Avatar ID to save
   * @returns {Promise<Object>} - Saved avatar data
   */
  async saveAvatar(token, avatarId) {
    try {
      const response = await fetch(`${RPM_API_BASE}/v2/avatars/${avatarId}`, {
        method: 'PUT',
        headers: {
          'x-api-key': this.apiKey
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to save avatar: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Saved RPM avatar:', avatarId);

      return data.data;
    } catch (error) {
      console.error('❌ Failed to save avatar:', error);
      throw error;
    }
  }

  /**
   * Get the GLB URL for an avatar
   * @param {string} avatarId - Avatar ID
   * @param {boolean} isPreview - Whether to get preview (draft) or final version
   * @returns {string} - GLB URL
   */
  getAvatarUrl(avatarId, isPreview = false) {
    if (isPreview) {
      return `${RPM_API_BASE}/v2/avatars/${avatarId}.glb?preview=true`;
    } else {
      return `${RPM_MODELS_BASE}/${avatarId}.glb`;
    }
  }

  /**
   * Extract application ID from subdomain
   * @returns {string} - Application ID
   */
  getApplicationId() {
    // Extract from subdomain: talent-ai.readyplayer.me -> talent-ai
    return this.subdomain.split('.')[0];
  }

  /**
   * Get partner name from subdomain
   * @returns {string} - Partner name
   */
  getPartnerName() {
    return this.getApplicationId();
  }

  /**
   * Initialize avatars for the application
   * Returns avatar configurations - local model with ARKit blend shapes has FULL lip-sync support
   * @returns {Promise<Array>} - Array of avatar configurations
   */
  async initializeAvatars() {
    console.log('🚀 Initializing avatars for lip-sync demo...');

    const avatars = [
      // Local face.glb with 52 ARKit blend shapes - BEST FOR LIP-SYNC
      {
        id: 'local-face-arkit',
        name: 'ARKit Face (52 Blend Shapes)',
        gender: 'neutral',
        style: 'professional',
        userId: 'local-model',
        avatarId: 'face-arkit',
        url: '/models/face.glb', // Local model in Vite public directory
        thumbnail: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%234A90E2" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" dy=".3em" fill="white" font-size="14"%3EARKit%3C/text%3E%3C/svg%3E',
        morphTargetType: 'ARKit', // 52 blend shapes including full mouth animation
        hasFullLipSync: true,
        isLocal: true
      },
      // RPM avatar - fallback for visual variety (but no visemes)
      {
        id: 'talent-ai-avatar',
        name: 'RPM Avatar (Fallback)',
        gender: 'neutral',
        style: 'professional',
        userId: 'demo-user',
        avatarId: '6916fff248062250a407130a',
        url: 'https://models.readyplayer.me/6916fff248062250a407130a.glb',
        thumbnail: 'https://render.readyplayer.me/render?scene=fullbody-portrait-v1&frame=0&blendShapes[Blink]=0&blendShapes[MouthOpen]=0&textureSize=512&background=ffffff&model=6916fff248062250a407130a',
        morphTargetType: 'Basic', // Only mouthOpen and mouthSmile
        hasFullLipSync: false,
        isLocal: false
      }
    ];

    console.log('✅ Initialized avatars:');
    avatars.forEach(avatar => {
      console.log(`   - ${avatar.name} (${avatar.morphTargetType}${avatar.hasFullLipSync ? ' ✅ Full Lip-Sync' : ''})`);
    });
    
    return avatars;
  }

  /**
   * Get fallback avatars when RPM API is not available
   * Uses avatars with known morph targets for lip-sync testing
   * NO API calls - direct URLs only
   * @returns {Array} - Array of fallback avatar configurations
   */
  getFallbackAvatars() {
    console.log('🔄 Using fallback avatars for testing (no API)...');

    return FALLBACK_AVATAR_METADATA.map((avatar) => ({
      ...avatar,
      userId: avatar.userId ?? 'demo-user',
      url: `https://models.readyplayer.me/${avatar.avatarId}.glb`,
      thumbnail: `https://render.readyplayer.me/render?scene=fullbody-portrait-v1&frame=0&blendShapes[Blink]=0&blendShapes[MouthOpen]=0&textureSize=512&background=ffffff&model=${avatar.avatarId}`
    }));
  }
}

export const rpmService = new RPMService();