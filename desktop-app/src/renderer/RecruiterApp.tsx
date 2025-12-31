import React, { useState, useEffect } from 'react';
import { SearchPrompt } from './components/SearchPrompt';
import { ProgressPanel } from './components/ProgressPanel';
import { CandidateResults, Candidate } from './components/CandidateResults';
import { scoutCoordinator } from '../services/scoutCoordinatorClient';
import { jobDescriptionParser } from '../services/jobDescriptionParser';
import { qualityScoringClient } from '../services/qualityScoringClient';
import { useWebSocket } from './hooks/useWebSocket';
import { ToastProvider, useToast } from './components/Toast';
import { OutreachModal } from './components/OutreachModal';
import { SettingsModal } from './components/SettingsModal';
import { enrichmentClient } from '../services/enrichmentClient';
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
    return (
        <ToastProvider>
            <RecruiterAppContent />
        </ToastProvider>
    );
}

function RecruiterAppContent() {
    const { addToast } = useToast();
    const [isSearching, setIsSearching] = useState(false);
    const [pipeline, setPipeline] = useState<Pipeline | null>(null);
    const [agentHealth, setAgentHealth] = useState<AgentHealth>({});
    const [candidates, setCandidates] = useState<Candidate[]>([]);
    const [outreachCandidate, setOutreachCandidate] = useState<Candidate | null>(null);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [apiKeys, setApiKeys] = useState<{ contactOut?: string; salesQL?: string }>({});

    // WebSocket integration
    useWebSocket((message: any) => {
        console.log('WebSocket received:', message);
        if (message.type === 'pipeline_update') {
            const data = message.payload;
            const stateMap: { [key: string]: Pipeline['status'] } = {
                'initiated': 'pending',
                'scanning': 'scanning',
                'scoring': 'scoring',
                'engaging': 'enriching',
                'interviewing': 'enriching',
                'completed': 'completed',
                'failed': 'failed'
            };

            const uiStatus = stateMap[data.new_state?.toLowerCase() || data.state?.toLowerCase()] || 'pending';

            setPipeline(prevPipeline => {
                if (!prevPipeline || prevPipeline.id !== data.pipeline_id) return prevPipeline;

                if (prevPipeline.status !== uiStatus) {
                    if (uiStatus === 'completed') addToast('Pipeline completed!', 'success');
                }

                return {
                    ...prevPipeline,
                    status: uiStatus,
                    progress: data.progress_percentage ?? prevPipeline.progress ?? 0,
                    activities: [
                        ...prevPipeline.activities,
                        {
                            timestamp: new Date().toLocaleTimeString(),
                            type: 'info',
                            icon: '📡',
                            message: `Update: ${data.new_state || data.state}`
                        }
                    ]
                };
            });
        }
    });

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
            addToast('Sourcing pipeline started successfully', 'success');

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
            const errorMsg = error instanceof Error ? error.message : 'Unknown error';
            addToast(`Search failed: ${errorMsg}`, 'error');
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

                // Trigger toasts and update state
                setPipeline(prevPipeline => {
                    if (!prevPipeline) return null;

                    if (prevPipeline.status !== uiStatus) {
                        if (uiStatus === 'completed') {
                            addToast('Sourcing pipeline completed!', 'success');
                        } else if (uiStatus === 'scanning') {
                            addToast('Started scanning for candidates...', 'info');
                        }
                    }

                    return {
                        ...prevPipeline,
                        id: pipelineId,
                        status: uiStatus,
                        progress: status.progress_percentage ?? prevPipeline.progress ?? 0,
                        activities: [
                            ...(prevPipeline.activities || []),
                            {
                                timestamp: new Date().toLocaleTimeString(),
                                type: 'info',
                                icon: uiStatus === 'completed' ? '🎉' : '🔄',
                                message: `${status.state}: ${status.candidates_found} candidates found`
                            }
                        ]
                    };
                });

                // Stop polling if completed or failed
                if (status.state === 'completed' || status.state === 'failed') {
                    clearInterval(pollInterval);
                    setIsSearching(false);

                    // Fetch and score candidates on completion
                    if (status.state === 'completed') {
                        try {
                            const candidateData = await scoutCoordinator.getCandidates(pipelineId);
                            console.log('Candidates retrieved:', candidateData);

                            // Map and score candidates
                            const mappedCandidates: Candidate[] = await Promise.all(
                                (candidateData.candidates || []).map(async (c: any) => {
                                    // Try to get score if not provided
                                    let score = c.score || 50;
                                    try {
                                        const scoreResult = await qualityScoringClient.scoreCandidate({
                                            candidate_id: c.id,
                                            job_description: pipeline?.activities[0]?.message || '', // Use original prompt or stored JD
                                            candidate_profile: c
                                        });
                                        score = scoreResult.overall_score;
                                    } catch (err) {
                                        console.warn(`Scoring failed for candidate ${c.id}:`, err);
                                    }

                                    return {
                                        id: c.id,
                                        name: c.name || 'Anonymous',
                                        headline: c.headline || c.title || 'Developer',
                                        location: c.location,
                                        score: score,
                                        skills: c.skills || [],
                                        github_url: c.github_url || c.github,
                                        github_stars: c.github_stars,
                                        linkedin_url: c.linkedin_url || c.linkedin,
                                        stackoverflow_url: c.stackoverflow_url || c.stackoverflow,
                                        stackoverflow_reputation: c.stackoverflow_reputation,
                                        avatar_url: c.avatar_url,
                                        bio: c.bio || c.summary,
                                        experience: c.experience
                                    };
                                })
                            );

                            setCandidates(mappedCandidates);
                        } catch (error) {
                            console.error('Failed to fetch candidates:', error);
                        }
                    }
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
                    <button
                        className="btn-settings-toggle"
                        onClick={() => setIsSettingsOpen(true)}
                        title="Platform Settings"
                    >
                        ⚙️
                    </button>
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
                {candidates.length > 0 && (
                    <CandidateResults
                        candidates={candidates}
                        onEnrichClick={async (candidate) => {
                            if (!candidate.linkedin_url) {
                                addToast('No LinkedIn URL found for enrichment', 'warning');
                                return;
                            }
                            addToast(`Enriching contact info for ${candidate.name}...`, 'info');
                            try {
                                const enriched = await enrichmentClient.enrichCandidate(candidate.id, candidate.linkedin_url);
                                if (enriched.email || enriched.phone) {
                                    setCandidates(prev => prev.map(c =>
                                        c.id === candidate.id ? { ...c, bio: `${c.bio}\n\n[Enriched info from ${enriched.source}]\nEmail: ${enriched.email}\nPhone: ${enriched.phone}` } : c
                                    ));
                                    addToast(`Enrichment successful for ${candidate.name}!`, 'success');
                                } else {
                                    addToast('No new contact info found.', 'info');
                                }
                            } catch (error) {
                                addToast('Enrichment failed. Check your API keys.', 'error');
                            }
                        }}
                        onOutreachClick={(candidate) => setOutreachCandidate(candidate)}
                        onInterviewClick={(candidate) => {
                            console.log('Schedule interview for:', candidate);
                            addToast(`Interview invitation sent to ${candidate.name}`, 'info');
                        }}
                    />
                )}
            </main>

            {outreachCandidate && (
                <OutreachModal
                    candidate={outreachCandidate}
                    onClose={() => setOutreachCandidate(null)}
                    onSend={(msg, method) => {
                        console.log(`Sending ${method} to ${outreachCandidate.name}:`, msg);
                        addToast(`Outreach sent to ${outreachCandidate.name} via ${method}`, 'success');
                        setOutreachCandidate(null);
                    }}
                />
            )}

            {isSettingsOpen && (
                <SettingsModal
                    currentKeys={apiKeys}
                    onClose={() => setIsSettingsOpen(false)}
                    onSave={(keys) => {
                        setApiKeys(keys);
                        enrichmentClient.setApiKeys(keys);
                        addToast('Settings saved successfully', 'success');
                    }}
                />
            )}

            <footer className="footer">
                <p>🔒 Private recruiting platform. All data processing happens locally.</p>
            </footer>
        </div>
    );
}
