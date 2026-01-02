import { act, renderHook } from '@testing-library/react-hooks';
import { useInterviewStore } from '../stores/interviewStore';

global.fetch = jest.fn();

describe('Voice Service Integration', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('calls the voice service API and updates state with phonemes', async () => {
    const mockResponse = {
      phonemes: [
        { phoneme: 'AA', start: 0, end: 1 },
        { phoneme: 'EH', start: 1, end: 2 },
      ],
      audio_data: 'mockAudioData',
      duration: 2,
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useInterviewStore());

    await act(async () => {
      await result.current.speakQuestion('Hello world');
    });

    expect(fetch).toHaveBeenCalledWith('http://localhost:8002/voice/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Hello world',
        voice: 'en-US',
        extract_phonemes: true,
      }),
    });

    expect(result.current.phonemes).toEqual(mockResponse.phonemes);
    expect(result.current.audioData).toBe(mockResponse.audio_data);
    expect(result.current.duration).toBe(mockResponse.duration);
  });

  it('handles API errors gracefully', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => useInterviewStore());

    await act(async () => {
      try {
        await result.current.speakQuestion('Hello world');
      } catch (error) {
        expect(error.message).toBe('Voice service error: 500');
      }
    });

    expect(result.current.phonemes).toEqual([]);
    expect(result.current.audioData).toBeNull();
    expect(result.current.duration).toBe(0);
  });

  it('handles network errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useInterviewStore());

    await act(async () => {
      try {
        await result.current.speakQuestion('Hello world');
      } catch (error) {
        expect(error.message).toBe('Network error');
      }
    });

    expect(result.current.phonemes).toEqual([]);
    expect(result.current.audioData).toBeNull();
    expect(result.current.duration).toBe(0);
  });
});
