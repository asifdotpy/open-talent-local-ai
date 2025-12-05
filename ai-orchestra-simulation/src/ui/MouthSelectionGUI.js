import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import * as THREE from 'three';
import { Logger } from '../utils/Logger.js';

/**
 * GUI for mouth vertex selection and bounding box configuration
 */
export class MouthSelectionGUI {
  constructor(meshManager, scene) {
    this.meshManager = meshManager;
    this.scene = scene;
    this.logger = Logger.getInstance();
    this.gui = null;

    // GUI configuration
    this.mouthBoxConfig = {
      minX: -0.1,
      minY: 0.7,
      minZ: 0.45,
      maxX: 0.1,
      maxY: 0.8,
      maxZ: 0.6,
      update: () => this.updateMouthVertices(),
    };

    // GUI constraints
    this.GUI_CONSTRAINTS = {
      POSITION_RANGE: { min: -100.0, max: 100.0, step: 0.1 },
      HEIGHT_RANGE: { min: 130.0, max: 185.0, step: 0.1 },
      DEPTH_RANGE: { min: -15.0, max: 20.0, step: 0.1 },
    };

    // Visual helpers
    this.mouthBoxHelper = null;
    this.mouthPointsHelper = null;

    this.init();
  }

  init() {
    this.logger.log('INFO', 'Initializing Mouth Selection GUI');

    this.gui = new GUI();
    this.gui.title('Mouth Selection');

    this.createBoundingBoxControls();
    this.createVisualHelpers();

    this.logger.log('SUCCESS', 'Mouth Selection GUI initialized');
  }

  createBoundingBoxControls() {
    const boxFolder = this.gui.addFolder('Mouth Bounding Box');

    boxFolder
      .add(
        this.mouthBoxConfig,
        'minX',
        this.GUI_CONSTRAINTS.POSITION_RANGE.min,
        this.GUI_CONSTRAINTS.POSITION_RANGE.max,
        this.GUI_CONSTRAINTS.POSITION_RANGE.step
      )
      .name('Min X')
      .onChange(this.mouthBoxConfig.update);

    boxFolder
      .add(
        this.mouthBoxConfig,
        'minY',
        this.GUI_CONSTRAINTS.HEIGHT_RANGE.min,
        this.GUI_CONSTRAINTS.HEIGHT_RANGE.max,
        this.GUI_CONSTRAINTS.HEIGHT_RANGE.step
      )
      .name('Min Y')
      .onChange(this.mouthBoxConfig.update);

    boxFolder
      .add(
        this.mouthBoxConfig,
        'minZ',
        this.GUI_CONSTRAINTS.DEPTH_RANGE.min,
        this.GUI_CONSTRAINTS.DEPTH_RANGE.max,
        this.GUI_CONSTRAINTS.DEPTH_RANGE.step
      )
      .name('Min Z')
      .onChange(this.mouthBoxConfig.update);

    boxFolder
      .add(
        this.mouthBoxConfig,
        'maxX',
        this.GUI_CONSTRAINTS.POSITION_RANGE.min,
        this.GUI_CONSTRAINTS.POSITION_RANGE.max,
        this.GUI_CONSTRAINTS.POSITION_RANGE.step
      )
      .name('Max X')
      .onChange(this.mouthBoxConfig.update);

    boxFolder
      .add(
        this.mouthBoxConfig,
        'maxY',
        this.GUI_CONSTRAINTS.HEIGHT_RANGE.min,
        this.GUI_CONSTRAINTS.HEIGHT_RANGE.max,
        this.GUI_CONSTRAINTS.HEIGHT_RANGE.step
      )
      .name('Max Y')
      .onChange(this.mouthBoxConfig.update);

    boxFolder
      .add(
        this.mouthBoxConfig,
        'maxZ',
        this.GUI_CONSTRAINTS.DEPTH_RANGE.min,
        this.GUI_CONSTRAINTS.DEPTH_RANGE.max,
        this.GUI_CONSTRAINTS.DEPTH_RANGE.step
      )
      .name('Max Z')
      .onChange(this.mouthBoxConfig.update);

    boxFolder.open();
  }

  createVisualHelpers() {
    // Mouth bounding box helper
    const mouthBox = new THREE.Box3();
    this.mouthBoxHelper = new THREE.Box3Helper(mouthBox, 0x00ff00); // Green box
    this.mouthBoxHelper.visible = false; // Hide by default for cleaner view
    this.scene.add(this.mouthBoxHelper);

    // Mouth points helper
    const geometry = new THREE.BufferGeometry();
    const material = new THREE.PointsMaterial({ color: 0xff00ff, size: 2.0 });
    this.mouthPointsHelper = new THREE.Points(geometry, material);
    this.mouthPointsHelper.visible = false; // Hide by default for cleaner view
    this.scene.add(this.mouthPointsHelper);

    this.updateVisualHelpers();
  }

