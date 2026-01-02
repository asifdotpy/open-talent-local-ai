import { act, renderHook } from '@testing-library/react-hooks';
import { useInterviewStore } from '../stores/interviewStore';

describe('LipSyncController', () => {
  it('updates phoneme data correctly', () => {
    const { result } = renderHook(() => useInterviewStore());

    act(() => {
      result.current.setPhonemes([
        { phoneme: 'AA', start: 0, end: 1 },
        { phoneme: 'EH', start: 1, end: 2 },
      ]);
    });

    expect(result.current.phonemes).toHaveLength(2);
    expect(result.current.phonemes[0].phoneme).toBe('AA');
  });

  it('handles audio time updates', () => {
    const { result } = renderHook(() => useInterviewStore());

    act(() => {
      result.current.setAudioTime(1.5);
    });

    expect(result.current.audioTime).toBe(1.5);
  });

  it('resets state when speaking stops', () => {
    const { result } = renderHook(() => useInterviewStore());

    act(() => {
      result.current.setPhonemes([
        { phoneme: 'AA', start: 0, end: 1 },
      ]);
      result.current.setAudioTime(0.5);
      result.current.stopSpeaking();
    });

    expect(result.current.phonemes).toHaveLength(0);
    expect(result.current.audioTime).toBe(0);
  });
});
