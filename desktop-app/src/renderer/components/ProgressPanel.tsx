import React from 'react';

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

const statusLabels = {
    pending: 'Pending',
    scanning: 'Scanning for Candidates',
    enriching: 'Enriching Profiles',
    scoring: 'Scoring Candidates',
    completed: 'Completed',
    failed: 'Failed'
};

const statusEmoji = {
    pending: '⏳',
    scanning: '🔍',
    enriching: '📊',
    scoring: '⭐',
    completed: '✅',
    failed: '❌'
};

export function ProgressPanel({ pipeline, agentHealth }: ProgressPanelProps) {
    if (!pipeline) {
        return (
            <div className="progress-panel">
                <div className="no-search">
                    <p>💡 Enter a job description above to start searching for candidates</p>
                </div>
            </div>
        );
    }

    const { status, progress, activities } = pipeline;

    return (
        <div className="progress-panel">
            <h3>Search Progress</h3>

            <div className="status-indicator">
                <span className="status-emoji">{statusEmoji[status]}</span>
                <span className={`status-text status-${status}`}>
                    {statusLabels[status]}
                </span>
            </div>

            <div className="progress-bar-container">
                <div className="progress-bar">
                    <div
                        className={`progress-fill progress-${status}`}
                        style={{ width: `${progress}%` }}
                    />
                </div>
                <span className="progress-percentage">{progress}%</span>
            </div>

            <div className="activity-feed">
                <h4>Recent Activity</h4>
                {activities.length === 0 ? (
                    <p className="no-activities">No activities yet</p>
                ) : (
                    <div className="activities-list">
                        {activities.slice(-5).reverse().map((activity, i) => (
                            <div key={i} className={`activity-item activity-${activity.type}`}>
                                <span className="activity-time">{activity.timestamp}</span>
                                <span className="activity-icon">{activity.icon}</span>
                                <span className="activity-message">{activity.message}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="agent-health">
                <h4>Agent Status</h4>
                <div className="agents-grid">
                    {Object.entries(agentHealth).map(([name, health]) => (
                        <div key={name} className={`agent-item agent-${health}`}>
                            <span className="agent-name">{formatAgentName(name)}</span>
                            <span className="agent-health-indicator">
                                {health === 'healthy' ? '✅' :
                                    health === 'unhealthy' ? '⚠️' :
                                        health === 'unreachable' ? '🔴' : '⚪'}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {status === 'failed' && (
                <div className="error-message">
                    <p>❌ Search failed. Please try again or adjust your search criteria.</p>
                </div>
            )}

            {status === 'completed' && (
                <div className="success-message">
                    <p>🎉 Search completed! Check candidates below.</p>
                </div>
            )}
        </div>
    );
}

function formatAgentName(name: string): string {
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