  updateMouthVertices() {
    if (!this.meshManager || !this.meshManager.headMesh) {
      this.logger.log('WARNING', 'No head mesh available for mouth vertex detection');
      return;
    }

    this.logger.log('INFO', 'Updating mouth vertices with new bounding box parameters');

    // Use the mesh manager's advanced detection if available, otherwise fall back to simple method
    if (this.meshManager.identifyMouthVertices) {
      this.meshManager.identifyMouthVertices(this.mouthBoxConfig);
    } else {
      // Fallback to simple bounding box detection
      this.detectMouthVerticesSimple();
    }

    this.updateVisualHelpers();
  }

  detectMouthVerticesSimple() {
    const mesh = this.meshManager.headMesh;
    if (!mesh || !mesh.geometry || !mesh.geometry.attributes.position) {
      this.logger.log('ERROR', 'Invalid mesh for mouth vertex detection');
      return;
    }

    const positionAttribute = mesh.geometry.attributes.position;
    const mouthVertices = [];
    const originalPositions = [];

    const box = new THREE.Box3(
      new THREE.Vector3(this.mouthBoxConfig.minX, this.mouthBoxConfig.minY, this.mouthBoxConfig.minZ),
      new THREE.Vector3(this.mouthBoxConfig.maxX, this.mouthBoxConfig.maxY, this.mouthBoxConfig.maxZ)
    );

    for (let i = 0; i < positionAttribute.count; i++) {
      const vertex = new THREE.Vector3();
      vertex.fromBufferAttribute(positionAttribute, i);

      if (box.containsPoint(vertex)) {
        mouthVertices.push(i);
        originalPositions.push(vertex.clone());
      }
    }

    // Update mesh manager with detected vertices
    this.meshManager.mouthVertexIndices = mouthVertices;
    this.meshManager.originalMouthPositions = originalPositions;

    // Calculate mouth center Y
    if (originalPositions.length > 0) {
      this.meshManager.mouthCenterY = originalPositions.reduce((sum, pos) => sum + pos.y, 0) / originalPositions.length;
    }

    this.logger.log('SUCCESS', `Detected ${mouthVertices.length} mouth vertices using bounding box`);
  }

  updateVisualHelpers() {
    if (!this.mouthBoxHelper || !this.mouthPointsHelper) return;

    // Update bounding box helper
    const mouthBox = this.mouthBoxHelper.box;
    mouthBox.min.set(
      this.mouthBoxConfig.minX,
      this.mouthBoxConfig.minY,
      this.mouthBoxConfig.minZ
    );
    mouthBox.max.set(
      this.mouthBoxConfig.maxX,
      this.mouthBoxConfig.maxY,
      this.mouthBoxConfig.maxZ
    );

    // Update points helper
    if (this.meshManager && this.meshManager.originalMouthPositions) {
      const positions = this.meshManager.originalMouthPositions;
      if (positions.length > 0) {
        const helperPositions = new Float32Array(positions.length * 3);
        positions.forEach((pos, i) => pos.toArray(helperPositions, i * 3));

        this.mouthPointsHelper.geometry.setAttribute(
          'position',
          new THREE.BufferAttribute(helperPositions, 3)
        );
      }
    }
  }

  toggleHelpers() {
    if (this.mouthBoxHelper) {
      this.mouthBoxHelper.visible = !this.mouthBoxHelper.visible;
    }
    if (this.mouthPointsHelper) {
      this.mouthPointsHelper.visible = !this.mouthPointsHelper.visible;
    }

    const visible = this.mouthBoxHelper?.visible || false;
    this.logger.log('INFO', `Mouth helpers ${visible ? 'shown' : 'hidden'}`);
  }

  updateConfig(newConfig) {
    Object.assign(this.mouthBoxConfig, newConfig);
    this.updateMouthVertices();
  }

  getConfig() {
    return { ...this.mouthBoxConfig };
  }

  dispose() {
    if (this.gui) {
      this.gui.destroy();
      this.gui = null;
    }

    if (this.mouthBoxHelper) {
      this.scene.remove(this.mouthBoxHelper);
      this.mouthBoxHelper = null;
    }

    if (this.mouthPointsHelper) {
      this.scene.remove(this.mouthPointsHelper);
      if (this.mouthPointsHelper.geometry) {
        this.mouthPointsHelper.geometry.dispose();
      }
      if (this.mouthPointsHelper.material) {
        this.mouthPointsHelper.material.dispose();
      }
      this.mouthPointsHelper = null;
    }

    this.logger.log('SUCCESS', 'Mouth Selection GUI disposed');
  }
}