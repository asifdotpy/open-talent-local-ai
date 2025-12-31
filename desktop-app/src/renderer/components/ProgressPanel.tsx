import React, { CSSProperties } from 'react';

interface Activity {
    timestamp: string;
    type: 'success' | 'info' | 'warning' | 'error';
    icon: string;
    message: string;
}

interface Pipeline {
    id?: string;
    status: 'pending' | 'scanning' | 'enriching' | 'scoring' | 'completed' | 'failed';
    progress: number;
    activities: Activity[];
}

interface AgentHealth {
    [agentName: string]: 'healthy' | 'unhealthy' | 'unreachable' | 'unknown';
}

interface ProgressPanelProps {
    pipeline: Pipeline | null;
    agentHealth: AgentHealth;
}

const statusLabels: Record<string, string> = {
    pending: 'Ready to Start',
    scanning: 'Scanning',
    enriching: 'Enriching',
    scoring: 'Scoring',
    completed: 'Finished',
    failed: 'Failed'
};

export function ProgressPanel({ pipeline, agentHealth }: ProgressPanelProps) {
    if (!pipeline) {
        return (
            <div className="progress-panel">
                <h3>Pipeline Status</h3>
                <div className="no-search">
                    <p>Start a search to see progress</p>
                </div>
            </div>
        );
    }

    const { status, progress, activities } = pipeline;
    const progressDeg = (progress / 100) * 360;

    return (
        <div className="progress-panel">
            <h3>Pipeline Status</h3>

            <div className="circular-progress-container">
                <div
                    className="circular-progress"
                    style={{ '--progress': `${progressDeg}deg` } as any}
                >
                    <div className="circular-progress-inner">
                        <span className="progress-value">{progress}%</span>
                        <span className="progress-status-label">{statusLabels[status]}</span>
                    </div>
                </div>
            </div>

            <div className="linear-progress-mini">
                <div className="linear-progress-fill" style={{ width: `${progress}%` }} />
            </div>

            <div className="activity-feed-section">
                <h4>Recent Activity</h4>
                <div className="activities-list">
                    {activities.length === 0 ? (
                        <p className="no-activities">Waiting for activity...</p>
                    ) : (
                        activities.slice(-3).reverse().map((activity, i) => (
                            <div key={i} className={`activity-item activity-${activity.type}`}>
                                <span className="activity-icon">{activity.icon === '📡' ? '🔵' : activity.icon === '🚀' ? '🟢' : activity.icon}</span>
                                <span className="activity-message">{activity.message}</span>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <div className="agent-health" style={{ marginTop: '20px' }}>
                <h4>Agent Status</h4>
                <div className="agents-grid">
                    {Object.entries(agentHealth).slice(0, 3).map(([name, health]) => (
                        <div key={name} className={`agent-item agent-${health}`} style={{ padding: '6px 10px' }}>
                            <span className="agent-name" style={{ fontSize: '12px' }}>{formatAgentName(name)}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function formatAgentName(name: string): string {
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
