import React, { useState, useEffect } from 'react';
import { CONFIG } from '../config';

const LegalPages = () => {
    const [activePage, setActivePage] = useState('privacy');

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const page = params.get('page');
        if (page === 'terms') setActivePage('terms');
    }, []);

    const PrivacyContent = () => (
        <div className="space-y-8">
            <header className="border-b border-slate-800 pb-8">
                <h1 className="text-4xl font-bold text-white mb-4">Privacy Policy</h1>
                <p className="text-slate-400">Last Updated: January 1, 2026</p>
            </header>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">Our Core Privacy Principle</h2>
                <p className="text-slate-300 leading-relaxed">
                    OpenTalent is a desktop-first, privacy-first application. Our core principle is that <strong className="text-primary-400">your data is your own</strong>. The Service is designed to run 100% locally on your hardware, meaning no candidate data, interview transcripts, or user-generated content is ever transmitted to our servers or any third-party cloud services for processing or storage.
                </p>
            </section>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">Information We Do Not Collect</h2>
                <p className="text-slate-300 mb-4">Due to the local nature of the Service, we do not collect, store, or process the following types of information:</p>
                <ul className="space-y-3 text-slate-300">
                    <li className="flex gap-3">
                        <span className="text-primary-500 font-bold">•</span>
                        <span><strong>Candidate Data:</strong> We do not collect names, contact information, resumes, interview transcripts, or any other data related to the candidates you source or interview.</span>
                    </li>
                    <li className="flex gap-3">
                        <span className="text-primary-500 font-bold">•</span>
                        <span><strong>User Content:</strong> We do not collect or view the content of your AI interviews, search queries, or internal notes.</span>
                    </li>
                    <li className="flex gap-3">
                        <span className="text-primary-500 font-bold">•</span>
                        <span><strong>Usage Data:</strong> We do not track your specific activities within the application.</span>
                    </li>
                </ul>
            </section>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">Information We May Collect (Anonymized)</h2>
                <p className="text-slate-300 mb-4">We may collect minimal, anonymized data for the sole purpose of improving stability:</p>
                <ul className="space-y-3 text-slate-300">
                    <li className="flex gap-3">
                        <span className="text-primary-500 font-bold">•</span>
                        <span><strong>Crash Reports:</strong> Anonymized technical reports generated during a crash (requires your approval).</span>
                    </li>
                    <li className="flex gap-3">
                        <span className="text-primary-500 font-bold">•</span>
                        <span><strong>Version Information:</strong> Checks for available updates to keep your application secure.</span>
                    </li>
                </ul>
            </section>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">Data Storage and Security</h2>
                <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                        <h3 className="text-lg font-medium text-white mb-2">Local Storage</h3>
                        <p className="text-slate-400 text-sm">All sensitive data is stored exclusively on your local machine, typically within your user directory.</p>
                    </div>
                    <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                        <h3 className="text-lg font-medium text-white mb-2">Microservices</h3>
                        <p className="text-slate-400 text-sm">Internal services communicate only via local network interfaces, ensuring no data leakage.</p>
                    </div>
                </div>
            </section>

            <section className="bg-primary-500/10 p-8 rounded-2xl border border-primary-500/20">
                <h2 className="text-2xl font-semibold text-white mb-4">Contact Us</h2>
                <p className="text-slate-300">
                    If you have any questions about this Privacy Policy, please contact us at: 
                    <code className="ml-2 bg-slate-800 px-2 py-1 rounded text-primary-300">{CONFIG.project.contactEmail}</code>
                </p>
            </section>
        </div>
    );

    const TermsContent = () => (
        <div className="space-y-8">
            <header className="border-b border-slate-800 pb-8">
                <h1 className="text-4xl font-bold text-white mb-4">Terms of Service</h1>
                <p className="text-slate-400">Last Updated: January 1, 2026</p>
            </header>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">1. Acceptance of Terms</h2>
                <p className="text-slate-300 leading-relaxed">
                    By downloading, installing, or using the OpenTalent desktop application, you agree to be bound by these Terms of Service. If you do not agree to these Terms, you may not use the Service.
                </p>
            </section>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">2. License and Open Source</h2>
                <p className="text-slate-300 mb-4">
                    The core software of OpenTalent is licensed under the <strong className="text-primary-400">MIT License</strong>. You are free to use, copy, modify, and distribute the software subject to the conditions outlined in the license.
                </p>
            </section>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">3. User Responsibilities</h2>
                <ul className="space-y-4 text-slate-300">
                    <li className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                        <strong className="text-white block mb-2">Data Responsibility</strong>
                        You are solely responsible for the security, backup, and compliance of locally stored data, including adherence to GDPR, CCPA, and other applicable laws.
                    </li>
                    <li className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                        <strong className="text-white block mb-2">Third-Party Keys</strong>
                        You are responsible for complying with the terms of service of third-party providers when using the "Bring Your Own Key" (BYOK) model.
                    </li>
                </ul>
            </section>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">4. Disclaimer of Warranties</h2>
                <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-xl text-slate-300 italic">
                    "THE SERVICE IS PROVIDED 'AS IS,' WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT."
                </div>
            </section>

            <section>
                <h2 className="text-2xl font-semibold text-white mb-4">5. Limitation of Liability</h2>
                <p className="text-slate-300 leading-relaxed">
                    In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from, out of, or in connection with the software or the use of the software.
                </p>
            </section>

            <section className="bg-primary-500/10 p-8 rounded-2xl border border-primary-500/20">
                <h2 className="text-2xl font-semibold text-white mb-4">Contact Information</h2>
                <p className="text-slate-300">
                    For questions about these Terms, please contact us at: 
                    <code className="ml-2 bg-slate-800 px-2 py-1 rounded text-primary-300">{CONFIG.project.contactEmail}</code>
                </p>
            </section>
        </div>
    );

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
                <div className="animate-in fade-in duration-500">
                    {activePage === 'privacy' ? <PrivacyContent /> : <TermsContent />}
                </div>

                {/* Back to Home */}
                <div className="mt-16 pt-8 border-t border-slate-800">
                    <a 
                        href="/" 
                        onClick={(e) => {
                            e.preventDefault();
                            window.history.pushState({}, '', '/');
                            window.dispatchEvent(new PopStateEvent('popstate'));
                        }}
                        className="inline-flex items-center gap-2 text-primary-400 hover:text-primary-300 transition font-medium"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        Back to Home
                    </a>
                </div>
            </div>
        </div>
    );
};

export default LegalPages;
