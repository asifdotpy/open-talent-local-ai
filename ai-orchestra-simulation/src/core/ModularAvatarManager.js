/**
 * ModularAvatarManager.js - Advanced modular avatar system
 * Supports component-based avatar assembly with hair, skin, gender features
 * Extends ModelManager for enhanced modularity and customization
 */
import * as THREE from 'three'
import { ModelManager } from './ModelManager.js'

export class ModularAvatarManager extends ModelManager {
  constructor(config, options = {}) {
    super(config, options)

    // Modular components
    this.components = {
      head: null,
      hair: null,
      skin: null,
      gender: null,
      accessories: []
    }

    // Component configurations
    this.componentConfigs = {
      hair: {
        styles: ['short', 'medium', 'long', 'curly', 'straight', 'afro', 'bald'],
        colors: ['black', 'brown', 'blonde', 'red', 'gray', 'white']
      },
      skin: {
        tones: ['light', 'medium', 'tan', 'dark', 'deep']
      },
      gender: {
        features: ['masculine', 'feminine', 'neutral']
      }
    }

    // Active component state
    this.activeComponents = new Map()
  }

  /**
   * Load modular avatar with specified components
   * @param {Object} avatarSpec - Avatar specification with components
   * @returns {Promise<Object3D>}
   */
  async loadModularAvatar(avatarSpec = {}) {
    const avatar = new THREE.Group()
    avatar.name = 'ModularAvatar'

    // Load base head component
    const headComponent = await this.loadComponent('head', avatarSpec.head || 'default')
    if (headComponent) {
      avatar.add(headComponent)
      this.components.head = headComponent
    }

    // Load hair component
    if (avatarSpec.hair) {
      const hairComponent = await this.loadComponent('hair', avatarSpec.hair)
      if (hairComponent) {
        avatar.add(hairComponent)
        this.components.hair = hairComponent
      }
    }

    // Load skin modifications
    if (avatarSpec.skin) {
      await this.applySkinTone(avatar, avatarSpec.skin)
    }

    // Load gender-specific features
    if (avatarSpec.gender) {
      await this.applyGenderFeatures(avatar, avatarSpec.gender)
    }

    // Load accessories
    if (avatarSpec.accessories) {
      for (const accessorySpec of avatarSpec.accessories) {
        const accessory = await this.loadComponent('accessory', accessorySpec)
        if (accessory) {
          avatar.add(accessory)
          this.components.accessories.push(accessory)
        }
      }
    }

    // Apply final transformations and setup
    this.setupAvatar(avatar)

    return avatar
  }

  /**
   * Load individual component
   * @param {string} componentType - Type of component (head, hair, accessory)
   * @param {Object|string} componentSpec - Component specification
   * @returns {Promise<Object3D>}
   */
  async loadComponent(componentType, componentSpec) {
    const spec = typeof componentSpec === 'string' ? { style: componentSpec } : componentSpec

    switch (componentType) {
      case 'head':
        return this.loadHeadComponent(spec)
      case 'hair':
        return this.loadHairComponent(spec)
      case 'accessory':
        return this.loadAccessoryComponent(spec)
      default:
        throw new Error(`Unknown component type: ${componentType}`)
    }
  }

  /**
   * Load head component with morph targets
   * @param {Object} spec - Head specification
   * @returns {Promise<Object3D>}
   */
  async loadHeadComponent(spec) {
    // Use existing model loading for base head
    const headModel = await this.loadModel(spec.style || 'face')

    // Apply head-specific modifications
    headModel.traverse((child) => {
      if (child.isMesh) {
        // Ensure morph targets are properly set up
        this.ensureMorphTargets(child)
      }
    })

    return headModel
  }

