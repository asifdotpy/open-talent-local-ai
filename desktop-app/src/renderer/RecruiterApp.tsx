import React, { useState, useEffect } from 'react';
import { SearchPrompt } from './components/SearchPrompt';
import { ProgressPanel } from './components/ProgressPanel';
import { scoutCoordinator } from '../services/scoutCoordinatorClient';
import { jobDescriptionParser } from '../services/jobDescriptionParser';
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

    // Real agent health check
    const checkAgentHealth = async () => {
        try {
            const health = await scoutCoordinator.getAgentHealth();
            // Transform to simple status format
            const simpleHealth: AgentHealth = {};
            for (const [name, info] of Object.entries(health)) {
                simpleHealth[name] = info.status;
            }
            setAgentHealth(simpleHealth);
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

        try {
            // Parse job description
            const jobData = await jobDescriptionParser.parsePrompt(prompt);
            console.log('Parsed job data:', jobData);

            // Map tool names to platforms
            const platformMap: { [key: string]: string } = {
                'github': 'github',
                'stackoverflow': 'stackoverflow',
                'googleXray': 'linkedin',
                'contactout': 'linkedin',
                'salesql': 'linkedin'
            };
            const platforms = [...new Set(tools.map(t => platformMap[t] || 'linkedin'))];

            // Create pipeline
            const pipelineResponse = await scoutCoordinator.createPipeline({
                project_id: `desktop_${Date.now()}`,
                job_description: prompt,
                job_title: jobData.job_title,
                target_platforms: platforms,
                num_candidates_target: 50,
                priority: 'medium'
            });

            console.log('Pipeline created:', pipelineResponse.pipeline_id);

            // Initialize pipeline UI state
            setPipeline({
                id: pipelineResponse.pipeline_id,
                status: 'scanning',
                progress: 0,
                activities: [{
                    timestamp: new Date().toLocaleTimeString(),
                    type: 'info',
                    icon: '🚀',
                    message: 'Pipeline started'
                }]
            });

            // Start polling for status
            pollPipelineStatus(pipelineResponse.pipeline_id);

        } catch (error) {
            console.error('Search failed:', error);
            setPipeline({
                status: 'failed',
                progress: 0,
                activities: [{
                    timestamp: new Date().toLocaleTimeString(),
                    type: 'error',
                    icon: '❌',
                    message: `Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`
                }]
            });
            setIsSearching(false);
        }
    };

    // Poll pipeline status from scout-coordinator
    const pollPipelineStatus = async (pipelineId: string) => {
        const pollInterval = setInterval(async () => {
            try {
                const status = await scoutCoordinator.getPipelineStatus(pipelineId);
                console.log('Pipeline status:', status);

                // Map backend state to UI state
                const stateMap: { [key: string]: Pipeline['status'] } = {
                    'initiated': 'pending',
                    'scanning': 'scanning',
                    'scoring': 'scoring',
                    'engaging': 'enriching',
                    'interviewing': 'enriching',
                    'completed': 'completed',
                    'failed': 'failed',
                    'paused': 'pending'
                };

                const uiStatus = stateMap[status.state.toLowerCase()] || 'pending';

                setPipeline(prev => ({
                    ...prev,
                    id: pipelineId,
                    status: uiStatus,
                    progress: status.progress_percentage,
                    activities: [
                        ...(prev?.activities || []),
                        {
                            timestamp: new Date().toLocaleTimeString(),
                            type: 'info',
                            icon: uiStatus === 'completed' ? '🎉' : '🔄',
                            message: `${status.state}: ${status.candidates_found} candidates found`
                        }
                    ]
                }));

                // Stop polling if completed or failed
                if (status.state === 'completed' || status.state === 'failed') {
                    clearInterval(pollInterval);
                    setIsSearching(false);
                }

            } catch (error) {
                console.error('Status poll error:', error);
            }
        }, 2000); // Poll every 2 seconds

        // Timeout after 5 minutes
        setTimeout(() => {
            clearInterval(pollInterval);
            setIsSearching(false);
        }, 300000);
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
