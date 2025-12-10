// App State
let currentScreen = 'welcome';
let currentRole = '';
let currentModel = '';
let conversationHistory = [];
let questionCount = 0;

// DOM Elements
const welcomeScreen = document.getElementById('welcome-screen');
const interviewScreen = document.getElementById('interview-screen');
const resultsScreen = document.getElementById('results-screen');
const ollamaStatus = document.getElementById('ollama-status');
const modelSelect = document.getElementById('model-select');
const conversation = document.getElementById('conversation');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const endInterviewBtn = document.getElementById('end-interview-btn');
const newInterviewBtn = document.getElementById('new-interview-btn');
const interviewRole = document.getElementById('interview-role');
const conversationSummary = document.getElementById('conversation-summary');

// Initialize App
async function init() {
  await checkOllamaStatus();
  await loadModels();
  setupEventListeners();
}

// Check Ollama Status
async function checkOllamaStatus() {
  try {
    const result = await window.ollama.checkStatus();
    if (result.success && result.isRunning) {
      ollamaStatus.textContent = '🟢 Ollama Online';
      ollamaStatus.classList.add('online');
      ollamaStatus.classList.remove('offline');
    } else {
      throw new Error('Ollama is not running');
    }
  } catch (error) {
    ollamaStatus.textContent = '🔴 Ollama Offline';
    ollamaStatus.classList.add('offline');
    ollamaStatus.classList.remove('online');
    console.error('Ollama status check failed:', error);
  }
}

// Load Available Models
async function loadModels() {
  try {
    const result = await window.ollama.listModels();
    if (result.success && result.models.length > 0) {
      modelSelect.innerHTML = '';
      result.models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.name;
        option.textContent = model.name;
        modelSelect.appendChild(option);
      });
      currentModel = result.models[0].name;
    } else {
      modelSelect.innerHTML = '<option value="">No models found. Please install a model.</option>';
    }
  } catch (error) {
    console.error('Failed to load models:', error);
    modelSelect.innerHTML = '<option value="">Error loading models</option>';
  }
}

// Setup Event Listeners
function setupEventListeners() {
  // Role selection buttons
  document.querySelectorAll('.role-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const role = btn.dataset.role;
      startInterview(role);
    });
  });

  // Model selection
  modelSelect.addEventListener('change', (e) => {
    currentModel = e.target.value;
  });

  // Send message
  sendBtn.addEventListener('click', sendMessage);
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // End interview
  endInterviewBtn.addEventListener('click', endInterview);

  // New interview
  newInterviewBtn.addEventListener('click', () => {
    showScreen('welcome');
    resetInterview();
  });
}

// Start Interview
async function startInterview(role) {
  currentRole = role;
  conversationHistory = [];
  questionCount = 0;
  
  showScreen('interview');
  interviewRole.textContent = `${role} Interview`;
  conversation.innerHTML = '<div class="message loading">🤖 Interviewer is preparing the first question...</div>';

  try {
    const result = await window.ollama.startInterview(role, currentModel);
    if (result.success) {
      conversation.innerHTML = '';
      addMessage('interviewer', result.response);
      conversationHistory.push({ role: 'assistant', content: result.response });
      questionCount++;
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    conversation.innerHTML = `<div class="message error">❌ Failed to start interview: ${error.message}</div>`;
    console.error('Failed to start interview:', error);
  }
}

// Send Message
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  // Add user message to conversation
  addMessage('candidate', message);
  conversationHistory.push({ role: 'user', content: message });
  userInput.value = '';

  // Show loading indicator
  const loadingMsg = document.createElement('div');
  loadingMsg.className = 'message loading';
  loadingMsg.textContent = '🤖 Interviewer is thinking...';
  conversation.appendChild(loadingMsg);
  conversation.scrollTop = conversation.scrollHeight;

  try {
    const result = await window.ollama.sendMessage(message, currentModel, conversationHistory);
    
    // Remove loading indicator
    loadingMsg.remove();

    if (result.success) {
      addMessage('interviewer', result.response);
      conversationHistory.push({ role: 'assistant', content: result.response });
      questionCount++;

      // Check if interview should end (after 5-6 questions)
      if (questionCount >= 6) {
        setTimeout(() => {
          endInterview();
        }, 2000);
      }
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    loadingMsg.remove();
    addMessage('system', `❌ Error: ${error.message}`);
    console.error('Failed to send message:', error);
  }
}

// Add Message to Conversation
function addMessage(sender, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}`;
  
  const headerDiv = document.createElement('div');
  headerDiv.className = 'message-header';
  
  if (sender === 'interviewer') {
    headerDiv.innerHTML = '🤖 Interviewer';
  } else if (sender === 'candidate') {
    headerDiv.innerHTML = '👤 You';
  } else {
    headerDiv.innerHTML = '⚙️ System';
  }
  
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  contentDiv.textContent = content;
  
  messageDiv.appendChild(headerDiv);
  messageDiv.appendChild(contentDiv);
  conversation.appendChild(messageDiv);
  conversation.scrollTop = conversation.scrollHeight;
}

// End Interview
function endInterview() {
  // Show conversation summary
  conversationSummary.innerHTML = '';
  conversationHistory.forEach((msg, index) => {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message';
    msgDiv.innerHTML = `
      <div class="message-header">${msg.role === 'assistant' ? '🤖 Interviewer' : '👤 You'}</div>
      <div class="message-content">${msg.content}</div>
    `;
    conversationSummary.appendChild(msgDiv);
  });

  showScreen('results');
}

// Reset Interview
function resetInterview() {
  currentRole = '';
  conversationHistory = [];
  questionCount = 0;
  conversation.innerHTML = '';
  userInput.value = '';
}

// Show Screen
function showScreen(screen) {
  welcomeScreen.classList.remove('active');
  interviewScreen.classList.remove('active');
  resultsScreen.classList.remove('active');

  if (screen === 'welcome') {
    welcomeScreen.classList.add('active');
  } else if (screen === 'interview') {
    interviewScreen.classList.add('active');
  } else if (screen === 'results') {
    resultsScreen.classList.add('active');
  }

  currentScreen = screen;
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
