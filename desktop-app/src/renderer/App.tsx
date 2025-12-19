import React, { useState, useEffect } from 'react';
import '../index.css';

interface HardwareInfo {
  ramGb: number;
  ramAvailable: number;
  cpuCores: number;
  cpuModel: string;
  platform: string;
}

interface ModelRecommendation {
  recommended: string;
  reason: string;
  alternates: Array<{ model: string; reason: string }>;
}

interface Config {
  selectedModel?: string;
  hardware?: HardwareInfo;
}

declare global {
  interface Window {
    electronAPI: {
      detectHardware: () => Promise<HardwareInfo>;
      recommendModel: (ramGb: number) => Promise<ModelRecommendation>;
      loadConfig: () => Promise<Config | null>;
      saveConfig: (config: Config) => Promise<boolean>;
    };
  }
}

interface AppProps {
  onComplete?: (config: Config) => void;
}

function App({ onComplete }: AppProps) {
  const [hardware, setHardware] = useState<HardwareInfo | null>(null);
  const [recommendation, setRecommendation] = useState<ModelRecommendation | null>(null);
  const [config, setConfig] = useState<Config | null>(null);
  const [step, setStep] = useState(1);
  const [selectedModel, setSelectedModel] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        const hw = await window.electronAPI.detectHardware();
        setHardware(hw);

        // Get recommendation based on detected RAM
        const rec = await window.electronAPI.recommendModel(hw.ramGb);
        setRecommendation(rec);
        setSelectedModel(rec.recommended);

        const cfg = await window.electronAPI.loadConfig();
        setConfig(cfg);

        if (cfg?.selectedModel) {
          setSelectedModel(cfg.selectedModel);
          setStep(3); // Skip wizard if already configured
        }
      } catch (error) {
        console.error('Initialization error:', error);
      } finally {
        setLoading(false);
      }
    };

    init();
  }, []);

  const handleSaveConfig = async () => {
    if (hardware && selectedModel) {
      const newConfig = {
        selectedModel,
        hardware
      };
      await window.electronAPI.saveConfig(newConfig);
      setConfig(newConfig);
      setStep(3);
    }
  };

  const renderProgressBar = () => (
    <div className="progress-bar">
      <div className={`progress-step ${step >= 1 ? 'completed' : ''} ${step === 1 ? 'active' : ''}`} />
      <div className={`progress-step ${step >= 2 ? 'completed' : ''} ${step === 2 ? 'active' : ''}`} />
      <div className={`progress-step ${step >= 3 ? 'completed' : ''} ${step === 3 ? 'active' : ''}`} />
    </div>
  );

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading configuration...</div>
      </div>
    );
  }

  if (!hardware || !recommendation) {
    return (
      <div className="container">
        <div className="loading">Detecting hardware...</div>
      </div>
    );
  }

  return (
    <div className="container">
      {renderProgressBar()}
      
      <h1>OpenTalent Setup</h1>

      {step === 1 && (
        <div>
          <div className="step-subtitle">Step 1 of 3: System Detection</div>
          <div className="card">
            <h2>📊 System Detected</h2>
            <div className="info">
              <p><strong>Total RAM:</strong> {hardware.ramGb} GB</p>
              <p><strong>Available RAM:</strong> {hardware.ramAvailable} GB</p>
              <p><strong>CPU Cores:</strong> {hardware.cpuCores}</p>
              <p><strong>CPU Model:</strong> {hardware.cpuModel}</p>
              <p><strong>Platform:</strong> {hardware.platform.toUpperCase()}</p>
            </div>
            <div className="buttonGroup">
              <button onClick={() => setStep(2)} className="btn-primary">
                Next: Choose Model →
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <div className="step-subtitle">Step 2 of 3: Select AI Model</div>
          <div className="card">
            <h2>🤖 Choose Your Model</h2>
            <div className="recommendationBox">
              <p>{recommendation.reason}</p>
            </div>

            <div className="modelOptions">
              {[
                { id: 'granite-350m', name: 'Granite 350M', params: '350M', ram: '2-4GB', quality: '⭐⭐⭐' },
                { id: 'granite-2b', name: 'Granite 2B', params: '2B', ram: '8-12GB', quality: '⭐⭐⭐⭐' },
                { id: 'granite-8b', name: 'Granite 8B', params: '8B', ram: '16-32GB', quality: '⭐⭐⭐⭐⭐' }
              ].map((model) => (
                <div
                  key={model.id}
                  onClick={() => setSelectedModel(model.id)}
                  className={`modelOption ${selectedModel === model.id ? 'selected' : ''}`}
                >
                  <div>{model.name}</div>
                  <div>{model.params} params | RAM: {model.ram} | Quality: {model.quality}</div>
                </div>
              ))}
            </div>

            <div className="buttonGroup">
              <button onClick={() => setStep(1)} className="btn-secondary">
                ← Back
              </button>
              <button onClick={handleSaveConfig} className="btn-primary">
                Next: Confirm →
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 3 && config && (
        <div>
          <div className="step-subtitle">Step 3 of 3: Setup Complete</div>
          <div className="card">
            <h2>✓ Configuration Saved</h2>
            <div className="confirmation">
              <div className="success-icon">✓</div>
              <p>
                <strong>Selected Model:</strong> {selectedModel.replace('granite-', 'Granite ').toUpperCase()}
              </p>
              <p>
                <strong>System Profile:</strong> {config.hardware?.ramGb}GB RAM, {config.hardware?.cpuCores} cores
              </p>
              <p style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
                Your configuration has been saved. OpenTalent is ready to use!
              </p>
            </div>
            <div className="buttonGroup">
              <button className="btn-primary" onClick={() => onComplete?.(config!)}>
                Start Interview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
