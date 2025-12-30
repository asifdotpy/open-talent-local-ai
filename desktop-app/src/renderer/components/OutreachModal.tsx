import React, { useState, useEffect } from 'react';
import { Candidate } from './CandidateResults';

interface OutreachModalProps {
    candidate: Candidate;
    onClose: () => void;
    onSend: (message: string, method: 'email' | 'whatsapp') => void;
}

export function OutreachModal({ candidate, onClose, onSend }: OutreachModalProps) {
    const [method, setMethod] = useState<'email' | 'whatsapp'>('email');
    const [subject, setSubject] = useState('');
    const [message, setMessage] = useState('');

    const templates = {
        email: {
            subject: `Exciting opportunity: {{job_title}} at OpenTalent`,
            body: `Hi {{candidate_name}},\n\nI was impressed by your profile and your background in {{skills}}. We're currently looking for a {{job_title}} and I think you'd be a great fit.\n\nWould you be open to a brief chat this week?\n\nBest regards,\n[Recruiter Name]`
        },
        whatsapp: {
            subject: '',
            body: `Hi {{candidate_name}}! This is [Recruiter Name] from OpenTalent. I came across your profile and was really impressed with your experience. We're looking for a {{job_title}} - would you be interested in learning more?`
        }
    };

    useEffect(() => {
        const template = templates[method];
        const jobTitle = "Software Engineer"; // Fallback or get from context
        const skills = candidate.skills?.slice(0, 3).join(', ') || 'software development';

        const filledBody = template.body
            .replace('{{candidate_name}}', candidate.name)
            .replace('{{job_title}}', jobTitle)
            .replace('{{skills}}', skills);

        const filledSubject = template.subject
            .replace('{{candidate_name}}', candidate.name)
            .replace('{{job_title}}', jobTitle);

        setSubject(filledSubject);
        setMessage(filledBody);
    }, [method, candidate]);

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content outreach-modal" onClick={e => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>✕</button>

                <div className="outreach-header">
                    <h2>Reach out to {candidate.name}</h2>
                    <div className="method-toggle">
                        <button
                            className={method === 'email' ? 'active' : ''}
                            onClick={() => setMethod('email')}
                        >
                            📧 Email
                        </button>
                        <button
                            className={method === 'whatsapp' ? 'active' : ''}
                            onClick={() => setMethod('whatsapp')}
                        >
                            💬 WhatsApp
                        </button>
                    </div>
                </div>

                <div className="outreach-form">
                    {method === 'email' && (
                        <div className="form-group">
                            <label>Subject</label>
                            <input
                                type="text"
                                value={subject}
                                onChange={e => setSubject(e.target.value)}
                            />
                        </div>
                    )}
                    <div className="form-group">
                        <label>Message</label>
                        <textarea
                            value={message}
                            onChange={e => setMessage(e.target.value)}
                            rows={10}
                        />
                    </div>
                </div>

                <div className="outreach-footer">
                    <button className="btn-cancel" onClick={onClose}>Cancel</button>
                    <button
                        className="btn-send"
                        onClick={() => onSend(message, method)}
                    >
                        Send via {method === 'email' ? 'Email' : 'WhatsApp'}
                    </button>
                </div>
            </div>
        </div>
    );
}
