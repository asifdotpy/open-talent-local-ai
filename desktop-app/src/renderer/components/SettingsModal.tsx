import React, { useState } from 'react';

interface SettingsModalProps {
    onClose: () => void;
    onSave: (keys: { contactOut?: string; salesQL?: string }) => void;
    currentKeys: { contactOut?: string; salesQL?: string };
}

export function SettingsModal({ onClose, onSave, currentKeys }: SettingsModalProps) {
    const [contactOutKey, setContactOutKey] = useState(currentKeys.contactOut || '');
    const [salesQLKey, setSalesQLKey] = useState(currentKeys.salesQL || '');

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content settings-modal" onClick={e => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>✕</button>

                <div className="settings-header">
                    <h2>Platform Settings</h2>
                    <p>Configure your API keys for candidate enrichment and outreach.</p>
                </div>

                <div className="settings-form">
                    <div className="settings-section">
                        <h3>Paid API Integrations</h3>
                        <div className="form-group">
                            <label>ContactOut API Key</label>
                            <input
                                type="password"
                                placeholder="Enter ContactOut Key"
                                value={contactOutKey}
                                onChange={e => setContactOutKey(e.target.value)}
                            />
                            <p className="field-hint">Used for high-accuracy email and phone number discovery.</p>
                        </div>

                        <div className="form-group">
                            <label>SalesQL API Key</label>
                            <input
                                type="password"
                                placeholder="Enter SalesQL Key"
                                value={salesQLKey}
                                onChange={e => setSalesQLKey(e.target.value)}
                            />
                            <p className="field-hint">Used as a secondary/fallback enrichment source.</p>
                        </div>
                    </div>

                    <div className="settings-section">
                        <h3>General Preferences</h3>
                        <div className="form-group">
                            <label>Default Outreach Method</label>
                            <select defaultValue="email">
                                <option value="email">Email</option>
                                <option value="whatsapp">WhatsApp</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div className="settings-footer">
                    <button className="btn-cancel" onClick={onClose}>Cancel</button>
                    <button
                        className="btn-send"
                        onClick={() => {
                            onSave({ contactOut: contactOutKey, salesQL: salesQLKey });
                            onClose();
                        }}
                    >
                        Save Settings
                    </button>
                </div>
            </div>
        </div>
    );
}
