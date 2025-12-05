/**
 * Avatar Component - Ready Player Me Avatar with Lip-Sync
 * Uses @readyplayerme/visage SDK for avatar loading and ARKit blend shapes
 */

/**
 * Avatar Component - Ready Player Me Avatar with Lip-Sync
 * Uses useGLTF with RPM authentication for avatar loading and ARKit blend shapes
 */

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js';
import { useInterviewStore } from '../stores/interviewStore';
import { LipSyncController } from './LipSyncController';

export function RPMAvatar({ avatarUrl }) {
  console.log('🎭 RPMAvatar component initialized with URL:', avatarUrl);

  const groupRef = useRef();
  const [faceMesh, setFaceMesh] = useState(null);
  const [scene, setScene] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { isAvatarSpeaking, phonemes } = useInterviewStore();

  const createFallbackAvatar = () => {
    // Create a more humanoid avatar with proper proportions and multiple morph targets
    const group = new THREE.Group();

    // Body (torso) - cylinder
    const bodyGeometry = new THREE.CylinderGeometry(0.4, 0.35, 1.0, 8);
    const bodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x4A90E2, // Blue shirt
      roughness: 0.8,
      metalness: 0.1
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0.2;
    group.add(body);

    // Head - sphere with multiple morph targets for lip sync
    const headGeometry = new THREE.SphereGeometry(0.25, 16, 12);

    // Create morph targets for different mouth shapes (Oculus visemes)
    const morphTargets = {};

    // Get original positions
    const positions = headGeometry.attributes.position.array;
    const vertexCount = positions.length / 3;

    // Create morph target arrays for each viseme
    const visemeNames = ['viseme_sil', 'viseme_PP', 'viseme_FF', 'viseme_TH', 'viseme_DD', 'viseme_kk', 'viseme_CH', 'viseme_SS', 'viseme_nn', 'viseme_RR', 'viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U'];

    visemeNames.forEach(visemeName => {
      const morphPositions = new Float32Array(positions.length);

      for (let i = 0; i < vertexCount; i++) {
        const baseIndex = i * 3;
        const x = positions[baseIndex];
        const y = positions[baseIndex + 1];
        const z = positions[baseIndex + 2];

        // Lower front area (mouth region)
        if (y < -0.1 && y > -0.25 && z > 0.1 && Math.abs(x) < 0.15) {
          let mouthFactor = 1.0;
          let yOffset = 0.0;

          // Different mouth shapes for different visemes
          switch (visemeName) {
            case 'viseme_sil': // Silence - slight neutral
              mouthFactor = 1.05;
              yOffset = -0.01;
              break;
            case 'viseme_PP': // Bilabial plosive - lips closed
            case 'viseme_FF': // Labiodental - lips slightly open
              mouthFactor = 0.95;
              yOffset = 0.02;
              break;
            case 'viseme_TH': // Dental - tongue visible
            case 'viseme_DD': // Alveolar - slight opening
              mouthFactor = 1.1;
              yOffset = -0.03;
              break;
            case 'viseme_kk': // Velar - back of mouth
            case 'viseme_CH': // Post-alveolar
            case 'viseme_SS': // Sibilant - narrow opening
              mouthFactor = 1.15;
              yOffset = -0.04;
              break;
            case 'viseme_nn': // Nasal - slight opening
            case 'viseme_RR': // Retroflex - tongue up
              mouthFactor = 1.08;
              yOffset = -0.02;
              break;
            case 'viseme_aa': // Open back vowel - wide open
              mouthFactor = 1.25;
              yOffset = -0.06;
              break;
            case 'viseme_E': // Mid front vowel
              mouthFactor = 1.18;
              yOffset = -0.04;
              break;
            case 'viseme_I': // Close front vowel - narrow
              mouthFactor = 1.12;
              yOffset = -0.03;
              break;
            case 'viseme_O': // Mid back rounded vowel
              mouthFactor = 1.2;
              yOffset = -0.05;
              break;
            case 'viseme_U': // Close back rounded vowel
              mouthFactor = 1.15;
              yOffset = -0.04;
              break;
          }

          morphPositions[baseIndex] = x * mouthFactor;
          morphPositions[baseIndex + 1] = y + yOffset;
          morphPositions[baseIndex + 2] = z * mouthFactor;
        } else {
          // Copy original positions for non-mouth areas
          morphPositions[baseIndex] = x;
          morphPositions[baseIndex + 1] = y;
          morphPositions[baseIndex + 2] = z;
        }
      }

      morphTargets[visemeName] = morphPositions;
    });

    // Set up morph attributes
    headGeometry.morphAttributes = { position: [] };
    headGeometry.morphTargetsRelative = false;

    // Create morph target dictionary and influences
    const morphTargetDictionary = {};
    const morphTargetInfluences = [];

    visemeNames.forEach((visemeName, index) => {
      morphTargetDictionary[visemeName] = index;
      morphTargetInfluences.push(0);
      headGeometry.morphAttributes.position.push(new THREE.Float32BufferAttribute(morphTargets[visemeName], 3));
    });

    const headMaterial = new THREE.MeshStandardMaterial({
      color: 0xF5DEB3, // Skin tone
      roughness: 0.7,
      metalness: 0.0
    });

    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.name = 'FallbackAvatar';
    head.morphTargetDictionary = morphTargetDictionary;
    head.morphTargetInfluences = morphTargetInfluences;
    head.position.y = 0.8;
    group.add(head);

    // Simple eyes
    const eyeGeometry = new THREE.SphereGeometry(0.03, 8, 6);
    const eyeMaterial = new THREE.MeshStandardMaterial({ color: 0x000000 });

    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.08, 0.85, 0.22);
    group.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.08, 0.85, 0.22);
    group.add(rightEye);

    // Arms
    const armGeometry = new THREE.CylinderGeometry(0.08, 0.08, 0.6, 6);
    const armMaterial = new THREE.MeshStandardMaterial({
      color: 0xF5DEB3, // Skin tone
      roughness: 0.8,
      metalness: 0.1
    });

    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
    leftArm.position.set(-0.5, 0.3, 0);
    leftArm.rotation.z = Math.PI / 6;
    group.add(leftArm);

    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
    rightArm.position.set(0.5, 0.3, 0);
    rightArm.rotation.z = -Math.PI / 6;
    group.add(rightArm);

    // Create a simple scene with the group
    const scene = new THREE.Scene();
    scene.add(group);

    setScene(scene);
    setFaceMesh(head); // Use the head for morph targets
    console.log('✅ Enhanced fallback avatar created with humanoid shape and', visemeNames.length, 'morph targets for lip-sync demo');
    console.log('🎭 Available morph targets:', visemeNames);
  };

  useEffect(() => {
    if (!avatarUrl) {
      console.log('🚫 No avatar URL provided - skipping load');
      setLoading(false);
      return;
    }

    console.log('🎭 Attempting to load avatar from URL:', avatarUrl);
    setLoading(true);
    setError(null);

    // Create custom GLTFLoader with KTX2 texture support
    const loader = new GLTFLoader();
    
    // Setup KTX2 loader for compressed textures
    const ktx2Loader = new KTX2Loader();
    ktx2Loader.setTranscoderPath('https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/libs/basis/');
    ktx2Loader.detectSupport(new THREE.WebGLRenderer());
    loader.setKTX2Loader(ktx2Loader);
    
    // Setup Meshopt decoder for geometry compression
    loader.setMeshoptDecoder(MeshoptDecoder);

    // RPM public models don't require authentication headers
    // Just fetch directly without auth headers to avoid CORS issues
    console.log('🔄 Fetching avatar GLB file...');
    fetch(avatarUrl)
    .then(response => {
      console.log('📡 Avatar fetch response status:', response.status, response.statusText);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.arrayBuffer();
    })
    .then(arrayBuffer => {
      console.log('📦 Avatar GLB loaded, size:', arrayBuffer.byteLength, 'bytes');
      // Parse the GLTF data
      loader.parse(arrayBuffer, '', (gltf) => {
        console.log('🎭 RPM Avatar parsed successfully, scene children:', gltf.scene.children.length);
        setScene(gltf.scene);
        setLoading(false);
      }, (error) => {
        console.error('❌ Failed to parse GLTF:', error);
        setError(error);
        setLoading(false);
      });
    })
    .catch(error => {
      console.error('❌ Failed to load RPM avatar:', error);
      console.log('🔄 Creating enhanced fallback avatar with 15 Oculus visemes for lip-sync demo...');
      createFallbackAvatar();
      setLoading(false);
    });
  }, [avatarUrl]);

  useEffect(() => {
    if (scene && groupRef.current) {
      // Clone the scene to avoid modifying the cached version
      const clonedScene = scene.clone();
      groupRef.current.add(clonedScene);

      // Traverse to find face mesh with morph targets
      let foundValidFaceMesh = false;
      
      clonedScene.traverse((node) => {
        // Skip if we already found a valid face mesh
        if (foundValidFaceMesh) return;
        
        if (node.name === 'FallbackAvatar') {
          // This is our fallback avatar head with morph targets
          console.log('🎭 Found fallback avatar head with morph targets:', node.name);
          console.log('📊 Available morph targets:', Object.keys(node.morphTargetDictionary));
          console.log('✅ Using ENHANCED FALLBACK AVATAR with 15 Oculus visemes for lip sync');
          setFaceMesh(node);
          foundValidFaceMesh = true;
        } else if (node.morphTargetDictionary && Object.keys(node.morphTargetDictionary).length > 0) {
          // Check if this mesh has Oculus visemes OR ARKit blend shapes
          const oculusVisemes = ['viseme_sil', 'viseme_PP', 'viseme_FF', 'viseme_TH', 'viseme_DD', 'viseme_kk', 'viseme_CH', 'viseme_SS', 'viseme_nn', 'viseme_RR', 'viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U'];
          const arkitMouthShapes = ['jawOpen', 'mouthFunnel', 'mouthPucker', 'mouthLeft', 'mouthRight', 'mouthSmile_L', 'mouthSmile_R', 'mouthFrown_L', 'mouthFrown_R', 'mouthClose'];
          
          const availableOculus = oculusVisemes.filter(viseme => node.morphTargetDictionary[viseme] !== undefined);
          const availableARKit = arkitMouthShapes.filter(shape => node.morphTargetDictionary[shape] !== undefined);
          
          // Use this mesh if it has either:
          // - At least 10 Oculus visemes (67% coverage) OR
          // - At least 6 ARKit mouth shapes (60% coverage)
          if (availableOculus.length >= 10) {
            console.log('🎭 Found avatar with Oculus visemes:', node.name);
            console.log('📊 All available morph targets:', Object.keys(node.morphTargetDictionary));
            console.log('✅ Available Oculus visemes:', availableOculus);
            console.log('🎯 Using OCULUS VISEME MODE for lip sync with', availableOculus.length, '/15 visemes');
            setFaceMesh(node);
            foundValidFaceMesh = true;
          } else if (availableARKit.length >= 6) {
            console.log('🎭 Found avatar with ARKit blend shapes:', node.name);
            console.log('📊 All available morph targets:', Object.keys(node.morphTargetDictionary));
            console.log('✅ Available ARKit mouth shapes:', availableARKit);
            console.log('🔍 ARKit blend shapes:', Object.keys(node.morphTargetDictionary).filter(key => key.startsWith('eye') || key.startsWith('mouth') || key.startsWith('brow') || key.startsWith('cheek') || key.startsWith('nose') || key.startsWith('jaw') || key.startsWith('tongue')));
            console.log('🎯 Using ARKIT MODE for lip sync with', availableARKit.length, 'mouth shapes (will convert from phonemes)');
            setFaceMesh(node);
            foundValidFaceMesh = true;
          } else {
            console.log('⚠️ Skipping mesh', node.name, '- insufficient morph targets (Oculus:', availableOculus.length, ', ARKit:', availableARKit.length, ')');
          }
        }
      });
      
      // If no valid face mesh found, create fallback avatar
      if (!foundValidFaceMesh) {
        console.warn('❌ Avatar has insufficient morph targets! Creating enhanced fallback avatar...');
        createFallbackAvatar();
      }
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