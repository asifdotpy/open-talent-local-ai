import React from 'react';

const Blog = () => {
    return (
        <section id="blog" className="py-24 px-4 bg-slate-900/30">
            <div className="max-w-4xl mx-auto text-white">
                <h2 className="text-4xl font-extrabold mb-8 text-center">
                    Why OpenTalent is the Future of <span className="gradient-text">Local AI Recruitment</span>
                </h2>
                
                <div className="space-y-8 text-lg text-slate-300">
                    <p>
                        In an era where data privacy is paramount, the recruitment industry faces a critical challenge: how to leverage powerful **AI tools** without compromising candidate confidentiality or incurring massive cloud costs. **OpenTalent** provides the definitive answer. It is the first desktop-first, **open-source AI recruitment platform** designed for complete privacy and control. By keeping all data and processing local, OpenTalent ensures that sensitive hiring information never leaves your machine.
                    </p>

                    <h3 className="text-2xl font-bold text-white pt-4">
                        The Power of 100% Local AI
                    </h3>
                    <p>
                        OpenTalent is powered by **local AI engines**, specifically leveraging the power of Ollama with models like Granite 4. This architecture allows for **offline interview processing** and candidate evaluation, eliminating the need for expensive, data-leaking cloud APIs. For recruiters and HR professionals, this means a **97% cost saving** compared to traditional cloud-based solutions like LinkedIn Recruiter and HireVue, while achieving full **GDPR and CCPA compliance** by design.
                    </p>

                    <h3 className="text-2xl font-bold text-white pt-4">
                        Key Features for Modern Talent Acquisition
                    </h3>
                    <p>
                        The platform is built on a robust microservices architecture, providing a unified gateway to several powerful features:
                    </p>
                    
                    <ul className="list-disc list-inside space-y-3 pl-6">
                        <li>
                            **Privacy-First Sourcing:** Access to over 1.8 billion profiles through multi-platform sourcing, all managed locally.
                        </li>
                        <li>
                            **AI-Led Interviews:** Conduct structured, consistent interviews using local LLMs, ensuring fair and unbiased candidate evaluation.
                        </li>
                        <li>
                            **Voice Intelligence:** Integrated local Text-to-Speech (TTS) and Speech-to-Text (STT) for immersive, AI-driven conversations.
                        </li>
                        <li>
                            **Open Source & Extensible:** Built with a modern stack (Electron, React, Python microservices), making it easy for developers to contribute and customize.
                        </li>
                    </ul>

                    <h3 className="text-2xl font-bold text-white pt-4">
                        Getting Started with OpenTalent
                    </h3>
                    <p>
                        Whether you are an executive seeking a cost-effective, compliant solution, or a developer looking to contribute to the future of **open-source recruitment software**, OpenTalent offers a clear path. The entire platform can be started with a single command using the provided `manage.sh` script, making deployment simple even for non-technical users. Join the movement towards **privacy-first hiring** and discover how **local AI** can transform your talent acquisition strategy.
                    </p>

                    <div className="mt-10 p-6 border border-primary-500/50 rounded-xl bg-slate-800/50">
                        <h4 className="text-xl font-bold text-primary-400 mb-2">SEO Keywords for Ranking:</h4>
                        <p className="text-sm text-slate-400">
                            **Local AI Recruitment**, **Open Source AI Recruitment Platform**, **Privacy-First Hiring**, **Offline Interview Processing**, **AI Tools for HR**, **Recruitment Software**, **Ollama AI**, **GDPR Compliant Recruitment**, **Talent Acquisition Software**.
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Blog;
