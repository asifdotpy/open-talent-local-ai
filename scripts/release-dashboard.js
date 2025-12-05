// scripts/release-dashboard.js
const { Octokit } = require('@octokit/rest');

class ReleaseDashboard {
  constructor() {
    this.octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
    this.submodules = ['agents', 'microservices', 'frontend', 'infrastructure'];
  }

  async getReleaseStatus() {
    const status = {};

    for (const submodule of this.submodules) {
      try {
        const releases = await this.octokit.repos.listReleases({
          owner: 'asifdotpy',
          repo: `talent-ai-${submodule}`
        });

        status[submodule] = {
          latest: releases.data[0]?.tag_name || 'none',
          published: releases.data[0]?.published_at || null,
          prerelease: releases.data[0]?.prerelease || false
        };
      } catch (error) {
        status[submodule] = { error: error.message };
      }
    }

    return status;
  }

  async createReleaseNotes(version) {
    // Generate comprehensive release notes
    // Include changes from all submodules
    // Format for stakeholder consumption
  }
}

// CLI interface
if (require.main === module) {
  const dashboard = new ReleaseDashboard();

  dashboard.getReleaseStatus().then(status => {
    console.log('Release Status Dashboard:');
    console.log('========================');
    Object.entries(status).forEach(([submodule, info]) => {
      console.log(`${submodule}: ${info.latest} (${info.published || 'unpublished'})`);
    });
  }).catch(console.error);
}

module.exports = ReleaseDashboard;