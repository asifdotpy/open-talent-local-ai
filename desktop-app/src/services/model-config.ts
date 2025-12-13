/**
 * Model Configuration
 * Supports multiple custom models trained on interview datasets
 */

export interface ModelConfig {
  id: string;
  name: string;
  huggingface: string;
  paramCount: string;
  ramRequired: string;
  downloadSize: string;
  description: string;
  status: 'trained' | 'planned';
  dataset?: string;
}

export const AVAILABLE_MODELS: ModelConfig[] = [
  {
    id: 'granite4:350m-h',
    name: 'Granite 350M (Lightweight)',
    huggingface: 'granite4:350m-h',
    paramCount: '350M',
    ramRequired: '2-4GB',
    downloadSize: '366MB',
    description: 'Smallest Granite variant (fast, fits low RAM systems)',
    status: 'trained',
  },
  {
    id: 'granite4:3b',
    name: 'Granite 3B (Clean)',
    huggingface: 'granite4:3b',
    paramCount: '3B',
    ramRequired: '8-12GB',
    downloadSize: '2.1GB',
    description: 'Official Granite 4 base model (clean, no hallucinated context)',
    status: 'trained',
  },
  {
    id: 'llama3.2-1b',
    name: 'Llama 3.2 1B (Fallback)',
    huggingface: 'meta-llama/Llama-3.2-1B',
    paramCount: '1B',
    ramRequired: '4-6GB',
    downloadSize: '600MB',
    description: 'Generic model - for comparison/fallback',
    status: 'trained',
  },
];

export const DEFAULT_MODEL = 'granite4:350m-h';

export function getModelConfig(modelId: string): ModelConfig | undefined {
  return AVAILABLE_MODELS.find((m) => m.id === modelId);
}

export function getTrainedModels(): ModelConfig[] {
  return AVAILABLE_MODELS.filter((m) => m.status === 'trained');
}

export function getPlannedModels(): ModelConfig[] {
  return AVAILABLE_MODELS.filter((m) => m.status === 'planned');
}
