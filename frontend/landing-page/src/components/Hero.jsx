import React from 'react';
import { Link } from 'react-router-dom';
import { Icons } from './Icons';
import { CONFIG } from '../config';

const Hero = () => {
    return (
        <section className="hero-gradient pt-32 pb-20 px-4 relative overflow-hidden">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-50"></div>
            <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center relative">
                <div className="text-center md:text-left">
                    <div className="inline-flex items-center gap-2 bg-slate-800/50 border border-slate-700 rounded-full px-4 py-2 mb-8">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        <span className="text-sm text-slate-300">Now Open Source</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
                        All-in-One Recruiting<br />
                        <span className="gradient-text">{CONFIG.project.tagline}</span>
                    </h1>

                    <p className="text-xl text-slate-300 max-w-xl mx-auto md:mx-0 mb-10">
                        {CONFIG.project.description}
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start mb-12">
                        <Link to="/download" className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition flex items-center justify-center gap-3">
                            Download Now
                        </Link>
                        <a href={CONFIG.project.githubUrl} target="_blank" rel="noopener noreferrer" className="bg-slate-800 hover:bg-slate-700 border border-slate-700 px-8 py-4 rounded-xl font-semibold text-lg transition flex items-center justify-center gap-3">
                            <Icons.GitHub /> View on GitHub
                        </a>
                    </div>

                    <div className="flex flex-wrap justify-center md:justify-start gap-8 text-slate-400">
                        <div className="flex items-center gap-2">
                            <Icons.Check />
                            <span>GDPR Compliant</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Icons.Check />
                            <span>Local AI Processing</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Icons.Check />
                            <span>Open Source</span>
                        </div>
                    </div>
                </div>
                <div className="hidden md:block">
                    <div className="w-full h-96 bg-slate-800/50 rounded-2xl border border-slate-700 flex items-center justify-center">
                        <p className="text-slate-500">Product screenshot coming soon</p>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
