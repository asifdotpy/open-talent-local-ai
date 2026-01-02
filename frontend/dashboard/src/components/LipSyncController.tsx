/**
 * LipSyncController Component
 * Manages phoneme-to-ARKit blend shape mapping and morph target animation
 */

import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';
import { useInterviewStore } from '../stores/interviewStore';

interface LipSyncControllerProps {
  faceMesh: THREE.Mesh;
}

/**
 * Maps phonemes to ARKit blend shapes
 */
const PHONEME_TO_ARKIT = {
  // Vowels
  'AA': { jawOpen: 0.8, mouthOpen: 0.6 },     // "father"
  'AE': { jawOpen: 0.7, mouthOpen: 0.5 },     // "cat"
  'AH': { jawOpen: 0.6, mouthOpen: 0.4 },     // "but"
  'AO': { jawOpen: 0.7, mouthFunnel: 0.5 },   // "caught"
  'AW': { jawOpen: 0.6, mouthFunnel: 0.4 },   // "cow"
  'AY': { jawOpen: 0.5, mouthOpen: 0.3 },     // "hide"
  'EH': { jawOpen: 0.6, mouthOpen: 0.4 },     // "red"
  'ER': { jawOpen: 0.5, mouthOpen: 0.3 },     // "her"
  'EY': { jawOpen: 0.7, mouthOpen: 0.5 },     // "ate"
  'IH': { jawOpen: 0.4, mouthOpen: 0.2 },     // "it"
  'IY': { jawOpen: 0.5, mouthOpen: 0.3 },     // "feet"
  'OW': { jawOpen: 0.6, mouthFunnel: 0.4 },   // "go"
  'OY': { jawOpen: 0.5, mouthFunnel: 0.3 },   // "boy"
  'UH': { jawOpen: 0.4, mouthFunnel: 0.2 },   // "book"
  'UW': { jawOpen: 0.5, mouthFunnel: 0.3 },   // "boot"

  // Consonants
  'B': { mouthClose: 0.8 },                   // "bat"
  'P': { mouthClose: 1.0 },                   // "pat"
  'M': { mouthClose: 0.6 },                   // "mat"
  'F': { mouthClose: 0.7 },                   // "fat"
  'V': { mouthClose: 0.6 },                   // "vat"
  'TH': { mouthClose: 0.5 },                  // "thin"
  'DH': { mouthClose: 0.4 },                  // "this"
  'T': { mouthClose: 0.6 },                   // "top"
  'D': { mouthClose: 0.5 },                   // "dog"
  'N': { mouthClose: 0.3 },                   // "no"
  'L': { mouthClose: 0.2 },                   // "let"
  'S': { mouthFunnel: 0.7 },                  // "sit"
  'Z': { mouthFunnel: 0.6 },                  // "zoo"
  'SH': { mouthFunnel: 0.8 },                 // "she"
  'ZH': { mouthFunnel: 0.7 },                 // "measure"
  'CH': { mouthFunnel: 0.9 },                 // "church"
  'JH': { mouthFunnel: 0.8 },                 // "judge"
  'K': { mouthFunnel: 0.6 },                  // "cat"
  'G': { mouthFunnel: 0.5 },                  // "go"
  'NG': { mouthFunnel: 0.4 },                 // "sing"
  'HH': { mouthFunnel: 0.3 },                 // "hat"
  'R': { mouthOpen: 0.4 },                    // "red"
  'W': { mouthFunnel: 0.2 },                  // "wet"
  'Y': { mouthOpen: 0.2 },                    // "yes"

  // Silence
  'sil': { mouthClose: 0.1 }
};

/**
 * Get ARKit blend shape weights for a phoneme
 */
function getArkitWeights(phoneme: string): Record<string, number> {
  if (!phoneme) return {};
  const upperPhoneme = phoneme.toUpperCase() as keyof typeof PHONEME_TO_ARKIT;
  return PHONEME_TO_ARKIT[upperPhoneme] || {};
}

/**
 * Smooth interpolation function
 */
function lerp(start: number, end: number, factor: number): number {
  return start + (end - start) * factor;
}

export function LipSyncController({ faceMesh }: LipSyncControllerProps) {
  const { phonemes } = useInterviewStore();

  // Animation state
  const currentWeights = useRef<Record<string, number>>({});
  const targetWeights = useRef<Record<string, number>>({});
  const lastPhonemeTime = useRef<number>(0);

  useFrame((state, delta) => {
    if (!faceMesh || !faceMesh.morphTargetInfluences || !faceMesh.morphTargetDictionary) {
      return;
    }

    const influences = faceMesh.morphTargetInfluences;
    const morphDict = faceMesh.morphTargetDictionary;
    const currentTime = state.clock.elapsedTime;

    // Find current phoneme
    let currentPhoneme: any = null;
    if (phonemes && phonemes.length > 0) {
      // Simple implementation: find phoneme active at current time
      // In production, you'd want more sophisticated timing
      currentPhoneme = phonemes.find((p: any) =>
        currentTime >= p.timestamp && currentTime < p.timestamp + 0.1
      );
    }

    // Calculate target weights
    if (currentPhoneme) {
      targetWeights.current = getArkitWeights(currentPhoneme.phoneme);
      lastPhonemeTime.current = currentTime;
    } else if (currentTime - lastPhonemeTime.current > 0.5) {
      // Return to neutral after silence
      targetWeights.current = {};
    }

    // Smooth interpolation
    const interpolationSpeed = 8 * delta; // Adjust speed as needed

    Object.entries(targetWeights.current).forEach(([morphName, targetWeight]) => {
      const morphIndex = morphDict[morphName];
      if (morphIndex !== undefined && influences[morphIndex] !== undefined) {
        const currentWeight = currentWeights.current[morphName] || 0;
        const interpolatedWeight = lerp(currentWeight, targetWeight, interpolationSpeed);

        influences[morphIndex] = Math.max(0, Math.min(1, interpolatedWeight));
        currentWeights.current[morphName] = interpolatedWeight;
      }
    });

    // Add subtle breathing motion when silent
    if (Object.keys(targetWeights.current).length === 0) {
      const breathingMotion = Math.sin(currentTime * 2) * 0.02 + 0.01;
      const jawIndex = morphDict['jawOpen'];
      if (jawIndex !== undefined && influences[jawIndex] !== undefined) {
        influences[jawIndex] = Math.max(0, Math.min(0.1, breathingMotion));
      }
    }
  });

  return null;
}
