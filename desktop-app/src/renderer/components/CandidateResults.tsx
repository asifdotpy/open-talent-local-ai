import React, { useState } from 'react';

export interface Candidate {
    id: string;
    name: string;
    headline?: string;
    location?: string;
    score: number;
    skills?: string[];
    github_url?: string;
    github_stars?: number;
    linkedin_url?: string;
    stackoverflow_url?: string;
    stackoverflow_reputation?: number;
    avatar_url?: string;
    bio?: string;
    experience?: Array<{
        title: string;
        company: string;
        duration: string;
    }>;
}

interface CandidateResultsProps {
    candidates: Candidate[];
    onInterviewClick?: (candidate: Candidate) => void;
    onOutreachClick?: (candidate: Candidate) => void;
    onEnrichClick?: (candidate: Candidate) => void;
}

export function CandidateResults({ candidates, onInterviewClick, onOutreachClick, onEnrichClick }: CandidateResultsProps) {
    const [sortBy, setSortBy] = useState<'score' | 'name'>('score');
    const [minScore, setMinScore] = useState(0);
    const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

    // Sort and filter candidates
    const filteredCandidates = candidates
        .filter(c => c.score >= minScore)
        .sort((a, b) => {
            if (sortBy === 'score') return b.score - a.score;
            return a.name.localeCompare(b.name);
        });

    const getScoreColor = (score: number): string => {
        if (score >= 80) return 'score-excellent';
        if (score >= 60) return 'score-good';
        if (score >= 40) return 'score-fair';
        return 'score-low';
    };

    return (
        <div className="candidate-results">
            <div className="results-header">
                <h2>
                    Found {filteredCandidates.length} Candidate{filteredCandidates.length !== 1 ? 's' : ''}
                    {minScore > 0 && ` (score ≥ ${minScore})`}
                </h2>

                <div className="controls">
                    <label className="control-item">
                        <span>Sort by:</span>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as 'score' | 'name')}
                        >
                            <option value="score">Score (High to Low)</option>
                            <option value="name">Name (A-Z)</option>
                        </select>
                    </label>

                    <label className="control-item">
                        <span>Min Score: {minScore}</span>
                        <input
                            type="range"
                            min="0"
                            max="100"
                            step="5"
                            value={minScore}
                            onChange={(e) => setMinScore(Number(e.target.value))}
                        />
                    </label>
                </div>
            </div>

            {filteredCandidates.length === 0 ? (
                <div className="no-results">
                    <p>No candidates match your criteria. Try lowering the minimum score.</p>
                </div>
            ) : (
                <div className="candidates-grid">
                    {filteredCandidates.map((candidate) => (
                        <div key={candidate.id} className="candidate-card">
                            <div className="card-header">
                                {candidate.avatar_url ? (
                                    <img
                                        src={candidate.avatar_url}
                                        alt={candidate.name}
                                        className="avatar"
                                    />
                                ) : (
                                    <div className="avatar-placeholder">
                                        {candidate.name.charAt(0).toUpperCase()}
                                    </div>
                                )}

                                <div className="candidate-info">
                                    <h3>{candidate.name}</h3>
                                    {candidate.headline && (
                                        <p className="headline">{candidate.headline}</p>
                                    )}
                                    {candidate.location && (
                                        <p className="location">📍 {candidate.location}</p>
                                    )}
                                </div>

                                <div className={`score-badge ${getScoreColor(candidate.score)}`}>
                                    {candidate.score}
                                </div>
                            </div>

                            {candidate.bio && (
                                <p className="bio">{candidate.bio.substring(0, 150)}...</p>
                            )}

                            {candidate.skills && candidate.skills.length > 0 && (
                                <div className="skills">
                                    {candidate.skills.slice(0, 5).map((skill, idx) => (
                                        <span key={idx} className="skill-tag">
                                            {skill}
                                        </span>
                                    ))}
                                    {candidate.skills.length > 5 && (
                                        <span className="skill-tag more">
                                            +{candidate.skills.length - 5} more
                                        </span>
                                    )}
                                </div>
                            )}

                            <div className="social-links">
                                {candidate.github_url && (
                                    <a
                                        href={candidate.github_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="social-link github"
                                        title="GitHub Profile"
                                    >
                                        <span>⭐</span>
                                        {candidate.github_stars && (
                                            <span className="stat">{candidate.github_stars}</span>
                                        )}
                                    </a>
                                )}
                                {candidate.linkedin_url && (
                                    <a
                                        href={candidate.linkedin_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="social-link linkedin"
                                        title="LinkedIn Profile"
                                    >
                                        in
                                    </a>
                                )}
                                {candidate.stackoverflow_url && (
                                    <a
                                        href={candidate.stackoverflow_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="social-link stackoverflow"
                                        title="Stack Overflow Profile"
                                    >
                                        <span>SO</span>
                                        {candidate.stackoverflow_reputation && (
                                            <span className="stat">
                                                {candidate.stackoverflow_reputation.toLocaleString()}
                                            </span>
                                        )}
                                    </a>
                                )}
                            </div>

                            <div className="card-actions">
                                <button
                                    onClick={() => setSelectedCandidate(candidate)}
                                    className="btn-view"
                                >
                                    View Details
                                </button>
                                {onEnrichClick && (
                                    <button
                                        onClick={() => onEnrichClick(candidate)}
                                        className="btn-view"
                                        style={{ backgroundColor: '#f0f9ff', color: '#0369a1', borderColor: '#bae6fd' }}
                                        title="Find contact info via ContactOut/SalesQL"
                                    ) : (
                                <span>Enrich</span>
                                    )}
                            </button>
                            {onOutreachClick && (
                                <button
                                    onClick={() => onOutreachClick(candidate)}
                                    className="btn-view"
                                    style={{ backgroundColor: '#e0f2fe', color: '#0369a1' }}
                                >
                                    Outreach
                                </button>
                            )}
                            {onInterviewClick && (
                                <button
                                    onClick={() => onInterviewClick(candidate)}
                                    className="btn-interview"
                                >
                                    Schedule Interview
                                </button>
                            )}
                        </div>
                        </div>
            ))}
        </div>
    )
}

{/* Candidate Detail Modal */ }
{
    selectedCandidate && (
        <div className="modal-overlay" onClick={() => setSelectedCandidate(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button
                    className="modal-close"
                    onClick={() => setSelectedCandidate(null)}
                >
                    ✕
                </button>

                <div className="modal-header">
                    {selectedCandidate.avatar_url ? (
                        <img
                            src={selectedCandidate.avatar_url}
                            alt={selectedCandidate.name}
                            className="avatar-large"
                        />
                    ) : (
                        <div className="avatar-placeholder-large">
                            {selectedCandidate.name.charAt(0).toUpperCase()}
                        </div>
                    )}
                    <div>
                        <h2>{selectedCandidate.name}</h2>
                        {selectedCandidate.headline && (
                            <p className="headline">{selectedCandidate.headline}</p>
                        )}
                        <div className={`score-badge-large ${getScoreColor(selectedCandidate.score)}`}>
                            Score: {selectedCandidate.score}/100
                        </div>
                    </div>
                </div>

                {selectedCandidate.bio && (
                    <div className="modal-section">
                        <h3>About</h3>
                        <p>{selectedCandidate.bio}</p>
                    </div>
                )}

                {selectedCandidate.experience && selectedCandidate.experience.length > 0 && (
                    <div className="modal-section">
                        <h3>Experience</h3>
                        {selectedCandidate.experience.map((exp, idx) => (
                            <div key={idx} className="experience-item">
                                <strong>{exp.title}</strong> at {exp.company}
                                <span className="duration">{exp.duration}</span>
                            </div>
                        ))}
                    </div>
                )}

                {selectedCandidate.skills && selectedCandidate.skills.length > 0 && (
                    <div className="modal-section">
                        <h3>Skills</h3>
                        <div className="skills">
                            {selectedCandidate.skills.map((skill, idx) => (
                                <span key={idx} className="skill-tag">
                                    {skill}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
        </div >
    );
}
