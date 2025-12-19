import React, { useEffect, useMemo, useState } from 'react';
import { Button } from '../../ui/Button';
import { Card } from '../../ui/Card';
import { Input } from '../../ui/Input';
import { cn } from '../../lib/utils';
import GatewayClient, { configureGateway } from '../../services/gateway-enhanced-client';
import type { InterviewSession } from '../../api/gateway';
import Interview from './Interview';
import Results from './Results';

type HealthStatus = 'online' | 'offline' | 'degraded' | 'unknown';

const JOB_ROLES = [
  'Software Engineer',
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'DevOps Engineer',
  'Data Scientist',
  'Product Manager',
  'UI/UX Designer',
  'QA Engineer',
  'Technical Lead',
];

export default function DashboardScreen() {
  const [candidateId, setCandidateId] = useState('');
  const [jobRole, setJobRole] = useState('');
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [health, setHealth] = useState<HealthStatus>('unknown');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [screen, setScreen] = useState<'dashboard' | 'interview' | 'results'>('dashboard');
  const [currentSession, setCurrentSession] = useState<InterviewSession | null>(null);
  const [currentSummary, setCurrentSummary] = useState<Record<string, any> | null>(null);

  const gatewayBase = useMemo(() => {
    return process.env.REACT_APP_INTEGRATION_BASE_URL || 'http://localhost:8009';
  }, []);

  useEffect(() => {
    configureGateway(gatewayBase);
    (async () => {
      await Promise.all([
        (async () => fetchHealth())(),
        (async () => fetchModels())(),
      ]);
    })();
  }, [gatewayBase]);

  async function refresh() {
    await Promise.all([fetchHealth(), fetchModels()]);
  }

  async function fetchHealth() {
    try {
      const h = await GatewayClient.system.getHealth();
      if (!h) {
        setHealth('offline');
        return;
      }
      setHealth((h.status as HealthStatus) || 'degraded');
    } catch {
      setHealth('offline');
    }
  }

  async function fetchModels() {
    try {
      const m = await GatewayClient.models.list();
      const names = (m || []).map((x: any) => x.name || x.id).filter(Boolean);
      setModels(names);
      if (names.length && !selectedModel) setSelectedModel(names[0]);
    } catch (e) {
      console.error('Failed to fetch models', e);
      setModels([]);
    }
  }

  async function startInterview() {
    setLoading(true);
    setError(null);
    try {
      if (!candidateId.trim()) throw new Error('Candidate ID is required');
      if (!jobRole) throw new Error('Please select a job role');
      if (!selectedModel) throw new Error('Please select a model');

      const session = await GatewayClient.interview.start({
        role: jobRole,
        model: selectedModel,
        totalQuestions: 5,
      });
      if (!session) throw new Error('Failed to start interview');

      setCurrentSession(session);
      setScreen('interview');
    } catch (e: any) {
      setError(e?.message || 'Failed to start interview');
    } finally {
      setLoading(false);
    }
  }

  function handleInterviewSummary(summary: Record<string, any>) {
    setCurrentSummary(summary);
    setScreen('results');
  }

  function handleBack() {
    setCurrentSession(null);
    setScreen('dashboard');
  }

  function handleNewInterview() {
    setCandidateId('');
    setJobRole('');
    setCurrentSession(null);
    setCurrentSummary(null);
    setScreen('dashboard');
  }

  if (screen === 'interview' && currentSession) {
    return <Interview session={currentSession} onSummary={handleInterviewSummary} onBack={handleBack} />;
  }

  if (screen === 'results' && currentSummary) {
    return <Results summary={currentSummary} onNewInterview={handleNewInterview} />;
  }

  const healthBadge = (
    <span
      className={cn(
        'px-2 py-1 text-xs rounded-md font-medium',
        health === 'online' && 'bg-green-100 text-green-800',
        health === 'degraded' && 'bg-yellow-100 text-yellow-800',
        health === 'offline' && 'bg-red-100 text-red-800',
        health === 'unknown' && 'bg-gray-100 text-gray-800'
      )}
    >
      {health === 'online' ? 'Gateway Online' : health === 'degraded' ? 'Gateway Degraded' : health === 'offline' ? 'Gateway Offline' : 'Checking...'}
    </span>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-4xl mx-auto px-4">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">OpenTalent</h1>
            <p className="text-gray-600">Privacy-First AI Interviews</p>
          </div>
          <div className="flex items-center gap-3">
            {healthBadge}
            <Button
              variant="outline"
              onClick={refresh}
              className="border-gray-300"
            >
              Refresh
            </Button>
          </div>
        </header>

        <Card className="mb-8">
          <div className="flex items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Start Your Interview</h2>
          </div>

          {health === 'offline' && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
              <p className="text-yellow-800 font-medium">Integration service offline</p>
              <p className="text-yellow-700 text-sm mt-1">Start the gateway on http://localhost:8009 then click Refresh.</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Candidate ID</label>
              <Input
                placeholder="Enter your candidate ID"
                value={candidateId}
                onChange={(e) => setCandidateId(e.target.value)}
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Job Role</label>
              <select
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={jobRole}
                onChange={(e) => setJobRole(e.target.value)}
                disabled={loading}
              >
                <option value="">Select a job role</option>
                {JOB_ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
              <select
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                disabled={loading || !models.length}
              >
                {models.length === 0 ? (
                  <option value="">No models available</option>
                ) : (
                  models.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))
                )}
              </select>
            </div>
            <div className="flex items-end">
              <Button
                className="w-full md:w-auto"
                onClick={startInterview}
                disabled={loading || !candidateId.trim() || !jobRole || !selectedModel || health === 'offline'}
              >
                {loading ? 'Starting…' : 'Start AI Interview'}
              </Button>
            </div>
          </div>
        </Card>

        <footer className="text-center text-sm text-gray-600">
          🔒 All processing happens locally on your device.
        </footer>
      </div>
    </div>
  );
}
