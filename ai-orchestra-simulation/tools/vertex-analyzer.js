/**
 * Vertex Analyzer Tool for face.glb
 * Analyzes GLTF model structure, vertex positions, and morph targets
 * Generates comprehensive debugging information
 * 
 * Uses @gltf-transform/core for GLB parsing (works in Node.js)
 */

import { NodeIO } from '@gltf-transform/core'
import {
    ALL_EXTENSIONS
} from '@gltf-transform/extensions'
import { mkdir, writeFile } from 'fs/promises'
import { MeshoptDecoder } from 'meshoptimizer'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

class VertexAnalyzer {
  constructor() {
    // Register all available extensions to handle compressed GLB files
    this.io = new NodeIO()
      .registerExtensions(ALL_EXTENSIONS)
      .registerDependencies({
        'meshopt.decoder': MeshoptDecoder
      })
    
    this.document = null
    this.analysisResults = {
      totalVertices: 0,
      totalPrimitives: 0,
      totalMeshes: 0,
      morphTargets: {},
      vertexRegions: {
        mouth: [],
        eyes: [],
        nose: [],
        jaw: [],
        other: []
      },
      boundingBox: null,
      geometryDetails: [],
      accessors: []
    }
  }

  /**
   * Load and analyze GLTF model
   */
  async analyze(modelPath) {
    console.log('🔍 Loading model:', modelPath)
    
    try {
      // Load GLTF document
      this.document = await this.io.read(modelPath)
      const root = this.document.getRoot()
      
      console.log('✅ Model loaded successfully using gltf-transform')
      console.log(`   Meshes: ${root.listMeshes().length}`)
      console.log(`   Accessors: ${root.listAccessors().length}`)
      console.log(`   Nodes: ${root.listNodes().length}`)
      
      // Analyze meshes and primitives
      this.analyzeMeshes()
      
      // Analyze vertices
      this.analyzeVertices()
      
      // Analyze morph targets
      this.analyzeMorphTargets()
      
      // Calculate statistics
      this.calculateStatistics()
      
      // Generate report
      return this.generateReport()
      
    } catch (error) {
      console.error('❌ Analysis failed:', error)
      throw error
    }
  }

  /**
   * Analyze all meshes in the document
   */
  analyzeMeshes() {
    console.log('\n📦 Analyzing meshes...')
    
    const meshes = this.document.getRoot().listMeshes()
    this.analysisResults.totalMeshes = meshes.length
    
    meshes.forEach((mesh, meshIndex) => {
      console.log(`\n  Mesh ${meshIndex + 1}: ${mesh.getName() || 'unnamed'}`)
      
      const primitives = mesh.listPrimitives()
      console.log(`    Primitives: ${primitives.length}`)
      
      primitives.forEach((primitive, primIndex) => {
        const positions = primitive.getAttribute('POSITION')
        const normals = primitive.getAttribute('NORMAL')
        const texCoords = primitive.getAttribute('TEXCOORD_0')
        const targets = primitive.listTargets()
        
        console.log(`\n    Primitive ${primIndex + 1}:`)
        console.log(`      Vertices: ${positions ? positions.getCount() : 0}`)
        console.log(`      Has normals: ${!!normals}`)
        console.log(`      Has UVs: ${!!texCoords}`)
        console.log(`      Morph targets: ${targets.length}`)
        
        // Store primitive details
        this.analysisResults.geometryDetails.push({
          meshIndex,
          meshName: mesh.getName() || 'unnamed',
          primitiveIndex: primIndex,
          vertexCount: positions ? positions.getCount() : 0,
          hasNormals: !!normals,
          hasUVs: !!texCoords,
          morphTargetCount: targets.length
        })
        
        this.analysisResults.totalPrimitives++
      })
    })
    
    console.log(`\n✅ Found ${meshes.length} mesh(es) with ${this.analysisResults.totalPrimitives} primitive(s)`)
  }