  /**
   * Load hair component
   * @param {Object} spec - Hair specification
   * @returns {Promise<Object3D>}
   */
  async loadHairComponent(spec) {
    const hairGroup = new THREE.Group()
    hairGroup.name = 'HairComponent'

    const style = spec.style || 'short'
    const color = spec.color || 'black'

    // Create procedural hair based on style
    const hairGeometry = this.createHairGeometry(style)
    const hairMaterial = this.createHairMaterial(color)

    const hairMesh = new THREE.Mesh(hairGeometry, hairMaterial)
    hairMesh.name = `Hair_${style}_${color}`

    // Position hair on head
    hairMesh.position.set(0, 0.8, 0.1)

    hairGroup.add(hairMesh)

    // Add secondary hair elements for more complex styles
    if (style === 'long' || style === 'curly') {
      const secondaryHair = new THREE.Mesh(
        this.createSecondaryHairGeometry(style),
        hairMaterial.clone()
      )
      secondaryHair.position.set(0, 0.5, 0.2)
      hairGroup.add(secondaryHair)
    }

    return hairGroup
  }

  /**
   * Create hair geometry based on style
   * @param {string} style - Hair style
   * @returns {BufferGeometry}
   */
  createHairGeometry(style) {
    switch (style) {
      case 'short':
        return new THREE.CylinderGeometry(0.6, 0.8, 0.3, 8)
      case 'medium':
        return new THREE.CylinderGeometry(0.7, 0.9, 0.5, 8)
      case 'long':
        return new THREE.CylinderGeometry(0.8, 1.0, 0.8, 8)
      case 'curly':
        return new THREE.SphereGeometry(0.7, 16, 12)
      case 'straight':
        return new THREE.CylinderGeometry(0.6, 0.7, 0.6, 6)
      case 'afro':
        return new THREE.SphereGeometry(0.8, 16, 16)
      case 'bald':
        return new THREE.PlaneGeometry(0.1, 0.1) // Minimal geometry
      default:
        return new THREE.CylinderGeometry(0.6, 0.8, 0.3, 8)
    }
  }

  /**
   * Create secondary hair geometry for complex styles
   * @param {string} style - Hair style
   * @returns {BufferGeometry}
   */
  createSecondaryHairGeometry(style) {
    if (style === 'long') {
      return new THREE.CylinderGeometry(0.3, 0.5, 0.6, 6)
    } else if (style === 'curly') {
      return new THREE.TorusGeometry(0.4, 0.2, 8, 16)
    }
    return new THREE.PlaneGeometry(0.1, 0.1)
  }

  /**
   * Create hair material with specified color
   * @param {string} color - Hair color
   * @returns {Material}
   */
  createHairMaterial(color) {
    const colorMap = {
      black: 0x1a1a1a,
      brown: 0x8B4513,
      blonde: 0xFFD700,
      red: 0xDC143C,
      gray: 0x808080,
      white: 0xF5F5F5
    }

    return new THREE.MeshLambertMaterial({
      color: colorMap[color] || colorMap.black,
      transparent: color === 'bald' // Make bald hair invisible
    })
  }

  /**
   * Apply skin tone to avatar
   * @param {Object3D} avatar - Avatar model
   * @param {Object} skinSpec - Skin specification
   */
  async applySkinTone(avatar, skinSpec) {
    const tone = skinSpec.tone || 'medium'

    const skinColors = {
      light: 0xF5DEB3,
      medium: 0xD2B48C,
      tan: 0xCD853F,
      dark: 0x8B4513,
      deep: 0x654321
    }

    const skinColor = skinColors[tone] || skinColors.medium

    avatar.traverse((child) => {
      if (child.isMesh && child.name.includes('Head')) {
        if (Array.isArray(child.material)) {
          child.material.forEach(mat => {
            if (mat.name && mat.name.toLowerCase().includes('skin')) {
              mat.color.setHex(skinColor)
            }
          })
        } else if (child.material) {
          child.material.color.setHex(skinColor)
        }
      }
    })
  }

