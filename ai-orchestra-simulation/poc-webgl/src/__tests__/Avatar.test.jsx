import { Canvas } from '@react-three/fiber';
import { render, screen } from '@testing-library/react';
import Avatar from '../components/Avatar';

jest.mock('@react-three/drei', () => ({
  useGLTF: jest.fn(() => ({
    scene: {},
    nodes: {
      FaceMesh: {
        morphTargetDictionary: {
          mouthOpen: 0,
          jawOpen: 1,
        },
        morphTargetInfluences: [0, 0],
      },
    },
  })),
}));

describe('Avatar Component', () => {
  it('renders the avatar model without crashing', () => {
    render(
      <Canvas>
        <Avatar avatarUrl="https://example.com/avatar.glb" />
      </Canvas>
    );

    expect(screen.getByTestId('avatar')).toBeInTheDocument();
  });

  it('applies morph target influences based on phonemes', () => {
    // Mock phoneme data
    const phonemes = [
      { phoneme: 'AA', start: 0, end: 1 },
      { phoneme: 'EH', start: 1, end: 2 },
    ];

    // Mock Zustand store
    jest.mock('../stores/interviewStore', () => ({
      useInterviewStore: jest.fn(() => ({
        phonemes,
        audioTime: 0.5,
      })),
    }));

    render(
      <Canvas>
        <Avatar avatarUrl="https://example.com/avatar.glb" />
      </Canvas>
    );

    // Assert morph target influences are updated
    const faceMesh = screen.getByTestId('avatar-face-mesh');
    expect(faceMesh.morphTargetInfluences[0]).toBeGreaterThan(0);
  });
});