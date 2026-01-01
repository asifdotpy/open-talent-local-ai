import React, { useState } from 'react';
import { Icons } from './Icons';
import { CONFIG } from '../config';

const LegalPages = () => {
    const [activePage, setActivePage] = useState('privacy');

    const privacyContent = `
# OpenTalent Privacy Policy

**Last Updated:** January 1, 2026

## Our Core Privacy Principle

OpenTalent is a desktop-first, privacy-first application. Our core principle is that **your data is your own**. The Service is designed to run 100% locally on your hardware, meaning **no candidate data, interview transcripts, or user-generated content is ever transmitted to our servers or any third-party cloud services.**

## Information We Do Not Collect

Due to the local nature of the Service, we do not collect, store, or process:

- **Candidate Data:** Names, contact information, resumes, interview transcripts, or any other candidate-related data
- **User Content:** Content of your AI interviews, search queries, or internal notes
- **Usage Data (Non-Anonymized):** Your specific activities within the application

## Information We May Collect (Anonymized)

We may collect minimal, anonymized, and aggregated data for improving application stability and performance:

- **Crash Reports:** Anonymized technical reports when the application crashes (you will be prompted to approve)
- **Version Information:** Application version checks for update notifications

## Data Storage and Security

- **Local Storage:** All sensitive data is stored exclusively on your local machine
- **Encryption:** We encourage using OS-level encryption (BitLocker, FileVault) for additional protection
- **Microservices:** All services communicate only locally via internal network interfaces

## Third-Party Services

The Service is designed to minimize third-party reliance. For BYOK (Bring Your Own Key) features, you establish direct connections with third-party providers, and their privacy policies govern the data shared.

## Contact Us

For questions about this Privacy Policy, contact: \`${CONFIG.project.contactEmail}\`
    `;

    const termsContent = `
# OpenTalent Terms of Service

**Last Updated:** January 1, 2026

## Acceptance of Terms

By downloading, installing, or using the OpenTalent desktop application, you agree to be bound by these Terms of Service. If you do not agree, you may not use the Service.

## The Service

OpenTalent is an open-source, desktop-first AI recruitment platform intended for sourcing and interviewing candidates using local AI processing.

## License and Open Source

The core software is licensed under the **MIT License**. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, subject to the MIT License conditions.

## User Responsibilities

You agree to use the Service only for lawful purposes:

- **Data Responsibility:** You are solely responsible for the security, backup, and compliance of locally stored data, including adherence to data protection laws (GDPR, CCPA, etc.)
- **Third-Party Keys:** You are responsible for complying with the terms of service of third-party providers when using the BYOK model

## Disclaimer of Warranties

**THE SERVICE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.**

We do not warrant that the Service will be uninterrupted, error-free, or completely secure. You assume all risk associated with using the Service.

## Limitation of Liability

In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from the software or its use.

## Contact Information

For questions about these Terms, contact: \`${CONFIG.project.contactEmail}\`
    `;

    const renderMarkdown = (text) => {
        return text.split('\n').map((line, i) => {
            if (line.startsWith('# ')) {
                return <h1 key={i} className="text-3xl font-bold mt-8 mb-4">{line.replace('# ', '')}</h1>;
            }
            if (line.startsWith('## ')) {
                return <h2 key={i} className="text-2xl font-bold mt-6 mb-3">{line.replace('## ', '')}</h2>;
            }
            if (line.startsWith('- ')) {
                return <li key={i} className="ml-6 mb-2">{line.replace('- ', '')}</li>;
            }
            if (line.startsWith('**') && line.endsWith('**')) {
                return <p key={i} className="font-semibold mb-2">{line}</p>;
            }
            if (line.trim() === '') {
                return <div key={i} className="h-2"></div>;
            }
            if (line.includes('`')) {
                return <p key={i} className="mb-2"><code className="bg-slate-800 px-2 py-1 rounded">{line}</code></p>;
            }
            return <p key={i} className="mb-2 text-slate-300">{line}</p>;
        });
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white pt-24">
            <div className="max-w-4xl mx-auto px-4 py-12">
                {/* Navigation Tabs */}
                <div className="flex gap-4 mb-12 border-b border-slate-800">
                    <button
                        onClick={() => setActivePage('privacy')}
                        className={`pb-4 px-4 font-semibold transition ${
                            activePage === 'privacy'
                                ? 'border-b-2 border-primary-500 text-white'
                                : 'text-slate-400 hover:text-white'
                        }`}
                    >
                        Privacy Policy
                    </button>
                    <button
                        onClick={() => setActivePage('terms')}
                        className={`pb-4 px-4 font-semibold transition ${
                            activePage === 'terms'
                                ? 'border-b-2 border-primary-500 text-white'
                                : 'text-slate-400 hover:text-white'
                        }`}
                    >
                        Terms of Service
                    </button>
                </div>

                {/* Content */}
                <div className="prose prose-invert max-w-none">
                    {activePage === 'privacy' ? renderMarkdown(privacyContent) : renderMarkdown(termsContent)}
                </div>

                {/* Back to Home */}
                <div className="mt-12 pt-8 border-t border-slate-800">
                    <a href="/" className="inline-flex items-center gap-2 text-primary-400 hover:text-primary-300 transition">
                        ← Back to Home
                    </a>
                </div>
            </div>
        </div>
    );
};

export default LegalPages;
