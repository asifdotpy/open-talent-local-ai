// OpenTalent Recruiter - App State
let agentHealth = {};
let currentPipeline = null;

// DOM Elements
const agentStatus = document.getElementById('agent-status');

// Initialize App
async function init() {
  console.log('OpenTalent Recruiter initializing...');
  await checkAgentHealth();
  setupEventListeners();

  // Poll agent health every 10 seconds
  setInterval(checkAgentHealth, 10000);
}

// Check Agent Health Status
async function checkAgentHealth() {
  try {
    // TODO: Replace with actual scout-coordinator-agent health check
    // const response = await fetch('http://localhost:8095/agents/health');
    // const data = await response.json();

    // Placeholder - simulate healthy agents
    agentHealth = {
      'scout-coordinator': 'healthy',
      'data-enrichment': 'healthy',
      'quality-focused': 'healthy',
      'proactive-scanning': 'healthy'
    };

    const healthyCount = Object.values(agentHealth).filter(h => h === 'healthy').length;
    const totalCount = Object.keys(agentHealth).length;

    if (healthyCount === totalCount) {
      agentStatus.textContent = `🟢 ${healthyCount}/${totalCount} Agents Online`;
      agentStatus.classList.add('online');
      agentStatus.classList.remove('offline');
    } else {
      agentStatus.textContent = `⚠️ ${healthyCount}/${totalCount} Agents Online`;
      agentStatus.classList.add('warning');
    }
  } catch (error) {
    console.error('Agent health check failed:', error);
    agentStatus.textContent = '🔴 Agents Offline';
    agentStatus.classList.add('offline');
    agentStatus.classList.remove('online', 'warning');
  }
}

// Setup Event Listeners
function setupEventListeners() {
  console.log('Event listeners ready');
  // TODO: Add event listeners for search button, filters, etc.
}

// Placeholder function for future candidate search
async function searchCandidates(prompt, tools) {
  console.log('Search candidates:', { prompt, tools });
  // TODO: Implement scout-coordinator-agent API call
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

console.log('OpenTalent Recruiter loaded');
