import React from 'react';
import { Button } from '../../ui/Button';
import { Card } from '../../ui/Card';

interface ResultsProps {
  summary: Record<string, any>;
  onNewInterview: () => void;
}

export default function Results({ summary, onNewInterview }: ResultsProps) {
  const formatValue = (val: any): string => {
    if (typeof val === 'number') return val.toFixed(2);
    if (Array.isArray(val)) return val.join(', ');
    if (typeof val === 'object' && val !== null) return JSON.stringify(val, null, 2);
    return String(val);
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-600 bg-green-100';
    if (score < -0.3) return 'text-red-600 bg-red-100';
    return 'text-yellow-600 bg-yellow-100';
  };

  const getQualityColor = (score: number) => {
    if (score >= 8) return 'text-green-600 bg-green-100';
    if (score >= 6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-4xl mx-auto px-4">
        <header className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="bg-green-100 p-3 rounded-full">
              <span className="text-3xl">✓</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Interview Complete</h1>
          <p className="text-gray-600 mt-2">Thank you for completing the interview!</p>
        </header>

        {/* Performance Overview */}
        {summary.analyticsAvailable && (
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <Card className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Quality</h3>
              <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getQualityColor(summary.averageQuality || 5)}`}>
                {summary.averageQuality?.toFixed(1) || '5.0'}/10
              </div>
            </Card>

            <Card className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Sentiment</h3>
              <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(summary.averageSentiment || 0)}`}>
                {summary.averageSentiment > 0.3 ? 'Positive' : summary.averageSentiment < -0.3 ? 'Needs Work' : 'Neutral'}
              </div>
            </Card>

            <Card className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Trend</h3>
              <div className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-600">
                {summary.sentimentTrend === 'improving' ? '↗ Improving' : '→ Stable'}
              </div>
            </Card>
          </div>
        )}

        {/* Recommendations */}
        {summary.recommendations && summary.recommendations.length > 0 && (
          <Card className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h2>
            <ul className="space-y-2">
              {summary.recommendations.map((rec: string, i: number) => (
                <li key={i} className="flex items-start">
                  <span className="text-blue-500 mr-2">💡</span>
                  <span className="text-gray-700">{rec}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* Detailed Summary */}
        <Card className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Interview Summary</h2>
          <div className="space-y-4">
            {Object.entries(summary).map(([key, value]) => {
              // Skip internal fields and already displayed data
              if (key.startsWith('_') || key === 'session' || 
                  ['analyticsAvailable', 'averageSentiment', 'averageQuality', 'sentimentTrend', 'recommendations', 'detailedAnalytics'].includes(key)) {
                return null;
              }
              return (
                <div key={key} className="border-b border-gray-200 pb-4 last:border-b-0">
                  <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">{key.replace(/([A-Z])/g, ' $1')}</p>
                  <p className="text-gray-900 mt-1 whitespace-pre-wrap text-sm">{formatValue(value)}</p>
                </div>
              );
            })}
          </div>
        </Card>

        {/* Analytics Details (if available) */}
        {summary.detailedAnalytics && (
          <Card className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Detailed Analytics</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-600 mb-2">Sentiment Scores</h3>
                <div className="flex space-x-2">
                  {summary.detailedAnalytics.sentimentScores?.map((score: number, i: number) => (
                    <div key={i} className={`px-2 py-1 rounded text-xs font-medium ${getSentimentColor(score)}`}>
                      Q{i+1}: {score.toFixed(1)}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-600 mb-2">Quality Scores</h3>
                <div className="flex space-x-2">
                  {summary.detailedAnalytics.qualityScores?.map((score: number, i: number) => (
                    <div key={i} className={`px-2 py-1 rounded text-xs font-medium ${getQualityColor(score)}`}>
                      Q{i+1}: {score.toFixed(1)}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        )}

        <div className="flex justify-center gap-4">
          <Button onClick={onNewInterview} className="w-full md:w-auto">
            Start New Interview
          </Button>
        </div>

        <footer className="text-center text-sm text-gray-600 mt-12">
          🔒 All processing happens locally on your device.
        </footer>
      </div>
    </div>
  );
}
