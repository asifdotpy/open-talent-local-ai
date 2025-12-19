/**
 * App Router Component
 * Main navigation controller for OpenTalent Desktop App
 * Handles switching between Setup, Interview, and Demo screens
 */

import React, { useState, useEffect } from 'react';
import App from './App';
import InterviewApp from './InterviewApp';
import DemoScreen from './screens/DemoScreen';

type AppScreen = 'setup' | 'interview' | 'demo';

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
          setCurrentScreen('interview');
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
    setCurrentScreen('interview');
  };

  const handleSwitchToDemo = () => {
    setCurrentScreen('demo');
  };

  const handleExitDemo = () => {
    setCurrentScreen('interview');
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading OpenTalent...</div>
      </div>
    );
  }

  return (
    <>
      {currentScreen === 'setup' && (
        <App onComplete={handleSetupComplete} />
      )}

      {currentScreen === 'interview' && (
        <InterviewApp
          onSwitchToDemo={handleSwitchToDemo}
          config={config}
        />
      )}

      {currentScreen === 'demo' && (
        <DemoScreen onExit={handleExitDemo} />
      )}
    </>
  );
};

export default AppRouter;