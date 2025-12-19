/**
 * Demo Dashboard Component
 * Shows comprehensive service status and demo controls
 * For SelectUSA presentation - displays all 11 microservices
 */

import React, { useState, useEffect } from 'react';
import { runInterviewDemo, runComprehensiveDemo, runSelectUSADemo } from '../services/interview-demo-helper';

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'offline';
  latency?: number;
  version?: string;
}

interface DemoDashboardProps {
  onDemoStart?: (demoType: string) => void;
  onDemoComplete?: (results: any) => void;
}

export const DemoDashboard: React.FC<DemoDashboardProps> = ({
  onDemoStart,
  onDemoComplete,
}) => {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [demoRunning, setDemoRunning] = useState(false);
  const [currentDemo, setCurrentDemo] = useState<string | null>(null);
  const [demoOutput, setDemoOutput] = useState<string[]>([]);

  // Mock service status for demo
  useEffect(() => {
    const mockServices: ServiceStatus[] = [
      { name: 'gateway', status: 'healthy', latency: 12, version: '1.0.0' },
      { name: 'interview', status: 'healthy', latency: 45, version: '1.0.0' },
      { name: 'voice', status: 'healthy', latency: 23, version: '1.0.0' },
      { name: 'analytics', status: 'healthy', latency: 34, version: '1.0.0' },
      { name: 'avatar', status: 'healthy', latency: 67, version: '1.0.0' },
      { name: 'conversation', status: 'healthy', latency: 28, version: '1.0.0' },
      { name: 'desktop-integration', status: 'healthy', latency: 15, version: '1.0.0' },
      { name: 'candidate', status: 'healthy', latency: 31, version: '1.0.0' },
      { name: 'security', status: 'healthy', latency: 19, version: '1.0.0' },
      { name: 'notification', status: 'healthy', latency: 22, version: '1.0.0' },
      { name: 'user', status: 'healthy', latency: 26, version: '1.0.0' },
    ];
    setServices(mockServices);
  }, []);

  const runDemo = async (demoType: 'interview' | 'selectusa' | 'comprehensive') => {
    setDemoRunning(true);
    setCurrentDemo(demoType);
    setDemoOutput([]);
    onDemoStart?.(demoType);

    try {
      // Capture console.log outputs for demo display
      const originalLog = console.log;
      const logs: string[] = [];
      console.log = (...args) => {
        logs.push(args.join(' '));
        setDemoOutput([...logs]);
        originalLog(...args);
      };

      switch (demoType) {
        case 'interview':
          await runInterviewDemo({
            role: 'Software Engineer',
            model: 'vetta-granite-2b-gguf-v4',
            totalQuestions: 2,
            enableVoice: true,
            enableSentimentAnalysis: true,
            enableVoiceAnalysis: true,
            enableAvatar: true,
            showAllServices: true,
          });
          break;
        case 'selectusa':
          await runSelectUSADemo();
          break;
        case 'comprehensive':
          await runComprehensiveDemo();
          break;
      }

      console.log = originalLog;
      onDemoComplete?.({ type: demoType, logs });
    } catch (error) {
      console.error('Demo failed:', error);
      setDemoOutput(prev => [...prev, `❌ Demo failed: ${error}`]);
    } finally {
      setDemoRunning(false);
      setCurrentDemo(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'offline': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '🟢';
      case 'degraded': return '🟡';
      case 'offline': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="demo-dashboard p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          OpenTalent Demo Dashboard
        </h1>
        <p className="text-gray-600">
          Privacy-First AI Interview Platform - All Services Showcase
        </p>
      </div>

      {/* Service Health Grid */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          🔍 Service Health Status (11 Services)
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {services.map((service) => (
            <div
              key={service.name}
              className={`p-4 rounded-lg border-2 ${getStatusColor(service.status)}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{service.name}</span>
                <span className="text-lg">{getStatusIcon(service.status)}</span>
              </div>
              <div className="text-sm space-y-1">
                <div>Status: <span className="capitalize">{service.status}</span></div>
                {service.latency && <div>Latency: {service.latency}ms</div>}
                {service.version && <div>Version: {service.version}</div>}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full">
            ✅ {services.filter(s => s.status === 'healthy').length}/{services.length} Services Healthy
          </div>
        </div>
      </div>

      {/* Demo Controls */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">🎬 Demo Controls</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <button
            onClick={() => runDemo('interview')}
            disabled={demoRunning}
            className="p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <div className="text-2xl mb-2">🎯</div>
            <div className="font-semibold text-blue-900">Interview Demo</div>
            <div className="text-sm text-blue-700 mt-1">
              Basic interview with voice, sentiment, avatar
            </div>
          </button>

          <button
            onClick={() => runDemo('selectusa')}
            disabled={demoRunning}
            className="p-4 border-2 border-purple-200 rounded-lg hover:border-purple-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <div className="text-2xl mb-2">🏆</div>
            <div className="font-semibold text-purple-900">SelectUSA Demo</div>
            <div className="text-sm text-purple-700 mt-1">
              Competition showcase with all features
            </div>
          </button>

          <button
            onClick={() => runDemo('comprehensive')}
            disabled={demoRunning}
            className="p-4 border-2 border-green-200 rounded-lg hover:border-green-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <div className="text-2xl mb-2">🚀</div>
            <div className="font-semibold text-green-900">Comprehensive Demo</div>
            <div className="text-sm text-green-700 mt-1">
              10-step walkthrough of all services
            </div>
          </button>
        </div>
      </div>

      {/* Demo Output */}
      {(demoRunning || demoOutput.length > 0) && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            📊 Demo Output
            {demoRunning && (
              <div className="ml-4 flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-blue-600">
                  Running {currentDemo} demo...
                </span>
              </div>
            )}
          </h2>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
            {demoOutput.length === 0 ? (
              <div className="text-gray-500 italic">Demo output will appear here...</div>
            ) : (
              demoOutput.map((line, i) => (
                <div key={i} className="mb-1">{line}</div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Privacy Notice */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 text-center">
        <div className="text-4xl mb-4">🔒</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          100% Local Processing
        </h3>
        <p className="text-gray-700">
          All AI processing happens on your device. No data ever leaves your machine.
          Complete privacy and security for sensitive interview data.
        </p>
      </div>
    </div>
  );
};

export default DemoDashboard;