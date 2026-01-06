import React from 'react';
import { Icons } from './Icons';
import { CONFIG } from '../config';

const Footer = () => {
    return (
        <footer className="py-12 px-4 border-t border-slate-800">
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="flex items-center gap-2">
                    <Icons.Logo className="w-8 h-8" />
                    <span className="text-xl font-bold">{CONFIG.project.name}</span>
                </div>
                <div className="flex items-center gap-6 text-slate-400">
                    <a href={CONFIG.project.githubUrl} target="_blank" rel="noopener noreferrer" className="hover:text-white transition flex items-center gap-2">
                        <Icons.GitHub /> GitHub
                    </a>
                    <a href={`mailto:${CONFIG.project.contactEmail}`} className="hover:text-white transition">Contact</a>
                    <a href="/legal?page=privacy" className="hover:text-white transition">Privacy</a>
                    <a href="/legal?page=terms" className="hover:text-white transition">Terms</a>
                </div>
                <div className="text-slate-500 text-sm">
                    © 2025 {CONFIG.project.name}. Open Source under MIT.
                </div>
            </div>
        </footer>
    );
};

export default Footer;
