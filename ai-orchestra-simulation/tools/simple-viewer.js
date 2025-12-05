/**
 * Simple Avatar Viewer - Minimal implementation for model visualization
 * Loads and displays 3D avatar with basic controls
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// Global variables
let scene, camera, renderer, controls, model;
const loader = new GLTFLoader();

// Initialize the application
function init() {
  // Setup scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a233f);
  scene.fog = new THREE.Fog(0x1a233f, 100, 1000);

  // Setup camera
  camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(0, 1.5, 2.5);
  camera.lookAt(0, 1, 0);

  // Setup renderer
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowShadowMap;
  document.body.appendChild(renderer.domElement);

  // Setup controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.autoRotate = true;
  controls.autoRotateSpeed = 2;
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0, 1, 0);
  controls.update();

  // Setup lighting
  setupLights();

  // Load model
  loadModel();

  // Handle window resize
  window.addEventListener('resize', onWindowResize);

  // Start animation loop
  animate();

  // Log instructions
  console.log('%c🎭 Avatar Viewer Ready!', 'color: #00ff00; font-size: 16px; font-weight: bold;');
  console.log('%cControls:', 'color: #00ffff; font-size: 12px;');
  console.log('• Mouse drag: Rotate');
  console.log('• Scroll: Zoom');
  console.log('• Right-click + drag: Pan');
  console.log('• Press SPACE to toggle auto-rotation');
}

// Setup lighting
function setupLights() {
  // Ambient light
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  // Main directional light
  const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
  mainLight.position.set(5, 10, 7);
  mainLight.castShadow = true;
  mainLight.shadow.mapSize.width = 2048;
  mainLight.shadow.mapSize.height = 2048;
  mainLight.shadow.camera.near = 0.5;
  mainLight.shadow.camera.far = 500;
  mainLight.shadow.camera.left = -50;
  mainLight.shadow.camera.right = 50;
  mainLight.shadow.camera.top = 50;
  mainLight.shadow.camera.bottom = -50;
  scene.add(mainLight);

  // Fill light
  const fillLight = new THREE.DirectionalLight(0x88ccff, 0.4);
  fillLight.position.set(-5, 5, -10);
  scene.add(fillLight);

  // Back light
  const backLight = new THREE.DirectionalLight(0xff6b9d, 0.3);
  backLight.position.set(0, 5, -10);
  scene.add(backLight);
}

// Load 3D model
function loadModel() {
  const modelPath = './assets/models/metaHumanHead.glb';

  loader.load(
    modelPath,
    (gltf) => {
      model = gltf.scene;
      model.scale.set(1, 1, 1);
      model.position.y = 0;
      scene.add(model);

      // Log model info
      console.log('✅ Model loaded successfully!');
      console.log('Model info:', {
        meshes: countMeshes(model),
        materials: countMaterials(model),
        scale: model.scale.toArray(),
        position: model.position.toArray(),
      });

      // Cast shadows
      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });
    },
    (progress) => {
      const percent = Math.round((progress.loaded / progress.total) * 100);
      console.log(`Loading: ${percent}%`);
    },
    (error) => {
      console.error('❌ Error loading model:', error);
      showErrorMessage(`Failed to load model: ${error.message}`);
    }
  );
}

// Count meshes in model
function countMeshes(obj) {
  let count = 0;
  obj.traverse((child) => {
    if (child.isMesh) count++;
  });
  return count;
}

// Count materials in model
function countMaterials(obj) {
  const materials = new Set();
  obj.traverse((child) => {
    if (child.isMesh) {
      if (Array.isArray(child.material)) {
        child.material.forEach((m) => materials.add(m));
      } else {
        materials.add(child.material);
      }
    }
  });
  return materials.size;
}

// Show error message
function showErrorMessage(message) {
  const div = document.createElement('div');
  div.style.cssText = `
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: #ff4444;
    color: white;
    padding: 20px;
    border-radius: 10px;
    font-size: 18px;
    z-index: 1000;
    text-align: center;
  `;
  div.innerText = message;
  document.body.appendChild(div);
}

// Animation loop
function animate() {
  requestAnimationFrame(animate);

  controls.update();

  renderer.render(scene, camera);
}

// Handle window resize
function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

// Toggle auto-rotation
document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') {
    controls.autoRotate = !controls.autoRotate;
    console.log(`Auto-rotation ${controls.autoRotate ? 'ON' : 'OFF'}`);
  }
});

// Start application
init();
