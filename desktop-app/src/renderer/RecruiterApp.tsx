import React, { useState, useEffect } from 'react';
import { SearchPrompt } from './components/SearchPrompt';
import { ProgressPanel } from './components/ProgressPanel';
import './components/components.css';

interface Pipeline {
    id?: string;
    status: 'pending' | 'scanning' | 'enriching' | 'scoring' | 'completed' | 'failed';
    progress: number;
    activities: Activity[];
}

interface Activity {
    timestamp: string;
    type: 'success' | 'info' | 'warning' | 'error';
    icon: string;
    message: string;
}

interface AgentHealth {
    [key: string]: 'healthy' | 'unhealthy' | 'unreachable' | 'unknown';
}

export function RecruiterApp() {
    const [isSearching, setIsSearching] = useState(false);
    const [pipeline, setPipeline] = useState<Pipeline | null>(null);
    const [agentHealth, setAgentHealth] = useState<AgentHealth>({});

    // Poll for agent health every 10 seconds
    useEffect(() => {
        checkAgentHealth();
        const interval = setInterval(checkAgentHealth, 10000);
        return () => clearInterval(interval);
    }, []);

    // Mock agent health check (will be replaced with real API call)
    const checkAgentHealth = async () => {
        try {
            // TODO: Replace with actual scout-coordinator-agent health check
            // const response = await fetch('http://localhost:8095/agents/health');
            // const data = await response.json();

            // Mock data for now
            setAgentHealth({
                'scout-coordinator': 'healthy',
                'data-enrichment': 'healthy',
                'quality-focused': 'healthy',
                'proactive-scanning': 'healthy',
                'boolean-mastery': 'healthy'
            });
        } catch (error) {
            console.error('Agent health check failed:', error);
            setAgentHealth({
                'scout-coordinator': 'unreachable'
            });
        }
    };

    const handleSearch = async ({ prompt, tools }: { prompt: string; tools: string[] }) => {
        console.log('Starting search:', { prompt, tools });
        setIsSearching(true);

        // Initialize pipeline
        setPipeline({
            status: 'pending',
            progress: 0,
            activities: [{
                timestamp: new Date().toLocaleTimeString(),
                type: 'info',
                icon: '🚀',
                message: 'Search initiated'
            }]
        });

        // TODO: Replace with actual scout-coordinator-agent API call
        // Mock pipeline simulation for now
        simulatePipeline(prompt, tools);
    };

    // Mock pipeline simulation (will be replaced with WebSocket updates)
    const simulatePipeline = (prompt: string, tools: string[]) => {
        setTimeout(() => {
            setPipeline(prev => prev ? {
                ...prev,
                status: 'scanning',
                progress: 25,
                activities: [
                    ...prev.activities,
                    {
                        timestamp: new Date().toLocaleTimeString(),
                        type: 'info',
                        icon: '🔍',
                        message: `Scanning ${tools.length} sources...`
                    }
                ]
            } : null);
        }, 1000);

        setTimeout(() => {
            setPipeline(prev => prev ? {
                ...prev,
                progress: 50,
                activities: [
                    ...prev.activities,
                    {
                        timestamp: new Date().toLocaleTimeString(),
                        type: 'success',
                        icon: '✅',
                        message: 'Found 12 potential candidates'
                    }
                ]
            } : null);
        }, 3000);

        setTimeout(() => {
            setPipeline(prev => prev ? {
                ...prev,
                status: 'enriching',
                progress: 75,
                activities: [
                    ...prev.activities,
                    {
                        timestamp: new Date().toLocaleTimeString(),
                        type: 'info',
                        icon: '📊',
                        message: 'Enriching candidate profiles...'
                    }
                ]
            } : null);
        }, 5000);

        setTimeout(() => {
            setPipeline(prev => prev ? {
                ...prev,
                status: 'completed',
                progress: 100,
                activities: [
                    ...prev.activities,
                    {
                        timestamp: new Date().toLocaleTimeString(),
                        type: 'success',
                        icon: '🎉',
                        message: 'Search completed! Found 12 candidates'
                    }
                ]
            } : null);
            setIsSearching(false);
        }, 7000);
    };

    return (
        <div className="recruiter-app">
            <header className="header">
                <div className="logo">
                    <h1>🎯 OpenTalent Recruiter</h1>
                    <p className="tagline">AI-Powered Candidate Discovery</p>
                </div>
                <div className="status">
                    <span className={`status-indicator ${Object.values(agentHealth).every(h => h === 'healthy') ? 'online' :
                            Object.values(agentHealth).some(h => h === 'healthy') ? 'warning' : 'offline'
                        }`}>
                        {Object.values(agentHealth).filter(h => h === 'healthy').length} / {Object.keys(agentHealth).length} Agents Online
                    </span>
                </div>
            </header>

            <main className="main-content">
                <SearchPrompt onSearch={handleSearch} isSearching={isSearching} />
                <ProgressPanel pipeline={pipeline} agentHealth={agentHealth} />
            </main>

            <footer className="footer">
                <p>🔒 Private recruiting platform. All data processing happens locally.</p>
            </footer>
        </div>
    );
}
