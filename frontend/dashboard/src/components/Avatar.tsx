/**
 * Avatar Component - 3D Avatar with ARKit Lip-Sync
 * Uses Three.js with GLTFLoader, KTX2Loader, and MeshoptDecoder for compressed models
 */

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js';
import { LipSyncController } from './LipSyncController';

interface AvatarProps {
  avatarUrl?: string;
}

export function Avatar({ avatarUrl }: AvatarProps) {
  console.log('🎭 Avatar component initialized with URL:', avatarUrl);

  const groupRef = useRef<THREE.Group>(null);
  const [faceMesh, setFaceMesh] = useState<THREE.Mesh | null>(null);
  const [scene, setScene] = useState<THREE.Group | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const createFallbackAvatar = () => {
    console.log('🔄 Creating fallback avatar...');
    const group = new THREE.Group();

    // Simple head with basic morph targets
    const headGeometry = new THREE.SphereGeometry(0.25, 16, 12);
    const headMaterial = new THREE.MeshStandardMaterial({
      color: 0xF5DEB3, // Skin tone
      roughness: 0.7,
      metalness: 0.0
    });

    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.name = 'FallbackAvatar';
    head.position.y = 0.8;
    group.add(head);

    setScene(group);
    setFaceMesh(head);
    console.log('✅ Fallback avatar created');
  };

  useEffect(() => {
    if (!avatarUrl) {
      console.log('🚫 No avatar URL provided - using fallback');
      createFallbackAvatar();
      setLoading(false);
      return;
    }

    console.log('🎭 Loading avatar from URL:', avatarUrl);
    setLoading(true);
    setError(null);

    // Create GLTFLoader with KTX2 and Meshopt support
    const loader = new GLTFLoader();

    // Setup KTX2 loader for compressed textures
    const ktx2Loader = new KTX2Loader();
    ktx2Loader.setTranscoderPath('https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/libs/basis/');
    ktx2Loader.detectSupport(new THREE.WebGLRenderer());
    loader.setKTX2Loader(ktx2Loader);

    // Setup Meshopt decoder for geometry compression
    loader.setMeshoptDecoder(MeshoptDecoder);

    // Load the GLTF model
    loader.load(
      avatarUrl,
      (gltf) => {
        console.log('🎭 Avatar loaded successfully');
        console.log('📦 Scene children:', gltf.scene.children.length);

        // Find face mesh with ARKit blend shapes
        let foundFaceMesh: THREE.Mesh | null = null;

        gltf.scene.traverse((node) => {
          if (foundFaceMesh) return;

          if (node instanceof THREE.Mesh && node.morphTargetDictionary) {
            const arkitMouthShapes = [
              'jawOpen', 'mouthFunnel', 'mouthPucker', 'mouthLeft', 'mouthRight',
              'mouthSmile_L', 'mouthSmile_R', 'mouthFrown_L', 'mouthFrown_R', 'mouthClose'
            ];

            const availableARKit = arkitMouthShapes.filter(
              shape => node.morphTargetDictionary![shape] !== undefined
            );

            if (availableARKit.length >= 6) {
              console.log('🎭 Found ARKit face mesh:', node.name);
              console.log('✅ Available ARKit shapes:', availableARKit);
              console.log('🎯 Using ARKIT MODE for lip sync');
              foundFaceMesh = node as THREE.Mesh;
            }
          }
        });

        if (foundFaceMesh) {
          setScene(gltf.scene);
          setFaceMesh(foundFaceMesh);
        } else {
          console.warn('❌ No suitable face mesh found, using fallback');
          createFallbackAvatar();
        }

        setLoading(false);
      },
      (progress) => {
        console.log('📊 Loading progress:', (progress.loaded / progress.total * 100) + '%');
      },
      (error) => {
        console.error('❌ Failed to load avatar:', error);
        setError(error instanceof Error ? error.message : 'Failed to load avatar');
        createFallbackAvatar();
        setLoading(false);
      }
    );
  }, [avatarUrl]);

  useEffect(() => {
    if (scene && groupRef.current) {
      // Clear previous content
      while (groupRef.current.children.length > 0) {
        groupRef.current.remove(groupRef.current.children[0]);
      }

      // Add the new scene
      groupRef.current.add(scene);
    }
  }, [scene]);

  if (loading) {
    return (
      <group ref={groupRef}>
        <mesh>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="blue" />
        </mesh>
        <mesh position={[0, 1.5, 0]}>
          <sphereGeometry args={[0.3]} />
          <meshStandardMaterial color="yellow" />
        </mesh>
      </group>
    );
  }

  if (error) {
    return (
      <group ref={groupRef}>
        <mesh>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="red" />
        </mesh>
        <mesh position={[0, 1.5, 0]}>
          <sphereGeometry args={[0.5]} />
          <meshStandardMaterial color="orange" />
        </mesh>
      </group>
    );
  }

  return (
    <group ref={groupRef}>
      {faceMesh && (
        <LipSyncController faceMesh={faceMesh} />
      )}
    </group>
  );
}