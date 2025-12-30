import React, { useState } from 'react';

interface SearchPromptProps {
    onSearch: (data: { prompt: string; tools: string[] }) => void;
    isSearching: boolean;
}

interface ToolSelectionState {
    github: boolean;
    stackoverflow: boolean;
    googleXray: boolean;
    contactout: boolean;
    salesql: boolean;
}

export function SearchPrompt({ onSearch, isSearching }: SearchPromptProps) {
    const [prompt, setPrompt] = useState('');
    const [selectedTools, setSelectedTools] = useState<ToolSelectionState>({
        github: true,
        stackoverflow: true,
        googleXray: true,
        contactout: false,
        salesql: false
    });

    const handleSearch = () => {
        if (!prompt.trim()) return;

        const enabledTools = Object.entries(selectedTools)
            .filter(([_, enabled]) => enabled)
            .map(([tool, _]) => tool);

        onSearch({
            prompt: prompt.trim(),
            tools: enabledTools
        });
    };

    const toggleTool = (tool: keyof ToolSelectionState) => {
        setSelectedTools(prev => ({
            ...prev,
            [tool]: !prev[tool]
        }));
    };

    return (
        <div className="search-prompt">
            <h2>🔍 Find Your Next Hire</h2>

            <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the candidate you're looking for... (e.g., 'Senior React developer in NYC with 5+ years experience in fintech')"
                rows={4}
                disabled={isSearching}
                className="prompt-textarea"
            />

            <div className="tool-selection">
                <h4>Search Tools</h4>

                <div className="tools-grid">
                    <label className="tool-checkbox">
                        <input
                            type="checkbox"
                            checked={selectedTools.github}
                            onChange={() => toggleTool('github')}
                            disabled={isSearching}
                        />
                        <span className="tool-name">
                            GitHub <span className="badge free">Free</span>
                        </span>
                        <span className="tool-desc">500M+ developer profiles</span>
                    </label>

                    <label className="tool-checkbox">
                        <input
                            type="checkbox"
                            checked={selectedTools.stackoverflow}
                            onChange={() => toggleTool('stackoverflow')}
                            disabled={isSearching}
                        />
                        <span className="tool-name">
                            Stack Overflow <span className="badge free">Free</span>
                        </span>
                        <span className="tool-desc">20M+ technical profiles</span>
                    </label>

                    <label className="tool-checkbox">
                        <input
                            type="checkbox"
                            checked={selectedTools.googleXray}
                            onChange={() => toggleTool('googleXray')}
                            disabled={isSearching}
                        />
                        <span className="tool-name">
                            Google X-Ray <span className="badge free">Free</span>
                        </span>
                        <span className="tool-desc">Public LinkedIn search</span>
                    </label>

                    <label className="tool-checkbox">
                        <input
                            type="checkbox"
                            checked={selectedTools.contactout}
                            onChange={() => toggleTool('contactout')}
                            disabled={isSearching}
                        />
                        <span className="tool-name">
                            ContactOut <span className="badge paid">$0.04/profile</span>
                        </span>
                        <span className="tool-desc">800M+ verified contacts</span>
                    </label>

                    <label className="tool-checkbox">
                        <input
                            type="checkbox"
                            checked={selectedTools.salesql}
                            onChange={() => toggleTool('salesql')}
                            disabled={isSearching}
                        />
                        <span className="tool-name">
                            SalesQL <span className="badge paid">$0.02/profile</span>
                        </span>
                        <span className="tool-desc">500M+ B2B contacts</span>
                    </label>
                </div>
            </div>

            <button
                onClick={handleSearch}
                disabled={isSearching || !prompt.trim()}
                className={`search-btn ${isSearching ? 'loading' : ''}`}
            >
                {isSearching ? (
                    <>
                        <span className="spinner">⏳</span> Searching...
                    </>
                ) : (
                    <>
                        <span className="icon">🚀</span> Search Candidates
                    </>
                )}
            </button>

            {isSearching && (
                <div className="search-info">
                    <p>🔎 Your search is running in the background. Results will appear below.</p>
                </div>
            )}
        </div>
    );
}
