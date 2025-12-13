import { OllamaProvider } from '../ollama-provider';

// Mock axios.create to control responses upfront
jest.mock('axios', () => {
  const axiosCreate = jest.fn().mockReturnValue({
    get: jest.fn().mockResolvedValue({
      data: { models: [{ name: 'granite-code:3b' }, { name: 'llama3.2:1b' }] },
    }),
    post: jest.fn(),
  });
  return {
    __esModule: true,
    default: { create: axiosCreate },
  };
});

describe('OllamaProvider.listModels', () => {
  it('returns array of model names from /api/tags', async () => {
    const provider = new OllamaProvider({ baseURL: 'http://localhost:11434', timeout: 1000 });
    const names = await provider.listModels();
    expect(names).toEqual(['granite-code:3b', 'llama3.2:1b']);
  });
});
