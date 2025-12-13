import React, { useState, useEffect } from 'react';
import InterviewService, { InterviewSession } from '../services/interview-service';
import { useInterview } from './hooks/useInterview';
import { useConfig } from './hooks/useConfig';
import { useEventBus } from './hooks/useEventBus';
import { AVAILABLE_MODELS, DEFAULT_MODEL, getTrainedModels } from '../services/model-config';
import './InterviewApp.css';
import StatusBar from './ui/StatusBar';
import { fetchIntegrationHealth } from '../services/integration-service-client';

const useService = () => useInterview();

type Screen = 'setup' | 'interview' | 'summary';

const InterviewApp: React.FC = () => {
  const service = useService();
  const config = useConfig();
  const eventBus = useEventBus();
  const [screen, setScreen] = useState<Screen>('setup');
  const [role, setRole] = useState(() => config.get('interview').defaultRole || 'Software Engineer');
  const [selectedModel, setSelectedModel] = useState(() => config.get('ai').ollama.defaultModel || DEFAULT_MODEL);
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ollamaStatus, setOllamaStatus] = useState<boolean>(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [integrationStatus, setIntegrationStatus] = useState<'online' | 'offline' | 'degraded'>('offline');
  const [serviceStatuses, setServiceStatuses] = useState<any[]>([]);
  const [serviceMode, setServiceMode] = useState<'integration' | 'ollama'>('integration');

  // Check Ollama status on mount
  useEffect(() => {
    checkServiceStatus();
  }, []);

  const checkServiceStatus = async () => {
    // Check overall service status
    const status = await service.checkStatus();
    setOllamaStatus(status);

    // Check integration health
    const health = await fetchIntegrationHealth();
    if (health) {
      setIntegrationStatus(health.status);
      setServiceStatuses(health.services);
    }

    // Get service mode
    if ((service as any).getMode) {
      const mode = (service as any).getMode();
      setServiceMode(mode);
    }

    // List models
    if (status) {
      const models = await service.listModels();
      setAvailableModels(models.map((m: any) => m.name || m.id));
    }
  };

  const startInterview = async () => {
    setLoading(true);
    setError(null);

    try {
      const newSession = await service.startInterview(
        role,
        selectedModel,
        5
      );
      setSession(newSession);
      setScreen('interview');
      // fire event for analytics/telemetry hooks
      eventBus.emit('interview:started', { role, model: selectedModel });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const sendResponse = async () => {
    if (!session || !userInput.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const updatedSession = await service.sendResponse(session, userInput);
      setSession(updatedSession);
      setUserInput('');

      // Check if interview is complete
      if (updatedSession.isComplete) {
        setScreen('summary');
        eventBus.emit('interview:completed', { totalQuestions: updatedSession.config.totalQuestions });
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const restartInterview = () => {
    setSession(null);
    setUserInput('');
    setError(null);
    setScreen('setup');
  };

  const getCurrentQuestion = () => {
    if (!session) return '';
    // Get the last assistant message
    const assistantMessages = session.messages.filter(
      (m) => m.role === 'assistant'
    );
    return assistantMessages[assistantMessages.length - 1]?.content || '';
  };

  const getConversationHistory = () => {
    if (!session) return [];
    // Filter out system messages and the initial "start interview" message
    return session.messages.filter(
      (m) =>
        m.role !== 'system' &&
        !(m.role === 'user' && m.content === 'Please start the interview.')
    );
  };

  // Setup Screen
  if (screen === 'setup') {
    return (
      <div className="interview-app">
        <div className="setup-screen">
          <StatusBar services={serviceStatuses} integrationStatus={integrationStatus} />
          <div className="header">
            <h1>OpenTalent</h1>
            <p className="tagline">Privacy-First AI Interviews</p>
          </div>

          <div className="status-indicator">
            <div className={`status-dot ${ollamaStatus ? 'online' : 'offline'}`} />
            <span>
              Service: {ollamaStatus ? 'Online' : 'Offline'} 
              {serviceMode && <span className="service-mode"> ({serviceMode === 'integration' ? '🔥 Gateway' : '🦙 Direct Ollama'})</span>}
            </span>
          </div>

          {!ollamaStatus && (
            <div className="error-message">
              ⚠️ Service is not available. Please ensure the integration service or Ollama is running.
              <br />
              <small>Integration Service: http://localhost:8009 | Ollama: http://localhost:11434</small>
            </div>
          )}

          {ollamaStatus && (
            <>
              <div className="model-info">
                <p>Available Models: {availableModels.join(', ') || 'None'}</p>
                <p className="model-using">Using: {selectedModel || DEFAULT_MODEL}</p>
              </div>

              <div className="role-selection">
                <h2>Select Interview Role</h2>
                <div className="role-buttons">
                  <button
                    className={`role-btn ${
                      role === 'Software Engineer' ? 'active' : ''
                    }`}
                    onClick={() => setRole('Software Engineer')}
                  >
                    Software Engineer
                  </button>
                  <button
                    className={`role-btn ${
                      role === 'Product Manager' ? 'active' : ''
                    }`}
                    onClick={() => setRole('Product Manager')}
                  >
                    Product Manager
                  </button>
                  <button
                    className={`role-btn ${
                      role === 'Data Analyst' ? 'active' : ''
                    }`}
                    onClick={() => setRole('Data Analyst')}
                  >
                    Data Analyst
                  </button>
                </div>
              </div>

              <div className="model-selection">
                <h2>Select AI Model</h2>
                <p className="model-subtitle">Choose from your trained models</p>
                <div className="model-options">
                  {getTrainedModels().map((model) => (
                    <div
                      key={model.id}
                      className={`model-option ${selectedModel === model.id ? 'selected' : ''}`}
                      onClick={() => setSelectedModel(model.id)}
                    >
                      <div className="model-name">{model.name}</div>
                      <div className="model-details">
                        {model.paramCount} • {model.ramRequired} RAM • {model.downloadSize}
                      </div>
                      <div className="model-description">{model.description}</div>
                      {model.dataset && (
                        <div className="model-dataset">
                          📊 Dataset: {model.dataset}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <button
                className="start-btn"
                onClick={startInterview}
                disabled={loading}
              >
                {loading ? 'Starting Interview...' : 'Start Interview'}
              </button>

              {error && <div className="error-message">{error}</div>}
            </>
          )}

          <div className="privacy-badge">
            <span className="lock-icon">🔒</span>
            <span>100% Local Processing • No Cloud • Complete Privacy</span>
          </div>
        </div>
      </div>
    );
  }

  // Interview Screen
  if (screen === 'interview' && session) {
    const history = getConversationHistory();
    const currentQuestion = getCurrentQuestion();

    return (
      <div className="interview-app">
        <div className="interview-screen">
          <StatusBar services={serviceStatuses} integrationStatus={integrationStatus} />
          <div className="header">
            <h1>OpenTalent Interview</h1>
            <p className="role-display">{session.config.role}</p>
          </div>

          <div className="progress-bar">
            <span>
              Question {session.currentQuestion} of{' '}
              {session.config.totalQuestions}
            </span>
          </div>

          <div className="conversation-container">
            {history.map((message, index) => (
              <div
                key={index}
                className={`message ${message.role === 'user' ? 'user' : 'assistant'}`}
              >
                <div className="message-label">
                  {message.role === 'user' ? 'You' : 'Interviewer'}
                </div>
                <div className="message-content">{message.content}</div>
              </div>
            ))}
          </div>

          <div className="input-section">
            <textarea
              className="response-input"
              placeholder="Type your response here..."
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendResponse();
                }
              }}
              disabled={loading}
              rows={4}
            />
            <button
              className="send-btn"
              onClick={sendResponse}
              disabled={loading || !userInput.trim()}
            >
              {loading ? 'Sending...' : 'Send Response'}
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button className="end-btn" onClick={() => setScreen('summary')}>
            End Interview
          </button>
        </div>
      </div>
    );
  }

  // Summary Screen
  if (screen === 'summary' && session) {
    const summary = service.getInterviewSummary(session);

    return (
      <div className="interview-app">
        <div className="summary-screen">
          <StatusBar services={serviceStatuses} integrationStatus={integrationStatus} />
          <div className="header">
            <h1>Interview Complete!</h1>
          </div>

          <div className="summary-content">
            <pre>{summary}</pre>
          </div>

          <div className="conversation-history">
            <h2>Conversation History</h2>
            {getConversationHistory().map((message, index) => (
              <div key={index} className="history-item">
                <div className="history-label">
                  {message.role === 'user' ? 'You:' : 'Interviewer:'}
                </div>
                <div className="history-text">{message.content}</div>
              </div>
            ))}
          </div>

          <button className="restart-btn" onClick={restartInterview}>
            Start New Interview
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default InterviewApp;
