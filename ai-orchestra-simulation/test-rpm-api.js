#!/usr/bin/env node

/**
 * Ready Player Me API Explorer
 * Tests API capabilities with write access
 */

const API_KEY = 'sk_live_-E0zM-esf3a69p1mi1W3JVcNgGU9lTQCKjs0';
const SUBDOMAIN = 'talent-ai.readyplayer.me';
const API_BASE = 'https://api.readyplayer.me';

// Color output helpers
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

async function testEndpoint(name, url, options = {}) {
  log(colors.cyan, `\n🔍 Testing: ${name}`);
  log(colors.yellow, `   URL: ${url}`);
  
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
      console.log('   Response:', JSON.stringify(data, null, 2).substring(0, 500));
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
  log(colors.bright, '\n🚀 Ready Player Me API Explorer\n');
  log(colors.bright, '================================\n');
  
  const results = {};

  // 1. Create Anonymous User
  results.user = await testEndpoint(
    'Create Anonymous User',
    `${API_BASE}/v1/users`,
    {
      method: 'POST',
      body: JSON.stringify({
        data: {
          appName: 'talent-ai'
        }
      })
    }
  );

  let userId = null;
  if (results.user.success && results.user.data.data) {
    userId = results.user.data.data.id;
    log(colors.green, `   📝 User ID: ${userId}`);
  }

  // 2. Get Templates
  results.templates = await testEndpoint(
    'Get Avatar Templates',
    `${API_BASE}/v2/avatars/templates`
  );

  let templateId = null;
  if (results.templates.success && results.templates.data.data && results.templates.data.data.length > 0) {
    // Find a template with good morph targets
    const template = results.templates.data.data.find(t => 
      t.bodyType === 'halfbody' || t.bodyType === 'fullbody'
    ) || results.templates.data.data[0];
    
    templateId = template.id;
    log(colors.green, `   📋 Selected Template: ${template.id} (${template.bodyType})`);
    log(colors.yellow, `   Available templates: ${results.templates.data.data.length}`);
  }

  // 3. Create Avatar from Template (if we have both user and template)
  if (userId && templateId) {
    results.createAvatar = await testEndpoint(
      'Create Avatar from Template',
      `${API_BASE}/v2/avatars/templates/${templateId}`,
      {
        method: 'POST',
        body: JSON.stringify({
          data: {
            partner: 'talent-ai',
            bodyType: 'halfbody',
            userId: userId
          }
        })
      }
    );

    let avatarId = null;
    if (results.createAvatar.success && results.createAvatar.data.data) {
      avatarId = results.createAvatar.data.data.id;
      log(colors.green, `   🎭 Created Avatar ID: ${avatarId}`);
      log(colors.green, `   🔗 Preview URL: ${API_BASE}/v2/avatars/${avatarId}.glb?preview=true`);
      log(colors.green, `   🔗 Model URL: https://models.readyplayer.me/${avatarId}.glb`);

      // 4. Get Avatar Metadata
      results.metadata = await testEndpoint(
        'Get Avatar Metadata',
        `${API_BASE}/v1/avatars/${avatarId}.json`
      );

      if (results.metadata.success) {
        const meta = results.metadata.data;
        log(colors.cyan, '\n📊 Avatar Details:');
        log(colors.yellow, `   Body Type: ${meta.bodyType || 'unknown'}`);
        log(colors.yellow, `   Outfit Gender: ${meta.outfitGender || 'unknown'}`);
        
        if (meta.properties && meta.properties.morphTargets) {
          log(colors.green, `   ✅ Morph Targets: ${meta.properties.morphTargets}`);
        } else {
          log(colors.red, `   ⚠️  No morph target info in metadata`);
        }
      }

      // 5. Save Avatar (make it permanent)
      results.saveAvatar = await testEndpoint(
        'Save Avatar Permanently',
        `${API_BASE}/v2/avatars/${avatarId}`,
        {
          method: 'PUT'
        }
      );

      if (results.saveAvatar.success) {
        log(colors.green, `   💾 Avatar saved permanently!`);
        log(colors.bright, `\n🎉 FINAL AVATAR URL: https://models.readyplayer.me/${avatarId}.glb`);
      }
    }
  }

  // 6. Test different body types capability
  if (userId && templateId) {
    log(colors.cyan, '\n🔬 Testing Body Type Options...');
    
    for (const bodyType of ['halfbody', 'fullbody']) {
      const result = await testEndpoint(
        `Create ${bodyType} Avatar`,
        `${API_BASE}/v2/avatars/templates/${templateId}`,
        {
          method: 'POST',
          body: JSON.stringify({
            data: {
              partner: 'talent-ai',
              bodyType: bodyType,
              userId: userId
            }
          })
        }
      );

      if (result.success && result.data.data) {
        const id = result.data.data.id;
        log(colors.green, `   ✅ ${bodyType}: ${id}`);
        log(colors.yellow, `      URL: https://models.readyplayer.me/${id}.glb`);
      }
    }
  }

  // Summary
  log(colors.bright, '\n\n📋 Summary');
  log(colors.bright, '===========\n');
  
  console.log('API Capabilities:');
  console.log('  ✅ Create Anonymous Users:', results.user?.success ? 'YES' : 'NO');
  console.log('  ✅ Get Templates:', results.templates?.success ? 'YES' : 'NO');
  console.log('  ✅ Create Avatars:', results.createAvatar?.success ? 'YES' : 'NO');
  console.log('  ✅ Save Avatars:', results.saveAvatar?.success ? 'YES' : 'NO');
  console.log('  ✅ Get Metadata:', results.metadata?.success ? 'YES' : 'NO');

  if (results.templates?.success && results.templates.data.data) {
    log(colors.cyan, `\n📚 Available Templates: ${results.templates.data.data.length}`);
    results.templates.data.data.slice(0, 5).forEach((template, i) => {
      console.log(`   ${i + 1}. ${template.id} (${template.bodyType || 'unknown type'})`);
    });
    if (results.templates.data.data.length > 5) {
      console.log(`   ... and ${results.templates.data.data.length - 5} more`);
    }
  }

  log(colors.bright, '\n💡 Next Steps:');
  console.log('  1. Use created avatar IDs in your application');
  console.log('  2. Load GLB models to check morph targets');
  console.log('  3. Create multiple avatars with different templates');
  console.log('  4. Test Oculus viseme support in created avatars\n');
}

main().catch(error => {
  log(colors.red, '\n❌ Fatal error:', error.message);
  process.exit(1);
});
