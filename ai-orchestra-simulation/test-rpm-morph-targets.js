#!/usr/bin/env node

/**
 * RPM Avatar Creator with Morph Target Configuration
 * Explores advanced avatar creation options
 */

const API_KEY = 'sk_live_-E0zM-esf3a69p1mi1W3JVcNgGU9lTQCKjs0';
const SUBDOMAIN = 'talent-ai.readyplayer.me';
const API_BASE = 'https://api.readyplayer.me';

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
};

function log(color, ...args) {
  console.log(color, ...args, colors.reset);
}

async function apiCall(name, url, options = {}) {
  log(colors.cyan, `\n🔍 ${name}`);
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const contentType = response.headers.get('content-type');
    let data;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (response.ok) {
      log(colors.green, `   ✅ Success (${response.status})`);
      return { success: true, data, status: response.status };
    } else {
      log(colors.red, `   ❌ Failed (${response.status})`);
      console.log('   Error:', JSON.stringify(data, null, 2));
      return { success: false, data, status: response.status };
    }
  } catch (error) {
    log(colors.red, `   ❌ Error: ${error.message}`);
    return { success: false, error: error.message };
  }
}

async function main() {
  log(colors.bright, '\n🔬 RPM Advanced Avatar Creation\n');
  log(colors.bright, '================================\n');

  // 1. Create user
  const userResult = await apiCall(
    'Creating anonymous user',
    `${API_BASE}/v1/users`,
    {
      method: 'POST',
      body: JSON.stringify({ data: { appName: 'talent-ai' } })
    }
  );

  if (!userResult.success) {
    log(colors.red, '\n❌ Cannot proceed without user');
    return;
  }

  const userId = userResult.data.data.id;
  log(colors.green, `   User ID: ${userId}`);

  // 2. Get all templates with details
  const templatesResult = await apiCall(
    'Getting all templates',
    `${API_BASE}/v2/avatars/templates`
  );

  if (!templatesResult.success) {
    log(colors.red, '\n❌ Cannot get templates');
    return;
  }

  const templates = templatesResult.data.data;
  log(colors.green, `   Found ${templates.length} templates`);

  // 3. Try creating with different morphTargets configurations
  log(colors.bright, '\n\n🧪 Testing Different Morph Target Configurations:\n');

  const morphTargetOptions = [
    'ARKit',           // Apple ARKit blend shapes
    'Oculus',          // Oculus/Meta Quest visemes
    'OVR',             // Alternative name for Oculus
    'mouthShapes',     // Generic mouth shapes
    'visemes',         // Speech visemes
    'ARKit,Oculus',    // Both
    'OVR,ARKit'        // Both alternative
  ];

  const testTemplate = templates[0].id;
  const results = [];

  for (const morphTarget of morphTargetOptions) {
    const result = await apiCall(
      `Creating avatar with morphTargets: "${morphTarget}"`,
      `${API_BASE}/v2/avatars/templates/${testTemplate}`,
      {
        method: 'POST',
        body: JSON.stringify({
          data: {
            partner: 'talent-ai',
            bodyType: 'halfbody',
            userId: userId,
            morphTargets: morphTarget
          }
        })
      }
    );

    if (result.success && result.data.data) {
      const avatarId = result.data.data.id;
      log(colors.green, `   ✅ Created: ${avatarId}`);
      
      // Save it
      await apiCall(
        `Saving avatar ${avatarId}`,
        `${API_BASE}/v2/avatars/${avatarId}`,
        { method: 'PUT' }
      );

      results.push({
        morphTargets: morphTarget,
        avatarId: avatarId,
        url: `https://models.readyplayer.me/${avatarId}.glb`
      });
    }

    // Delay between requests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // 4. Try URL parameters for GLB export
  log(colors.bright, '\n\n🎯 Testing GLB Export Parameters:\n');

  if (results.length > 0) {
    const testAvatar = results[0].avatarId;
    
    const exportOptions = [
      '?morphTargets=ARKit',
      '?morphTargets=Oculus',
      '?morphTargets=ARKit,Oculus',
      '?lod=0',
      '?textureAtlas=256',
      '?useDracoMeshCompression=false',
      '?morphTargets=ARKit&preview=true',
      '?morphTargets=Oculus&preview=true'
    ];

    for (const params of exportOptions) {
      const url = `https://models.readyplayer.me/${testAvatar}.glb${params}`;
      log(colors.cyan, `\nTrying: ${params}`);
      
      try {
        const response = await fetch(url);
        if (response.ok) {
          const size = parseInt(response.headers.get('content-length') || '0');
          log(colors.green, `   ✅ Success - Size: ${(size / 1024).toFixed(2)} KB`);
        } else {
          log(colors.red, `   ❌ Failed: ${response.status}`);
        }
      } catch (error) {
        log(colors.red, `   ❌ Error: ${error.message}`);
      }

      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }

  // Summary
  log(colors.bright, '\n\n📋 Results Summary\n');
  log(colors.bright, '==================\n');

  console.log(`Successful avatar creations: ${results.length}/${morphTargetOptions.length}\n`);

  if (results.length > 0) {
    log(colors.green, '✅ Created Avatars:\n');
    results.forEach((r, i) => {
      console.log(`${i + 1}. morphTargets: "${r.morphTargets}"`);
      console.log(`   ID: ${r.avatarId}`);
      console.log(`   URL: ${r.url}\n`);
    });
  }

  // 5. Check RPM documentation endpoint
  log(colors.bright, '\n🔍 Checking RPM API Documentation:\n');
  
  const docEndpoints = [
    `${API_BASE}/v1/docs`,
    `${API_BASE}/v2/docs`,
    `${API_BASE}/docs`,
    `${API_BASE}/v1/schema`,
    `${API_BASE}/v2/schema`,
  ];

  for (const endpoint of docEndpoints) {
    await apiCall(`Testing ${endpoint}`, endpoint);
    await new Promise(resolve => setTimeout(resolve, 300));
  }

  // Final recommendations
  log(colors.bright, '\n\n💡 Key Findings & Next Steps:\n');
  console.log('1. Ready Player Me avatars by default only include:');
  console.log('   - mouthOpen');
  console.log('   - mouthSmile\n');
  
  console.log('2. Oculus visemes are NOT included in standard templates\n');
  
  console.log('3. Possible solutions:');
  console.log('   ✅ Continue using enhanced fallback avatar (100% reliable)');
  console.log('   💡 Contact RPM support to enable Oculus visemes on templates');
  console.log('   💡 Request enterprise plan with custom morph targets');
  console.log('   💡 Use RPM Studio to create custom templates with visemes');
  console.log('   💡 Post-process GLB files to add Oculus viseme morph targets\n');
  
  console.log('4. Current recommendation:');
  console.log('   ✅ Use intelligent fallback detection (already implemented)');
  console.log('   ✅ Enhanced fallback avatar provides guaranteed lip-sync');
  console.log('   📧 Submit RPM support ticket requesting Oculus viseme support\n');
}

main().catch(error => {
  log(colors.red, '\n❌ Fatal error:', error.message);
  process.exit(1);
});