  /**
   * Analyze vertex positions and categorize by anatomical regions
   */
  analyzeVertices() {
    console.log('\n🎯 Analyzing vertex positions...')
    
    const meshes = this.document.getRoot().listMeshes()
    let totalVertices = 0
    
    meshes.forEach((mesh, meshIndex) => {
      const primitives = mesh.listPrimitives()
      
      primitives.forEach((primitive, primIndex) => {
        const positions = primitive.getAttribute('POSITION')
        if (!positions) {
          console.warn(`  ⚠️  Primitive ${primIndex} has no position attribute`)
          return
        }
        
        const vertexCount = positions.getCount()
        totalVertices += vertexCount
        
        console.log(`\n  Analyzing vertices in Mesh ${meshIndex + 1}, Primitive ${primIndex + 1}`)
        console.log(`    Total vertices: ${vertexCount}`)
        
        // Get position array (Vec3)
        const array = positions.getArray()
        if (!array || array.length === 0) {
          console.warn(`    ⚠️  No vertex data found`)
          return
        }
        
        // Analyze vertex distribution
        let minY = Infinity, maxY = -Infinity
        let minZ = Infinity, maxZ = -Infinity
        
        for (let i = 0; i < vertexCount; i++) {
          const x = array[i * 3 + 0]
          const y = array[i * 3 + 1]
          const z = array[i * 3 + 2]
          
          minY = Math.min(minY, y)
          maxY = Math.max(maxY, y)
          minZ = Math.min(minZ, z)
          maxZ = Math.max(maxZ, z)
        }
        
        console.log(`    Y range: ${minY.toFixed(3)} to ${maxY.toFixed(3)}`)
        console.log(`    Z range: ${minZ.toFixed(3)} to ${maxZ.toFixed(3)}`)
        
        // Categorize vertices by anatomical regions (based on Y coordinate)
        const yRange = maxY - minY
        const mouthThreshold = minY + (yRange * 0.3) // Lower 30% for mouth/jaw
        const eyeThreshold = minY + (yRange * 0.7) // Upper 30% for eyes
        
        let mouthCount = 0, jawCount = 0, eyeCount = 0, noseCount = 0, otherCount = 0
        
        for (let i = 0; i < vertexCount; i++) {
          const x = array[i * 3 + 0]
          const y = array[i * 3 + 1]
          const z = array[i * 3 + 2]
          
          const vertex = { index: i, x, y, z, mesh: meshIndex, primitive: primIndex }
          
          if (y < mouthThreshold) {
            this.analysisResults.vertexRegions.mouth.push(vertex)
            mouthCount++
          } else if (y > eyeThreshold) {
            this.analysisResults.vertexRegions.eyes.push(vertex)
            eyeCount++
          } else if (Math.abs(z) < 0.1 && y > mouthThreshold && y < eyeThreshold) {
            this.analysisResults.vertexRegions.nose.push(vertex)
            noseCount++
          } else if (y < mouthThreshold + (yRange * 0.1)) {
            this.analysisResults.vertexRegions.jaw.push(vertex)
            jawCount++
          } else {
            this.analysisResults.vertexRegions.other.push(vertex)
            otherCount++
          }
        }
        
        console.log(`    Region distribution:`)
        console.log(`      Mouth: ${mouthCount}`)
        console.log(`      Jaw: ${jawCount}`)
        console.log(`      Eyes: ${eyeCount}`)
        console.log(`      Nose: ${noseCount}`)
        console.log(`      Other: ${otherCount}`)
      })
    })
    
    this.analysisResults.totalVertices = totalVertices
    console.log(`\n  📊 Total Vertex Distribution:`)
    console.log(`    Total vertices: ${totalVertices}`)
    console.log(`    Mouth region: ${this.analysisResults.vertexRegions.mouth.length}`)
    console.log(`    Jaw region: ${this.analysisResults.vertexRegions.jaw.length}`)
    console.log(`    Eyes region: ${this.analysisResults.vertexRegions.eyes.length}`)
    console.log(`    Nose region: ${this.analysisResults.vertexRegions.nose.length}`)
    console.log(`    Other: ${this.analysisResults.vertexRegions.other.length}`)
  }

