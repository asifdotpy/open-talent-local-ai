import * as THREE from 'https://cdn.jsdelivr.net/npm/three@r164/build/three.module.js';
import { GLTFExporter } from 'https://cdn.jsdelivr.net/npm/three@r164/examples/jsm/exporters/GLTFExporter.js';

// Create a simple head mesh with morph targets
const geometry = new THREE.IcosahedronGeometry(1, 5);

// Create base geometry positions for mouth deformations
const positionAttribute = geometry.getAttribute('position');
const positions = positionAttribute.array;

// Create morph target 1: Mouth Open
const mouthOpenTarget = new Float32Array(positions);
for (let i = 0; i < mouthOpenTarget.length; i += 3) {
  const x = mouthOpenTarget[i];
  const y = mouthOpenTarget[i + 1];
  const z = mouthOpenTarget[i + 2];
  
  // Deform vertices in mouth area (lower y area)
  if (y < 0.3 && y > -0.5 && Math.abs(x) < 0.3) {
    mouthOpenTarget[i + 1] -= 0.3; // Push down for mouth opening
  }
}

// Create morph target 2: Mouth Closed
const mouthClosedTarget = new Float32Array(positions);
for (let i = 0; i < mouthClosedTarget.length; i += 3) {
  const x = mouthClosedTarget[i];
  const y = mouthClosedTarget[i + 1];
  
  if (y < 0.3 && y > -0.5 && Math.abs(x) < 0.3) {
    mouthClosedTarget[i + 1] += 0.15;
  }
}

// Add morph targets
geometry.morphAttributes.position = [
  new THREE.BufferAttribute(mouthOpenTarget, 3),
  new THREE.BufferAttribute(mouthClosedTarget, 3)
];

// Create material and mesh
const material = new THREE.MeshPhongMaterial({ color: 0xffa3a3 });
const mesh = new THREE.SkinnedMesh(geometry, material);
mesh.morphTargetDictionary = {
  'mouth_open': 0,
  'mouth_closed': 1
};
mesh.morphTargetInfluences = [0, 0];

// Create scene and add mesh
const scene = new THREE.Scene();
scene.add(mesh);

// Add lights for better export
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 5, 5);
scene.add(light);

// Export to GLTF
const exporter = new GLTFExporter();
exporter.parse(scene, (gltf) => {
  const json = JSON.stringify(gltf);
  console.log('Model created with morph targets: mouth_open, mouth_closed');
  console.log('Model size:', (json.length / 1024).toFixed(2), 'KB');
  console.log('Morph targets:', Object.keys(mesh.morphTargetDictionary));
}, { binary: false });
