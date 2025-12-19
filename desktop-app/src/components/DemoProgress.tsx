/**
 * Demo Progress Component
 * Shows step-by-step progress of interview demo
 * Displays current step, completed steps, and upcoming steps
 */

import React from 'react';

export type DemoStepType =
  | 'intro'
  | 'question'
  | 'response'
  | 'sentiment'
  | 'voice_analysis'
  | 'avatar'
  | 'service_health'
  | 'summary'
  | 'error';

export interface DemoStep {
  type: DemoStepType;
  data?: any;
  timestamp?: Date;
  completed?: boolean;
}

interface DemoProgressProps {
  steps: DemoStep[];
  currentStep?: DemoStepType;
  showDetails?: boolean;
}

const STEP_LABELS: Record<DemoStepType, string> = {
  intro: 'Demo Started',
  question: 'Question Generated',
  response: 'Response Processed',
  sentiment: 'Sentiment Analyzed',
  voice_analysis: 'Voice Analyzed',
  avatar: 'Avatar Generated',
  service_health: 'Services Checked',
  summary: 'Summary Complete',
  error: 'Error Occurred',
};

const STEP_ICONS: Record<DemoStepType, string> = {
  intro: '🚀',
  question: '❓',
  response: '💬',
  sentiment: '📊',
  voice_analysis: '🎵',
  avatar: '🎭',
  service_health: '🔍',
  summary: '✅',
  error: '❌',
};

const STEP_DESCRIPTIONS: Record<DemoStepType, string> = {
  intro: 'Initializing demo environment',
  question: 'AI interviewer generates question',
  response: 'Candidate provides response',
  sentiment: 'Analyzing emotional tone',
  voice_analysis: 'Evaluating speech quality',
  avatar: 'Creating lip-sync animation',
  service_health: 'Checking all microservices',
  summary: 'Generating interview summary',
  error: 'Demo encountered an issue',
};

export const DemoProgress: React.FC<DemoProgressProps> = ({
  steps,
  currentStep,
  showDetails = false,
}) => {
  const getStepStatus = (stepType: DemoStepType) => {
    const step = steps.find(s => s.type === stepType);
    if (!step) return 'pending';
    if (step.type === 'error') return 'error';
    if (step.completed) return 'completed';
    if (currentStep === stepType) return 'current';
    return 'pending';
  };

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500 border-green-500';
      case 'current': return 'bg-blue-500 border-blue-500 animate-pulse';
      case 'error': return 'bg-red-500 border-red-500';
      default: return 'bg-gray-300 border-gray-300';
    }
  };

  const getStepTextColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-700';
      case 'current': return 'text-blue-700 font-semibold';
      case 'error': return 'text-red-700';
      default: return 'text-gray-500';
    }
  };

  const allSteps: DemoStepType[] = [
    'intro', 'question', 'response', 'sentiment',
    'voice_analysis', 'avatar', 'service_health', 'summary'
  ];

  return (
    <div className="demo-progress bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <div className="text-2xl mr-3">📈</div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Demo Progress</h3>
          <p className="text-sm text-gray-600">Step-by-step execution status</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-gray-500 mb-2">
          <span>Start</span>
          <span>{steps.filter(s => s.completed).length} of {allSteps.length} Complete</span>
          <span>Finish</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${(steps.filter(s => s.completed).length / allSteps.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Step List */}
      <div className="space-y-3">
        {allSteps.map((stepType, index) => {
          const status = getStepStatus(stepType);
          const step = steps.find(s => s.type === stepType);

          return (
            <div key={stepType} className="flex items-center space-x-3">
              {/* Step Circle */}
              <div className={`
                w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-semibold
                ${getStepColor(status)}
                ${status === 'completed' ? 'text-white' : status === 'current' ? 'text-white' : 'text-gray-600'}
              `}>
                {status === 'completed' ? '✓' : status === 'error' ? '✕' : index + 1}
              </div>

              {/* Step Content */}
              <div className="flex-1">
                <div className={`flex items-center ${getStepTextColor(status)}`}>
                  <span className="mr-2">{STEP_ICONS[stepType]}</span>
                  <span className="font-medium">{STEP_LABELS[stepType]}</span>
                  {status === 'current' && (
                    <div className="ml-2 flex items-center">
                      <div className="animate-spin rounded-full h-3 w-3 border-b border-blue-600"></div>
                    </div>
                  )}
                </div>

                {showDetails && (
                  <div className="text-sm text-gray-600 mt-1">
                    {STEP_DESCRIPTIONS[stepType]}
                    {step?.timestamp && (
                      <span className="ml-2 text-xs">
                        ({step.timestamp.toLocaleTimeString()})
                      </span>
                    )}
                  </div>
                )}

                {/* Step-specific data display */}
                {showDetails && step?.data && status === 'completed' && (
                  <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                    {step.type === 'sentiment' && (
                      <div>
                        Score: {(step.data.score * 100).toFixed(1)}% |
                        Magnitude: {(step.data.magnitude * 100).toFixed(1)}%
                      </div>
                    )}
                    {step.type === 'voice_analysis' && (
                      <div>
                        Confidence: {(step.data.confidence * 100).toFixed(1)}% |
                        Clarity: {(step.data.clarity * 100).toFixed(1)}%
                      </div>
                    )}
                    {step.type === 'avatar' && (
                      <div>
                        Video: {step.data.videoUrl ? 'Generated' : 'Failed'} |
                        Duration: {step.data.duration}s
                      </div>
                    )}
                    {step.type === 'service_health' && (
                      <div>
                        Services: {step.data.healthy}/{step.data.total} healthy
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Current Status */}
      {currentStep && (
        <div className="mt-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center text-blue-800">
            <div className="animate-pulse mr-2">🔄</div>
            <div className="text-sm">
              <strong>Currently:</strong> {STEP_LABELS[currentStep]}
            </div>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {steps.some(s => s.type === 'summary' && s.completed) && (
        <div className="mt-6 p-3 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center text-green-800">
            <div className="text-2xl mr-2">🎉</div>
            <div className="text-sm font-medium">
              Demo completed successfully! All services demonstrated.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DemoProgress;