  /**
   * Analyze morph targets and their properties
   */
  analyzeMorphTargets() {
    console.log('\n🎭 Analyzing morph targets...')
    
    const meshes = this.document.getRoot().listMeshes()
    
    meshes.forEach((mesh, meshIndex) => {
      const primitives = mesh.listPrimitives()
      
      primitives.forEach((primitive, primIndex) => {
        const targets = primitive.listTargets()
        
        if (targets.length === 0) {
          console.log(`  Mesh ${meshIndex + 1}, Primitive ${primIndex + 1}: No morph targets`)
          return
        }
        
        console.log(`\n  Mesh ${meshIndex + 1}, Primitive ${primIndex + 1}: ${mesh.getName() || 'unnamed'}`)
        console.log(`    Morph targets: ${targets.length}`)
        
        // Get morph target names from extras (if available)
        const extras = primitive.getExtras()
        const targetNames = extras?.targetNames || []
        
        console.log(`    Morph target list:`)
        targets.forEach((target, idx) => {
          const name = targetNames[idx] || `target_${idx}`
          console.log(`      [${idx}] ${name}`)
        })
        
        // Check for required lip-sync targets
        const requiredTargets = ['jawOpen', 'mouthFunnel', 'mouthClose', 'mouthSmile']
        const foundTargets = requiredTargets.filter(target => targetNames.includes(target))
        const missingTargets = requiredTargets.filter(target => !targetNames.includes(target))
        
        if (foundTargets.length > 0) {
          console.log(`\n    ✅ Found lip-sync targets: ${foundTargets.join(', ')}`)
        }
        if (missingTargets.length > 0) {
          console.log(`    ⚠️  Missing lip-sync targets: ${missingTargets.join(', ')}`)
        }
        
        // Store morph target info
        const key = `mesh_${meshIndex}_prim_${primIndex}`
        this.analysisResults.morphTargets[key] = {
          meshName: mesh.getName() || 'unnamed',
          primitiveIndex: primIndex,
          count: targets.length,
          names: targetNames,
          hasRequiredTargets: missingTargets.length === 0,
          foundTargets,
          missingTargets
        }
      })
    })
  }

  /**
   * Calculate overall statistics
   */
  calculateStatistics() {
    console.log('\n📏 Calculating statistics...')
    
    // Calculate bounding box from all vertices
    let minX = Infinity, maxX = -Infinity
    let minY = Infinity, maxY = -Infinity
    let minZ = Infinity, maxZ = -Infinity
    
    const meshes = this.document.getRoot().listMeshes()
    meshes.forEach(mesh => {
      mesh.listPrimitives().forEach(primitive => {
        const positions = primitive.getAttribute('POSITION')
        if (!positions) return
        
        const array = positions.getArray()
        for (let i = 0; i < positions.getCount(); i++) {
          const x = array[i * 3 + 0]
          const y = array[i * 3 + 1]
          const z = array[i * 3 + 2]
          
          minX = Math.min(minX, x)
          maxX = Math.max(maxX, x)
          minY = Math.min(minY, y)
          maxY = Math.max(maxY, y)
          minZ = Math.min(minZ, z)
          maxZ = Math.max(maxZ, z)
        }
      })
    })
    
    const sizeX = maxX - minX
    const sizeY = maxY - minY
    const sizeZ = maxZ - minZ
    const centerX = (minX + maxX) / 2
    const centerY = (minY + maxY) / 2
    const centerZ = (minZ + maxZ) / 2
    
    this.analysisResults.boundingBox = {
      min: { x: minX, y: minY, z: minZ },
      max: { x: maxX, y: maxY, z: maxZ },
      size: { x: sizeX, y: sizeY, z: sizeZ },
      center: { x: centerX, y: centerY, z: centerZ }
    }
    
    console.log(`  Model bounding box:`)
    console.log(`    Min: (${minX.toFixed(3)}, ${minY.toFixed(3)}, ${minZ.toFixed(3)})`)
    console.log(`    Max: (${maxX.toFixed(3)}, ${maxY.toFixed(3)}, ${maxZ.toFixed(3)})`)
    console.log(`    Size: (${sizeX.toFixed(3)}, ${sizeY.toFixed(3)}, ${sizeZ.toFixed(3)})`)
    console.log(`    Center: (${centerX.toFixed(3)}, ${centerY.toFixed(3)}, ${centerZ.toFixed(3)})`)
  }

