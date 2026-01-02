import React from 'react';

const Blog = () => {
    return (
        <section id="blog" className="py-24 px-4 bg-slate-900/30">
            <div className="max-w-4xl mx-auto text-white">
                <header className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-extrabold mb-6 leading-tight">
                        Why OpenTalent is the Future of <span className="gradient-text">Local AI Recruitment</span>
                    </h2>
                    <div className="w-24 h-1 bg-primary-500 mx-auto rounded-full"></div>
                </header>

                <div className="prose prose-invert prose-slate max-w-none space-y-12 text-lg text-slate-300 leading-relaxed">
                    <article>
                        <p className="first-letter:text-5xl first-letter:font-bold first-letter:text-white first-letter:mr-3 first-letter:float-left">
                            In an era where data privacy is paramount, the recruitment industry faces a critical challenge: how to leverage powerful AI tools without compromising candidate confidentiality or incurring massive cloud costs. OpenTalent provides the definitive answer. It is the first desktop-first, open-source AI recruitment platform designed for complete privacy and control. By keeping all data and processing local, OpenTalent ensures that sensitive hiring information never leaves your machine.
                        </p>
                    </article>

                    <article className="space-y-4">
                        <h3 className="text-3xl font-bold text-white">
                            The Power of 100% Local AI
                        </h3>
                        <p>
                            OpenTalent is powered by local AI engines, specifically leveraging the power of Ollama with models like Granite 4. This architecture allows for offline interview processing and candidate evaluation, eliminating the need for expensive, data-leaking cloud APIs. For recruiters and HR professionals, this means a 97% cost saving compared to traditional cloud-based solutions like LinkedIn Recruiter and HireVue, while achieving full GDPR and CCPA compliance by design.
                        </p>
                    </article>

                    <article className="space-y-6">
                        <h3 className="text-3xl font-bold text-white">
                            Key Features for Modern Talent Acquisition
                        </h3>
                        <p>
                            The platform is built on a robust microservices architecture, providing a unified gateway to several powerful features:
                        </p>

                        <div className="grid md:grid-cols-2 gap-6 not-prose">
                            {[
                                {
                                    title: "Privacy-First Sourcing",
                                    desc: "Access to over 1.8 billion profiles through multi-platform sourcing, all managed locally."
                                },
                                {
                                    title: "AI-Led Interviews",
                                    desc: "Conduct structured, consistent interviews using local LLMs, ensuring fair and unbiased candidate evaluation."
                                },
                                {
                                    title: "Voice Intelligence",
                                    desc: "Integrated local Text-to-Speech (TTS) and Speech-to-Text (STT) for immersive, AI-driven conversations."
                                },
                                {
                                    title: "Open Source & Extensible",
                                    desc: "Built with a modern stack (Electron, React, Python microservices), making it easy for developers to contribute and customize."
                                }
                            ].map((item, i) => (
                                <div key={i} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-primary-500/50 transition-colors">
                                    <h4 className="text-xl font-bold text-white mb-2">{item.title}</h4>
                                    <p className="text-slate-400 text-sm leading-relaxed">{item.desc}</p>
                                </div>
                            ))}
                        </div>
                    </article>

                    <article className="space-y-4">
                        <h3 className="text-3xl font-bold text-white">
                            Getting Started with OpenTalent
                        </h3>
                        <p>
                            Whether you are an executive seeking a cost-effective, compliant solution, or a developer looking to contribute to the future of open-source recruitment software, OpenTalent offers a clear path. The entire platform can be started with a single command using the provided manage.sh script, making deployment simple even for non-technical users. Join the movement towards privacy-first hiring and discover how local AI can transform your talent acquisition strategy.
                        </p>
                    </article>
                </div>
            </div>
        </section>
    );
};

export default Blog;
