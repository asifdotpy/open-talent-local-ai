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
            <div className="prompt-container">
                <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe the candidate you're looking for..."
                    disabled={isSearching}
                    className="prompt-textarea"
                />
                <button
                    onClick={handleSearch}
                    disabled={isSearching || !prompt.trim()}
                    className="search-icon-btn"
                    title="Search"
                >
                    {isSearching ? '⏳' : '🔍'}
                </button>
            </div>

            <div className="tools-and-action">
                <div className="tool-selection">
                    <h4>Source Tools</h4>
                    <div className="tools-row">
                        <label className={`tool-checkbox ${selectedTools.github ? 'active' : ''}`}>
                            <input
                                type="checkbox"
                                checked={selectedTools.github}
                                onChange={() => toggleTool('github')}
                                disabled={isSearching}
                            />
                            GitHub (Free)
                        </label>
                        <label className={`tool-checkbox ${selectedTools.stackoverflow ? 'active' : ''}`}>
                            <input
                                type="checkbox"
                                checked={selectedTools.stackoverflow}
                                onChange={() => toggleTool('stackoverflow')}
                                disabled={isSearching}
                            />
                            Stack Overflow (Free)
                        </label>
                        <label className={`tool-checkbox ${selectedTools.googleXray ? 'active' : ''}`}>
                            <input
                                type="checkbox"
                                checked={selectedTools.googleXray}
                                onChange={() => toggleTool('googleXray')}
                                disabled={isSearching}
                            />
                            Google X-Ray (Free)
                        </label>
                        <label className={`tool-checkbox ${selectedTools.contactout ? 'active' : ''}`}>
                            <input
                                type="checkbox"
                                checked={selectedTools.contactout}
                                onChange={() => toggleTool('contactout')}
                                disabled={isSearching}
                            />
                            ContactOut (Paid)
                        </label>
                        <label className={`tool-checkbox ${selectedTools.salesql ? 'active' : ''}`}>
                            <input
                                type="checkbox"
                                checked={selectedTools.salesql}
                                onChange={() => toggleTool('salesql')}
                                disabled={isSearching}
                            />
                            SalesQL (Paid)
                        </label>
                    </div>
                </div>

                <button
                    onClick={handleSearch}
                    disabled={isSearching || !prompt.trim()}
                    className="search-btn-large"
                >
                    {isSearching ? 'Searching...' : 'Search Candidates'}
                </button>
            </div>

            {isSearching && (
                <div className="search-info">
                    <span>🔍</span>
                    <span>Scanning for candidates across selected platforms...</span>
                </div>
            )}
        </div>
    );
}