  /**
   * Generate comprehensive analysis report
   */
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalMeshes: this.analysisResults.totalMeshes,
        totalPrimitives: this.analysisResults.totalPrimitives,
        totalVertices: this.analysisResults.totalVertices,
        hasMorphTargets: Object.keys(this.analysisResults.morphTargets).length > 0,
        totalMorphTargets: Object.values(this.analysisResults.morphTargets)
          .reduce((sum, m) => sum + m.count, 0)
      },
      boundingBox: this.analysisResults.boundingBox,
      geometryDetails: this.analysisResults.geometryDetails,
      morphTargets: this.analysisResults.morphTargets,
      vertexRegions: {
        mouth: this.analysisResults.vertexRegions.mouth.length,
        jaw: this.analysisResults.vertexRegions.jaw.length,
        eyes: this.analysisResults.vertexRegions.eyes.length,
        nose: this.analysisResults.vertexRegions.nose.length,
        other: this.analysisResults.vertexRegions.other.length
      },
      vertexSamples: {
        mouth: this.analysisResults.vertexRegions.mouth.slice(0, 10),
        jaw: this.analysisResults.vertexRegions.jaw.slice(0, 10),
        eyes: this.analysisResults.vertexRegions.eyes.slice(0, 10)
      }
    }
    
    return report
  }

  /**
   * Export analysis results to JSON file
   */
  async exportReport(report, outputPath) {
    const json = JSON.stringify(report, null, 2)
    await writeFile(outputPath, json, 'utf-8')
    console.log(`\n💾 Report exported to: ${outputPath}`)
  }

  /**
   * Generate HTML visualization of vertex positions
   */
  generateVisualization(report) {
    const html = `
<!DOCTYPE html>
<html>
<head>
  <title>Vertex Analysis - face.glb</title>
  <style>
    body { font-family: monospace; padding: 20px; background: #1a1a1a; color: #00ff00; }
    h1, h2, h3 { color: #00ff00; }
    .section { margin: 20px 0; padding: 20px; background: #2a2a2a; border-radius: 8px; }
    .stat { margin: 10px 0; }
    .label { color: #ffff00; font-weight: bold; }
    .value { color: #00ffff; }
    canvas { border: 1px solid #00ff00; background: #000; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    pre { background: #000; padding: 10px; overflow-x: auto; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>🔍 Vertex Analysis Report - face.glb</h1>
  <p>Generated: ${report.timestamp}</p>
  
  <div class="section">
    <h2>📊 Summary</h2>
    <div class="stat"><span class="label">Total Meshes:</span> <span class="value">${report.summary.totalMeshes}</span></div>
    <div class="stat"><span class="label">Total Primitives:</span> <span class="value">${report.summary.totalPrimitives || 0}</span></div>
    <div class="stat"><span class="label">Total Vertices:</span> <span class="value">${report.summary.totalVertices}</span></div>
    <div class="stat"><span class="label">Total Morph Targets:</span> <span class="value">${report.summary.totalMorphTargets}</span></div>
    <div class="stat"><span class="label">Has Morph Targets:</span> <span class="value">${report.summary.hasMorphTargets ? '✅ Yes' : '❌ No'}</span></div>
  </div>
  
  <div class="section">
    <h2>📏 Bounding Box</h2>
    <pre>${JSON.stringify(report.boundingBox, null, 2)}</pre>
  </div>
  
  <div class="section">
    <h2>🎭 Morph Targets</h2>
    <pre>${JSON.stringify(report.morphTargets, null, 2)}</pre>
  </div>
  
  <div class="section">
    <h2>🎯 Vertex Distribution</h2>
    <canvas id="vertexChart" width="800" height="400"></canvas>
  </div>
  
  <div class="section">
    <h2>📍 Vertex Regions</h2>
    <div class="grid">
      ${Object.entries(report.vertexRegions).map(([region, count]) => `
        <div>
          <h3>${region.charAt(0).toUpperCase() + region.slice(1)}</h3>
          <div class="stat"><span class="label">Count:</span> <span class="value">${count}</span></div>
        </div>
      `).join('')}
    </div>
  </div>
  
  <div class="section">
    <h2>🔬 Sample Vertices</h2>
    <h3>Mouth Region (first 10)</h3>
    <pre>${JSON.stringify(report.vertexSamples.mouth, null, 2)}</pre>
    <h3>Jaw Region (first 10)</h3>
    <pre>${JSON.stringify(report.vertexSamples.jaw, null, 2)}</pre>
    <h3>Eyes Region (first 10)</h3>
    <pre>${JSON.stringify(report.vertexSamples.eyes, null, 2)}</pre>
  </div>
  
  <script>
    // Draw vertex distribution chart
    const canvas = document.getElementById('vertexChart');
    const ctx = canvas.getContext('2d');
    const data = ${JSON.stringify(report.vertexRegions)};
    
    const regions = Object.keys(data);
    const counts = Object.values(data);
    const maxCount = Math.max(...counts);
    
    const barWidth = 120;
    const barSpacing = 40;
    const chartHeight = 300;
    const chartTop = 50;
    
    regions.forEach((region, i) => {
      const x = 50 + i * (barWidth + barSpacing);
      const barHeight = (counts[i] / maxCount) * chartHeight;
      const y = chartTop + chartHeight - barHeight;
      
      // Draw bar
      ctx.fillStyle = '#00ff00';
      ctx.fillRect(x, y, barWidth, barHeight);
      
      // Draw label
      ctx.fillStyle = '#ffff00';
      ctx.font = '14px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(region, x + barWidth/2, chartTop + chartHeight + 20);
      
      // Draw count
      ctx.fillStyle = '#00ffff';
      ctx.fillText(counts[i], x + barWidth/2, y - 10);
    });
    
    // Draw title
    ctx.fillStyle = '#00ff00';
    ctx.font = 'bold 16px monospace';
    ctx.textAlign = 'left';
    ctx.fillText('Vertex Distribution by Region', 50, 30);
  </script>
</body>
</html>
    `.trim()
    
    return html
  }

  /**
   * Export HTML visualization
   */
  async exportVisualization(report, outputPath) {
    const html = this.generateVisualization(report)
    await writeFile(outputPath, html, 'utf-8')
    console.log(`📊 Visualization exported to: ${outputPath}`)
  }
}

// Main execution
async function main() {
  console.log('🚀 Starting Vertex Analyzer for face.glb\n')
  
  const analyzer = new VertexAnalyzer()
  const modelPath = join(__dirname, '../assets/models/face.glb')
  
  try {
    // Analyze model
    const report = await analyzer.analyze(modelPath)
    
    // Export JSON report
    const jsonPath = join(__dirname, '../reports/vertex-analysis.json')
    await mkdir(join(__dirname, '../reports'), { recursive: true })
    await analyzer.exportReport(report, jsonPath)
    
    // Export HTML visualization
    const htmlPath = join(__dirname, '../reports/vertex-analysis.html')
    await analyzer.exportVisualization(report, htmlPath)
    
    console.log('\n✅ Analysis complete!')
    console.log(`\n📄 View reports:`)
    console.log(`   JSON: ${jsonPath}`)
    console.log(`   HTML: ${htmlPath}`)
    
  } catch (error) {
    console.error('\n❌ Analysis failed:', error.message)
    console.error(error.stack)
    process.exit(1)
  }
}

main()
