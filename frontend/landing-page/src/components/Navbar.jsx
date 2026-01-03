import React, { useState } from 'react';
import { Icons } from './Icons';
import { CONFIG } from '../config';

const Navbar = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const navigateTo = (path, e) => {
        if (e) e.preventDefault();
        window.history.pushState({}, '', path);
        window.dispatchEvent(new PopStateEvent('popstate'));
        setIsMenuOpen(false);
    };

    const handleNavClick = (href, e) => {
        if (href.startsWith('#')) {
            const id = href.substring(1);
            if (window.location.pathname !== '/') {
                navigateTo('/', e);
                // Wait for navigation to home before scrolling
                setTimeout(() => {
                    const element = document.getElementById(id);
                    if (element) element.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            } else {
                if (e) e.preventDefault();
                const element = document.getElementById(id);
                if (element) element.scrollIntoView({ behavior: 'smooth' });
                setIsMenuOpen(false);
            }
        } else {
            navigateTo(href, e);
        }
    };

    return (
        <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-lg border-b border-slate-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <a 
                        href="/" 
                        onClick={(e) => navigateTo('/', e)}
                        className="flex items-center space-x-2 hover:opacity-80 transition cursor-pointer"
                    >
                        <Icons.Logo className="w-8 h-8" />
                        <span className="text-xl font-bold">{CONFIG.project.name}</span>
                    </a>
                    
                    {/* Desktop Menu */}
                    <div className="hidden md:flex items-center space-x-8">
                        {CONFIG.navigation.map((link) => (
                            <a 
                                key={link.name} 
                                href={link.href} 
                                onClick={(e) => handleNavClick(link.href, e)}
                                className="text-slate-300 hover:text-white transition cursor-pointer"
                            >
                                {link.name}
                            </a>
                        ))}
                        <a href={CONFIG.project.githubUrl} target="_blank" rel="noopener noreferrer" className="text-slate-300 hover:text-white transition flex items-center gap-2">
                            <Icons.GitHub /> GitHub
                        </a>
                        <button className="bg-slate-800 text-slate-400 cursor-not-allowed px-4 py-2 rounded-lg font-medium transition flex items-center gap-2">
                            Coming Soon
                        </button>
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden flex items-center">
                        <button 
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="text-slate-300 hover:text-white p-2"
                        >
                            {isMenuOpen ? <Icons.Close /> : <Icons.Menu />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu Overlay */}
            {isMenuOpen && (
                <div className="md:hidden bg-slate-900 border-b border-slate-800 py-4 px-4 space-y-4">
                    {CONFIG.navigation.map((link) => (
                        <a 
                            key={link.name} 
                            href={link.href} 
                            onClick={(e) => handleNavClick(link.href, e)}
                            className="block text-slate-300 hover:text-white transition text-lg cursor-pointer"
                        >
                            {link.name}
                        </a>
                    ))}
                    <a 
                        href={CONFIG.project.githubUrl} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="flex items-center gap-2 text-slate-300 hover:text-white transition text-lg"
                    >
                        <Icons.GitHub /> GitHub
                    </a>
                    <button className="w-full bg-slate-800 text-slate-400 cursor-not-allowed py-3 rounded-lg font-medium text-center">
                        Coming Soon
                    </button>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
