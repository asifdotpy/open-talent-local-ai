/**
 * Demo Screen Component
 * Comprehensive demo interface for SelectUSA presentation
 * Integrates all demo components: dashboard, progress, voice analysis, avatar
 */

import React, { useState, useEffect } from 'react';
import DemoDashboard from '../../components/DemoDashboard';
import DemoProgress, { DemoStep } from '../../components/DemoProgress';
import VoiceAnalysisDisplay from '../../components/VoiceAnalysisDisplay';
import AvatarDisplay from '../../components/AvatarDisplay';
import { AvatarGender, AvatarSkinTone } from '../../services/avatar-renderer';
import StatusBar from '../ui/StatusBar';

interface DemoScreenProps {
  onExit?: () => void;
}

export const DemoScreen: React.FC<DemoScreenProps> = ({ onExit }) => {
  const [currentView, setCurrentView] = useState<'dashboard' | 'demo' | 'results'>('dashboard');
  const [demoSteps, setDemoSteps] = useState<DemoStep[]>([]);
  const [currentDemoStep, setCurrentDemoStep] = useState<string | null>(null);
  const [voiceAnalysisData, setVoiceAnalysisData] = useState(null);
  const [serviceStatuses, setServiceStatuses] = useState<any[]>([]);

  // Mock service statuses for demo
  useEffect(() => {
    const mockStatuses = [
      { name: 'gateway', status: 'online', latencyMs: 12 },
      { name: 'interview', status: 'online', latencyMs: 45 },
      { name: 'voice', status: 'online', latencyMs: 23 },
      { name: 'analytics', status: 'online', latencyMs: 34 },
      { name: 'avatar', status: 'online', latencyMs: 67 },
      { name: 'conversation', status: 'online', latencyMs: 28 },
      { name: 'desktop-integration', status: 'online', latencyMs: 15 },
      { name: 'candidate', status: 'online', latencyMs: 31 },
      { name: 'security', status: 'online', latencyMs: 19 },
      { name: 'notification', status: 'online', latencyMs: 22 },
      { name: 'user', status: 'online', latencyMs: 26 },
    ];
    setServiceStatuses(mockStatuses);
  }, []);

  const handleDemoStart = (demoType: string) => {
    setCurrentView('demo');
    setDemoSteps([]);
    setCurrentDemoStep('intro');

    // Simulate demo progress
    const mockSteps: DemoStep[] = [
      { type: 'intro', completed: true, timestamp: new Date() },
      { type: 'question', completed: true, timestamp: new Date() },
      { type: 'response', completed: true, timestamp: new Date() },
      { type: 'sentiment', completed: true, timestamp: new Date(), data: { score: 0.75, magnitude: 0.8 } },
      { type: 'voice_analysis', completed: true, timestamp: new Date(), data: {
        confidence: 0.82,
        clarity: 0.78,
        volume: 0.85,
        pace: 145,
        pauses: 2,
        fillerWords: ['um', 'like']
      }},
      { type: 'avatar', completed: true, timestamp: new Date(), data: { videoUrl: 'demo-url', duration: 4.1 } },
      { type: 'service_health', completed: true, timestamp: new Date(), data: { healthy: 11, total: 11 } },
    ];

    // Add steps progressively to simulate real-time progress
    mockSteps.forEach((step, index) => {
      setTimeout(() => {
        setDemoSteps(prev => [...prev, step]);
        setCurrentDemoStep(step.type);
        if (step.type === 'voice_analysis' && step.data) {
          setVoiceAnalysisData(step.data);
        }
      }, index * 1000);
    });

    // Complete demo after all steps
    setTimeout(() => {
      setCurrentDemoStep(null);
      setCurrentView('results');
    }, mockSteps.length * 1000 + 2000);
  };

  const handleDemoComplete = (results: any) => {
    console.log('Demo completed:', results);
  };

  const renderDashboard = () => (
    <div className="demo-screen">
      <div className="header-controls mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">OpenTalent Demo Center</h1>
          <p className="text-gray-600 mt-1">SelectUSA Competition Showcase</p>
        </div>
        <button
          onClick={onExit}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
        >
          Exit Demo
        </button>
      </div>

      <DemoDashboard
        onDemoStart={handleDemoStart}
        onDemoComplete={handleDemoComplete}
      />
    </div>
  );

  const renderDemo = () => (
    <div className="demo-screen">
      <StatusBar services={serviceStatuses} integrationStatus="online" />

      <div className="header-controls mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Demo in Progress</h1>
          <p className="text-gray-600 mt-1">Watch all services work together</p>
        </div>
        <button
          onClick={() => setCurrentView('dashboard')}
          className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors"
        >
          Back to Dashboard
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Column: Progress & Voice Analysis */}
        <div className="space-y-6">
          <DemoProgress
            steps={demoSteps}
            currentStep={currentDemoStep as any}
            showDetails={true}
          />

          {voiceAnalysisData && (
            <VoiceAnalysisDisplay
              analysis={voiceAnalysisData}
              showDetails={true}
            />
          )}
        </div>

        {/* Right Column: Avatar Display */}
        <div>
          <AvatarDisplay
            config={{
              gender: AvatarGender.FEMALE,
              skinTone: AvatarSkinTone.MEDIUM,
            }}
            showControls={false}
            recordingStatus="idle"
            autoPlay={true}
          />
        </div>
      </div>
    </div>
  );

  const renderResults = () => (
    <div className="demo-screen">
      <StatusBar services={serviceStatuses} integrationStatus="online" />

      <div className="header-controls mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Demo Complete! 🎉</h1>
          <p className="text-gray-600 mt-1">All services successfully demonstrated</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setCurrentView('demo')}
            className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors"
          >
            View Demo Again
          </button>
          <button
            onClick={() => setCurrentView('dashboard')}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      {/* Final Results Summary */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🏆</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            SelectUSA Demo Successful!
          </h2>
          <p className="text-gray-600">
            Demonstrated all 11 microservices working together in a privacy-first platform
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-3xl mb-2">🔒</div>
            <div className="font-semibold text-green-900">100% Private</div>
            <div className="text-sm text-green-700">No cloud dependencies</div>
          </div>

          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl mb-2">⚡</div>
            <div className="font-semibold text-blue-900">Hardware Flexible</div>
            <div className="text-sm text-blue-700">4GB to 32GB RAM support</div>
          </div>

          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-3xl mb-2">🔧</div>
            <div className="font-semibold text-purple-900">11 Services</div>
            <div className="text-sm text-purple-700">Microservices architecture</div>
          </div>
        </div>

        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold mb-4">Services Demonstrated:</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {[
              'Gateway Service',
              'Interview Service',
              'Voice Service (Piper TTS)',
              'Analytics Service',
              'Avatar Service (WebGL)',
              'Conversation Service',
              'Desktop Integration',
              'Candidate Management',
              'Security Service',
              'Notification Service',
              'User Management'
            ].map((service, index) => (
              <div key={index} className="flex items-center text-sm">
                <span className="text-green-500 mr-2">✅</span>
                {service}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {currentView === 'dashboard' && renderDashboard()}
      {currentView === 'demo' && renderDemo()}
      {currentView === 'results' && renderResults()}
    </div>
  );
};

export default DemoScreen;