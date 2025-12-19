import React, { useState } from 'react';
import { Button } from '../../ui/Button';
import { Card } from '../../ui/Card';
import { Textarea } from '../../ui/Textarea';
import GatewayClient from '../../services/gateway-enhanced-client';
import type { InterviewSession } from '../../api/gateway';

interface InterviewProps {
  session: InterviewSession;
  onSummary: (summary: Record<string, any>) => void;
  onBack: () => void;
}

export default function Interview({ session: initialSession, onSummary, onBack }: InterviewProps) {
  const [session, setSession] = useState(initialSession);
  const [userResponse, setUserResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [questionCount, setQuestionCount] = useState(1);

  const currentQuestion = (() => {
    const assistantMsgs = session.messages.filter((m: any) => m.role === 'assistant');
    return assistantMsgs[assistantMsgs.length - 1]?.content || '';
  })();

  async function handleSubmitResponse() {
    if (!userResponse.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const nextSession = await GatewayClient.interview.respond({
        message: userResponse,
        session,
      });

      if (!nextSession) throw new Error('Failed to get next question');

      setSession(nextSession);
      setUserResponse('');
      setQuestionCount(questionCount + 1);

      // Check if interview is complete
      if (nextSession.isComplete || questionCount >= (nextSession.config?.totalQuestions || 5)) {
        const summary = await GatewayClient.interview.getSummary(nextSession);
        if (summary) {
          onSummary(summary);
        } else {
          throw new Error('Failed to get interview summary');
        }
      }
    } catch (e: any) {
      setError(e?.message || 'Failed to submit response');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-4xl mx-auto px-4">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Interview in Progress</h1>
            <p className="text-gray-600">Question {questionCount} of {session.config?.totalQuestions || 5}</p>
          </div>
          <Button variant="outline" onClick={onBack} disabled={loading}>
            End Interview
          </Button>
        </header>

        <Card className="mb-8">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          )}

          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Interviewer</h2>
            <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
              <p className="text-gray-800 leading-relaxed">{currentQuestion}</p>
            </div>
          </div>

          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">Your Response</label>
            <Textarea
              placeholder="Type your answer here..."
              value={userResponse}
              onChange={(e) => setUserResponse(e.target.value)}
              disabled={loading}
              rows={4}
              className="mb-4"
            />
            <div className="text-sm text-gray-600 mb-4">
              {userResponse.length} characters
            </div>
            <Button
              className="w-full"
              onClick={handleSubmitResponse}
              disabled={loading || !userResponse.trim()}
            >
              {loading ? 'Submitting...' : 'Submit Response'}
            </Button>
          </div>

          <div className="bg-gray-50 p-4 rounded text-sm text-gray-600">
            <p><strong>Interview Flow:</strong></p>
            <p>You will be asked {session.config?.totalQuestions || 5} questions. Answer thoughtfully and hit Submit Response to move to the next question.</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
