/**
 * Quick validation script for metaHumanHead.glb
 * Run in Node.js environment (requires three.js in Node.js)
 * 
 * Note: This is a simplified check. For full validation, use test-metahuman-model.html in browser
 */

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const MODEL_PATH = resolve(__dirname, '../assets/models/metaHumanHead.glb');

console.log('\n🔍 Quick Validation: metaHumanHead.glb\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// Check file exists
try {
    const stats = readFileSync(MODEL_PATH);
    const fileSizeMB = (stats.length / (1024 * 1024)).toFixed(2);
    console.log(`✅ File exists: metaHumanHead.glb`);
    console.log(`   Size: ${fileSizeMB} MB\n`);
} catch (error) {
    console.error(`❌ File not found: ${MODEL_PATH}`);
    console.error(`   Error: ${error.message}\n`);
    process.exit(1);
}

// Check file format (GLB magic number)
try {
    const buffer = readFileSync(MODEL_PATH);
    const magic = buffer.toString('ascii', 0, 4);
    
    if (magic === 'glTF') {
        console.log('✅ Format: GLB (Binary GLTF)');
    } else {
        console.log(`⚠️  Format: Unknown (magic: ${magic})`);
    }
} catch (error) {
    console.error(`❌ Error reading file: ${error.message}`);
}

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
console.log('📝 Note: Full validation requires browser environment');
console.log('   Use: tests/test-metahuman-model.html\n');
console.log('   Or: Open http://localhost:9000/tests/test-metahuman-model.html\n');