  /**
   * Apply gender-specific features
   * @param {Object3D} avatar - Avatar model
   * @param {Object} genderSpec - Gender specification
   */
  async applyGenderFeatures(avatar, genderSpec) {
    const features = genderSpec.features || 'neutral'

    avatar.traverse((child) => {
      if (child.isMesh && child.morphTargetDictionary) {
        // Apply gender-specific morph target influences
        switch (features) {
          case 'feminine':
            this.applyFeminineFeatures(child)
            break
          case 'masculine':
            this.applyMasculineFeatures(child)
            break
          case 'neutral':
          default:
            // No modifications for neutral
            break
        }
      }
    })
  }

  /**
   * Apply feminine facial features
   * @param {Mesh} mesh - Mesh to modify
   */
  applyFeminineFeatures(mesh) {
    // Enhance feminine features through morph targets
    if (mesh.morphTargetDictionary.eyeWiden !== undefined) {
      mesh.morphTargetInfluences[mesh.morphTargetDictionary.eyeWiden] = 0.3
    }
    if (mesh.morphTargetDictionary.cheekRaise !== undefined) {
      mesh.morphTargetInfluences[mesh.morphTargetDictionary.cheekRaise] = 0.2
    }
  }

  /**
   * Apply masculine facial features
   * @param {Mesh} mesh - Mesh to modify
   */
  applyMasculineFeatures(mesh) {
    // Enhance masculine features through morph targets
    if (mesh.morphTargetDictionary.eyeNarrow !== undefined) {
      mesh.morphTargetInfluences[mesh.morphTargetDictionary.eyeNarrow] = 0.2
    }
    if (mesh.morphTargetDictionary.eyebrowFrown !== undefined) {
      mesh.morphTargetInfluences[mesh.morphTargetDictionary.eyebrowFrown] = 0.1
    }
  }

  /**
   * Load accessory component
   * @param {Object} spec - Accessory specification
   * @returns {Promise<Object3D>}
   */
  async loadAccessoryComponent(spec) {
    const accessoryGroup = new THREE.Group()
    accessoryGroup.name = `Accessory_${spec.type}`

    switch (spec.type) {
      case 'glasses':
        const glasses = this.createGlasses(spec.style || 'round')
        accessoryGroup.add(glasses)
        break
      case 'hat':
        const hat = this.createHat(spec.style || 'cap')
        accessoryGroup.add(hat)
        break
      case 'earrings':
        const earrings = this.createEarrings(spec.style || 'stud')
        accessoryGroup.add(earrings)
        break
      default:
        console.warn(`Unknown accessory type: ${spec.type}`)
    }

    return accessoryGroup
  }

