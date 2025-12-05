/**
 * Procedural Avatar Viewer - Generates a 3D head programmatically
 * No model files needed - pure Three.js geometry
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, head;
let stats = { fps: 0, triangles: 0, frameCount: 0 };

function init() {
  // Setup scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a2e);
  scene.fog = new THREE.Fog(0x1a1a2e, 100, 1000);

  // Setup camera
  camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(0, 0, 2.5);
  camera.lookAt(0, 0.2, 0);

  // Setup renderer
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  document.body.appendChild(renderer.domElement);

  // Setup controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.autoRotate = true;
  controls.autoRotateSpeed = 3;
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0, 0.3, 0);
  controls.update();

  // Setup lighting
  setupLights();

  // Create procedural head
  createProceduralHead();

  // Event listeners
  window.addEventListener('resize', onWindowResize);
  document.addEventListener('keydown', onKeyDown);

  // Start animation
  animate();

  console.log('%c✅ Procedural Avatar Viewer Ready!', 'color: #00ff00; font-size: 16px; font-weight: bold;');
}

function setupLights() {
  // Key light (warm)
  const keyLight = new THREE.DirectionalLight(0xffdd99, 1.0);
  keyLight.position.set(3, 4, 2);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.width = 2048;
  keyLight.shadow.mapSize.height = 2048;
  scene.add(keyLight);

  // Fill light (cool)
  const fillLight = new THREE.DirectionalLight(0x99ddff, 0.4);
  fillLight.position.set(-3, 2, 2);
  scene.add(fillLight);

  // Back light
  const backLight = new THREE.DirectionalLight(0xff99dd, 0.3);
  backLight.position.set(0, 2, -3);
  scene.add(backLight);

  // Ambient
  scene.add(new THREE.AmbientLight(0xffffff, 0.5));
}

function createProceduralHead() {
  head = new THREE.Group();

  // Head geometry (sphere + adjustments)
  const headGeometry = createHeadGeometry();
  const headMaterial = new THREE.MeshStandardMaterial({
    color: 0xd4a574,
    metalness: 0.0,
    roughness: 0.7,
    side: THREE.FrontSide,
  });
  const headMesh = new THREE.Mesh(headGeometry, headMaterial);
  headMesh.castShadow = true;
  headMesh.receiveShadow = true;
  head.add(headMesh);

  // Eyes
  const eyeGeometry = new THREE.SphereGeometry(0.08, 32, 32);
  const eyeMaterial = new THREE.MeshStandardMaterial({
    color: 0x8b4513,
    metalness: 0.2,
    roughness: 0.3,
  });

  const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
  leftEye.position.set(-0.18, 0.35, 0.4);
  leftEye.castShadow = true;
  head.add(leftEye);

  const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
  rightEye.position.set(0.18, 0.35, 0.4);
  rightEye.castShadow = true;
  head.add(rightEye);

  // Eye shine (specular highlights)
  const shineGeometry = new THREE.SphereGeometry(0.03, 16, 16);
  const shineMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    metalness: 1.0,
    roughness: 0.0,
  });

  const leftShine = new THREE.Mesh(shineGeometry, shineMaterial);
  leftShine.position.set(-0.18, 0.35, 0.46);
  head.add(leftShine);

  const rightShine = new THREE.Mesh(shineGeometry, shineMaterial);
  rightShine.position.set(0.18, 0.35, 0.46);
  head.add(rightShine);

  // Nose
  const noseGeometry = new THREE.ConeGeometry(0.05, 0.15, 16);
  const noseMaterial = new THREE.MeshStandardMaterial({
    color: 0xc89968,
    metalness: 0.0,
    roughness: 0.8,
  });
  const nose = new THREE.Mesh(noseGeometry, noseMaterial);
  nose.position.set(0, 0.15, 0.45);
  nose.castShadow = true;
  head.add(nose);

  // Mouth (simple ellipsoid)
  const mouthGeometry = new THREE.BoxGeometry(0.15, 0.03, 0.05);
  const mouthMaterial = new THREE.MeshStandardMaterial({
    color: 0xa0573d,
    metalness: 0.0,
    roughness: 0.9,
  });
  const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
  mouth.position.set(0, -0.05, 0.45);
  mouth.castShadow = true;
  head.add(mouth);

  // Hair
  const hairGeometry = new THREE.SphereGeometry(0.52, 32, 32, 0, Math.PI * 2, 0, Math.PI * 0.6);
  const hairMaterial = new THREE.MeshStandardMaterial({
    color: 0x3d2817,
    metalness: 0.0,
    roughness: 0.8,
    side: THREE.FrontSide,
  });
  const hair = new THREE.Mesh(hairGeometry, hairMaterial);
  hair.position.y = 0.15;
  hair.castShadow = true;
  head.add(hair);

  // Ears
  const earGeometry = new THREE.SphereGeometry(0.08, 16, 16, 0, Math.PI);
  const earMaterial = new THREE.MeshStandardMaterial({
    color: 0xd4a574,
    metalness: 0.0,
    roughness: 0.7,
  });

  const leftEar = new THREE.Mesh(earGeometry, earMaterial);
  leftEar.position.set(-0.48, 0.2, 0);
  leftEar.scale.set(1, 1.3, 0.8);
  leftEar.castShadow = true;
  head.add(leftEar);

  const rightEar = new THREE.Mesh(earGeometry, earMaterial);
  rightEar.position.set(0.48, 0.2, 0);
  rightEar.scale.set(1, 1.3, 0.8);
  rightEar.castShadow = true;
  head.add(rightEar);

  // Neck
  const neckGeometry = new THREE.ConeGeometry(0.22, 0.3, 32);
  const neckMaterial = new THREE.MeshStandardMaterial({
    color: 0xd4a574,
    metalness: 0.0,
    roughness: 0.7,
  });
  const neck = new THREE.Mesh(neckGeometry, neckMaterial);
  neck.position.y = -0.45;
  neck.castShadow = true;
  head.add(neck);

  scene.add(head);

  // Count geometry
  let triangles = 0;
  head.traverse((child) => {
    if (child.geometry) {
      triangles += child.geometry.attributes.position.count / 3;
    }
  });
  stats.triangles = Math.round(triangles);

  console.log(`✅ Created procedural head with ${stats.triangles} triangles`);
}

function createHeadGeometry() {
  // Create a basic head shape using a deformed sphere
  const geometry = new THREE.IcosahedronGeometry(0.5, 5);

  // Deform vertices to look more like a head
  const positions = geometry.attributes.position;
  const positionArray = positions.array;

  for (let i = 0; i < positionArray.length; i += 3) {
    const x = positionArray[i];
    const y = positionArray[i + 1];
    const z = positionArray[i + 2];

    // Elongate in Y (make it taller)
    positionArray[i + 1] *= 1.3;

    // Add some width variation
    const dist = Math.sqrt(x * x + z * z);
    if (y > 0.2) {
      // Top part (head) - make it rounder
      positionArray[i] *= 1.1;
      positionArray[i + 2] *= 1.2;
    } else if (y < -0.2) {
      // Bottom part (chin) - make it narrower
      positionArray[i] *= 0.8;
      positionArray[i + 2] *= 0.8;
    }
  }

  positions.needsUpdate = true;
  geometry.computeVertexNormals();

  return geometry;
}

function animate() {
  requestAnimationFrame(animate);

  // Update animation
  controls.update();

  // Simple head animation (slight tilt)
  if (head) {
    head.rotation.z = Math.sin(Date.now() * 0.0003) * 0.05;
  }

  renderer.render(scene, camera);

  // Update stats
  stats.frameCount++;
  updateStats();
}

function updateStats() {
  const fpsDisplay = document.getElementById('fps');
  const trianglesDisplay = document.getElementById('triangles');

  if (fpsDisplay) fpsDisplay.textContent = Math.round(1000 / (Date.now() - stats.lastTime || Date.now()));
  if (trianglesDisplay) trianglesDisplay.textContent = stats.triangles;

  stats.lastTime = Date.now();
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function onKeyDown(e) {
  if (e.code === 'Space') {
    controls.autoRotate = !controls.autoRotate;
    console.log(`Auto-rotation: ${controls.autoRotate ? 'ON' : 'OFF'}`);
  }
}

// Start
init();
