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
    id: 'vetta-granite-2b-gguf-v4',
    name: 'Granite 2B (Trained)',
    huggingface: 'asifdotpy/vetta-granite-2b-gguf-v4',
    paramCount: '2B',
    ramRequired: '8-12GB',
    downloadSize: '1.2GB',
    description: 'Custom trained on interview datasets (v4 GGUF format)',
    status: 'trained',
    dataset: 'asifdotpy/vetta-interview-dataset-enhanced',
  },
  {
    id: 'vetta-granite-2b-lora-v4',
    name: 'Granite 2B LoRA (Efficient)',
    huggingface: 'asifdotpy/vetta-granite-2b-lora-v4',
    paramCount: '2B + LoRA',
    ramRequired: '6-10GB',
    downloadSize: '500MB',
    description: 'LoRA-fine-tuned variant (lower memory)',
    status: 'trained',
    dataset: 'asifdotpy/vetta-interview-dataset-enhanced',
  },
  {
    id: 'vetta-granite-350m',
    name: 'Granite 350M (Planned)',
    huggingface: 'asifdotpy/vetta-granite-350m-gguf',
    paramCount: '350M',
    ramRequired: '2-4GB',
    downloadSize: '400MB',
    description: 'Low-resource model - training in progress',
    status: 'planned',
    dataset: 'asifdotpy/vetta-interview-dataset-enhanced',
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

export const DEFAULT_MODEL = 'vetta-granite-2b-gguf-v4';

export function getModelConfig(modelId: string): ModelConfig | undefined {
  return AVAILABLE_MODELS.find((m) => m.id === modelId);
}

export function getTrainedModels(): ModelConfig[] {
  return AVAILABLE_MODELS.filter((m) => m.status === 'trained');
}

export function getPlannedModels(): ModelConfig[] {
  return AVAILABLE_MODELS.filter((m) => m.status === 'planned');
}
