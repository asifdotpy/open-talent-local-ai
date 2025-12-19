/**
 * Voice Analysis Display Component
 * Shows voice clarity, confidence, and analysis metrics
 * Used in interview demo for voice analysis step
 */

import React from 'react';

interface VoiceAnalysisData {
  confidence: number; // 0-1
  clarity: number; // 0-1
  volume: number; // 0-1
  pace: number; // words per minute
  pauses: number; // number of pauses
  fillerWords: string[]; // detected filler words
}

interface VoiceAnalysisDisplayProps {
  analysis: VoiceAnalysisData;
  showDetails?: boolean;
}

export const VoiceAnalysisDisplay: React.FC<VoiceAnalysisDisplayProps> = ({
  analysis,
  showDetails = true,
}) => {
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getClarityColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600 bg-green-100';
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;

  return (
    <div className="voice-analysis-display bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-4">
        <div className="text-2xl mr-3">🎵</div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Voice Analysis</h3>
          <p className="text-sm text-gray-600">Real-time voice quality assessment</p>
        </div>
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className={`inline-block px-3 py-2 rounded-full text-sm font-semibold ${getConfidenceColor(analysis.confidence)}`}>
            {formatPercentage(analysis.confidence)}
          </div>
          <div className="text-xs text-gray-600 mt-1">Confidence</div>
        </div>

        <div className="text-center">
          <div className={`inline-block px-3 py-2 rounded-full text-sm font-semibold ${getClarityColor(analysis.clarity)}`}>
            {formatPercentage(analysis.clarity)}
          </div>
          <div className="text-xs text-gray-600 mt-1">Clarity</div>
        </div>

        <div className="text-center">
          <div className="inline-block px-3 py-2 rounded-full text-sm font-semibold bg-blue-100 text-blue-600">
            {analysis.pace}
          </div>
          <div className="text-xs text-gray-600 mt-1">WPM</div>
        </div>

        <div className="text-center">
          <div className="inline-block px-3 py-2 rounded-full text-sm font-semibold bg-purple-100 text-purple-600">
            {formatPercentage(analysis.volume)}
          </div>
          <div className="text-xs text-gray-600 mt-1">Volume</div>
        </div>
      </div>

      {/* Detailed Metrics */}
      {showDetails && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Detailed Analysis</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Speech Pace:</span>
                <span className="font-medium">{analysis.pace} WPM</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Pauses Detected:</span>
                <span className="font-medium">{analysis.pauses}</span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Volume Level:</span>
                <span className="font-medium">{formatPercentage(analysis.volume)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Clarity Score:</span>
                <span className="font-medium">{formatPercentage(analysis.clarity)}</span>
              </div>
            </div>
          </div>

          {/* Filler Words */}
          {analysis.fillerWords.length > 0 && (
            <div className="mt-4">
              <div className="text-sm text-gray-600 mb-2">Detected Filler Words:</div>
              <div className="flex flex-wrap gap-2">
                {analysis.fillerWords.map((word, index) => (
                  <span
                    key={index}
                    className="inline-block px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full"
                  >
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <div className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> {
            analysis.confidence < 0.6 ? 'Try speaking more clearly and confidently.' :
            analysis.clarity < 0.5 ? 'Reduce background noise for better clarity.' :
            analysis.pace < 120 ? 'Consider speaking at a moderate pace.' :
            'Great voice quality! Keep it up.'
          }
        </div>
      </div>
    </div>
  );
};

export default VoiceAnalysisDisplay;