  /**
   * Create glasses accessory
   * @param {string} style - Glasses style
   * @returns {Object3D}
   */
  createGlasses(style) {
    const glassesGroup = new THREE.Group()

    // Frame geometry
    const frameGeometry = new THREE.TorusGeometry(0.15, 0.02, 8, 16)
    const frameMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 })

    // Left lens
    const leftLens = new THREE.Mesh(frameGeometry, frameMaterial)
    leftLens.position.set(-0.2, 0.1, 0.4)
    glassesGroup.add(leftLens)

    // Right lens
    const rightLens = new THREE.Mesh(frameGeometry, frameMaterial)
    rightLens.position.set(0.2, 0.1, 0.4)
    glassesGroup.add(rightLens)

    // Bridge
    const bridgeGeometry = new THREE.CylinderGeometry(0.01, 0.01, 0.1, 8)
    const bridge = new THREE.Mesh(bridgeGeometry, frameMaterial)
    bridge.rotation.z = Math.PI / 2
    bridge.position.set(0, 0.1, 0.4)
    glassesGroup.add(bridge)

    return glassesGroup
  }

  /**
   * Create hat accessory
   * @param {string} style - Hat style
   * @returns {Object3D}
   */
  createHat(style) {
    const hatGeometry = new THREE.CylinderGeometry(0.8, 0.6, 0.2, 16)
    const hatMaterial = new THREE.MeshBasicMaterial({ color: 0x333333 })

    const hat = new THREE.Mesh(hatGeometry, hatMaterial)
    hat.position.set(0, 1.0, 0)

    return hat
  }

  /**
   * Create earrings accessory
   * @param {string} style - Earrings style
   * @returns {Object3D}
   */
  createEarrings(style) {
    const earringsGroup = new THREE.Group()

    const earringGeometry = new THREE.SphereGeometry(0.05, 8, 8)
    const earringMaterial = new THREE.MeshBasicMaterial({ color: 0xFFD700 })

    // Left earring
    const leftEarring = new THREE.Mesh(earringGeometry, earringMaterial)
    leftEarring.position.set(-0.3, -0.1, 0.5)
    earringsGroup.add(leftEarring)

    // Right earring
    const rightEarring = new THREE.Mesh(earringGeometry, earringMaterial)
    rightEarring.position.set(0.3, -0.1, 0.5)
    earringsGroup.add(rightEarring)

    return earringsGroup
  }

  /**
   * Ensure morph targets are properly set up on mesh
   * @param {Mesh} mesh - Mesh to check/modify
   */
  ensureMorphTargets(mesh) {
    if (!mesh.morphTargetDictionary) {
      mesh.morphTargetDictionary = {}
    }
    if (!mesh.morphTargetInfluences) {
      mesh.morphTargetInfluences = []
    }

    // Ensure required morph targets exist
    const requiredTargets = [
      'jawOpen', 'mouthFunnel', 'mouthClose', 'mouthSmile',
      'eyebrowRaise', 'eyebrowFrown', 'eyeWiden', 'eyeNarrow',
      'mouthFrown', 'cheekRaise'
    ]

    requiredTargets.forEach(target => {
      if (mesh.morphTargetDictionary[target] === undefined) {
        const index = Object.keys(mesh.morphTargetDictionary).length
        mesh.morphTargetDictionary[target] = index
        mesh.morphTargetInfluences[index] = 0
      }
    })
  }

  /**
   * Setup final avatar configuration
   * @param {Object3D} avatar - Avatar model
   */
  setupAvatar(avatar) {
    // Position avatar appropriately
    avatar.position.set(0, 0, 0)
    avatar.scale.set(1, 1, 1)

    // Add any final setup logic here
    console.log('Modular avatar assembled with components:', Object.keys(this.components))
  }

  /**
   * Update component at runtime
   * @param {string} componentType - Type of component to update
   * @param {Object} newSpec - New component specification
   */
  async updateComponent(componentType, newSpec) {
    // Remove existing component
    if (this.components[componentType]) {
      this.components[componentType].parent.remove(this.components[componentType])
    }

    // Load new component
    const newComponent = await this.loadComponent(componentType, newSpec)
    if (newComponent) {
      // Add to avatar (assuming we have reference to avatar)
      if (this.currentModel) {
        this.currentModel.add(newComponent)
      }
      this.components[componentType] = newComponent
    }
  }

  /**
   * Get available component options
   * @param {string} componentType - Type of component
   * @returns {Object} Available options
   */
  getComponentOptions(componentType) {
    return this.componentConfigs[componentType] || {}
  }

  /**
   * Export avatar configuration
   * @returns {Object} Avatar specification
   */
  exportAvatarSpec() {
    const spec = {}

    if (this.components.head) spec.head = { style: 'face' }
    if (this.components.hair) {
      const hairName = this.components.hair.name
      const parts = hairName.split('_')
      spec.hair = { style: parts[1], color: parts[2] }
    }
    if (this.components.skin) spec.skin = { tone: 'medium' } // Would need to track this
    if (this.components.gender) spec.gender = { features: 'neutral' } // Would need to track this

    spec.accessories = this.components.accessories.map(acc => {
      const type = acc.name.split('_')[1]
      return { type, style: 'default' }
    })

    return spec
  }
}
