/**
 * App Router Component
 * Main navigation controller for OpenTalent Desktop App
 * Handles switching between Setup, Interview, and Demo screens
 */

import React, { useState, useEffect } from 'react';
import App from './App';
import InterviewApp from './InterviewApp';
import { RecruiterApp } from './RecruiterApp';
import DemoScreen from './screens/DemoScreen';

type AppScreen = 'setup' | 'interview' | 'recruiter' | 'demo';

interface Config {
  selectedModel?: string;
  hardware?: any;
}

const AppRouter: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('setup');
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkConfig = async () => {
      try {
        const cfg = await window.electronAPI.loadConfig();
        if (cfg?.selectedModel && cfg?.hardware) {
          // Config exists, skip setup
          setConfig(cfg);
          setCurrentScreen('recruiter'); // Redirect to RecruiterApp by default
        }
      } catch (error) {
        console.error('Error loading config:', error);
      } finally {
        setLoading(false);
      }
    };

    checkConfig();
  }, []);

  const handleSetupComplete = (newConfig: Config) => {
    setConfig(newConfig);
    setCurrentScreen('recruiter');
  };

  const handleSwitchToDemo = () => {
    setCurrentScreen('demo');
  };

  const handleExitDemo = () => {
    setCurrentScreen('recruiter');
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading OpenTalent...</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Navigation Sidebar */}
      <nav style={{
        width: '240px',
        backgroundColor: '#111827',
        color: 'white',
        padding: '24px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        flexShrink: 0
      }}>
        <div style={{ padding: '0 8px 24px 8px', borderBottom: '1px solid #374151', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '700', margin: 0 }}>OpenTalent</h2>
        </div>

        <button
          onClick={() => setCurrentScreen('recruiter')}
          style={{
            padding: '12px 16px',
            borderRadius: '8px',
            backgroundColor: currentScreen === 'recruiter' ? '#3b82f6' : 'transparent',
            color: 'white',
            border: 'none',
            textAlign: 'left',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          🎯 Recruiter (New)
        </button>

        <button
          onClick={() => setCurrentScreen('interview')}
          style={{
            padding: '12px 16px',
            borderRadius: '8px',
            backgroundColor: currentScreen === 'interview' ? '#3b82f6' : 'transparent',
            color: 'white',
            border: 'none',
            textAlign: 'left',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          🎙️ AI Interview
        </button>

        <button
          onClick={() => setCurrentScreen('demo')}
          style={{
            padding: '12px 16px',
            borderRadius: '8px',
            backgroundColor: currentScreen === 'demo' ? '#3b82f6' : 'transparent',
            color: 'white',
            border: 'none',
            textAlign: 'left',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          🎬 Demo View
        </button>

        <div style={{ marginTop: 'auto', padding: '16px 8px', fontSize: '12px', color: '#9ca3af' }}>
          v1.1.0
        </div>
      </nav>

      {/* Main Content Area */}
      <div style={{ flex: 1, overflowY: 'auto', backgroundColor: '#f9fafb' }}>
        {currentScreen === 'setup' && (
          <App onComplete={handleSetupComplete} />
        )}

        {currentScreen === 'interview' && (
          <InterviewApp
            onSwitchToDemo={handleSwitchToDemo}
            config={config}
          />
        )}

        {currentScreen === 'recruiter' && (
          <RecruiterApp />
        )}

        {currentScreen === 'demo' && (
          <DemoScreen onExit={handleExitDemo} />
        )}
      </div>
    </div>
  );
};

export default AppRouter;
