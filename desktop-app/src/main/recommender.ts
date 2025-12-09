/**
 * Model Recommendation Engine
 * Recommends Granite model size based on available RAM
 */

export interface ModelRecommendation {
  recommended: 'granite-350m' | 'granite-2b' | 'granite-8b';
  reason: string;
  alternates: Array<{
    model: 'granite-350m' | 'granite-2b' | 'granite-8b';
    reason: string;
  }>;
}

/**
 * Recommend model based on available RAM
 * - < 6GB: Granite-350M (minimal footprint)
 * - 6-14GB: Granite-2B (balanced)
 * - 14GB+: Granite-8B (best quality)
 */
export function recommendModel(ramGb: number): ModelRecommendation {
  if (ramGb < 6) {
    return {
      recommended: 'granite-350m',
      reason: `Your system has ${ramGb}GB RAM. Granite-350M is optimized for low-resource systems.`,
      alternates: [
        {
          model: 'granite-2b',
          reason: 'Better quality, but requires 8GB+ RAM (not recommended for your system)'
        }
      ]
    };
  }

  if (ramGb < 14) {
    return {
      recommended: 'granite-2b',
      reason: `Your system has ${ramGb}GB RAM. Granite-2B offers excellent quality with good performance.`,
      alternates: [
        {
          model: 'granite-350m',
          reason: 'Lower resource usage, but reduced conversation quality'
        },
        {
          model: 'granite-8b',
          reason: 'Best quality, but requires 16GB+ RAM (not recommended for your system)'
        }
      ]
    };
  }

  return {
    recommended: 'granite-8b',
    reason: `Your system has ${ramGb}GB RAM. Granite-8B provides the best conversation quality.`,
    alternates: [
      {
        model: 'granite-2b',
        reason: 'Lighter resource usage, good quality'
      },
      {
        model: 'granite-350m',
        reason: 'Minimal resource usage, but reduced conversation quality'
      }
    ]
  };
}

/**
 * Get model details (size, quality, speed)
 */
export function getModelDetails(model: 'granite-350m' | 'granite-2b' | 'granite-8b') {
  const details = {
    'granite-350m': {
      name: 'Granite 350M',
      parameters: '350M',
      ramRequired: '2-4GB',
      downloadSize: '400MB',
      quality: '⭐⭐⭐',
      speed: '⚡ Very Fast',
      description: 'Best for low-end laptops and older hardware'
    },
    'granite-2b': {
      name: 'Granite 2B',
      parameters: '2B',
      ramRequired: '8-12GB',
      downloadSize: '1.2GB',
      quality: '⭐⭐⭐⭐',
      speed: '⚡ Fast',
      description: 'Balanced quality and performance for most systems'
    },
    'granite-8b': {
      name: 'Granite 8B',
      parameters: '8B',
      ramRequired: '16-32GB',
      downloadSize: '4.5GB',
      quality: '⭐⭐⭐⭐⭐',
      speed: '⚡ Moderate',
      description: 'Best quality for high-end workstations'
    }
  };

  return details[model];
}
