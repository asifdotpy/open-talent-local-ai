import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Icons } from './Icons';
import { CONFIG } from '../config';

const Navbar = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <header className="sticky top-0 z-50 w-full bg-slate-950/80 backdrop-blur-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <Link to="/" className="flex items-center gap-2">
                        <Icons.Logo />
                        <span className="text-xl font-bold">{CONFIG.project.name}</span>
                    </Link>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center gap-6 text-slate-300">
                        {CONFIG.navLinks.map((link) => (
                            <Link
                                key={link.href}
                                to={link.href}
                                className="hover:text-white transition"
                            >
                                {link.label}
                            </Link>
                        ))}
                    </nav>

                    <div className="hidden md:flex items-center gap-4">
                        <a
                            href={CONFIG.project.githubUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-slate-400 hover:text-white transition"
                        >
                            <Icons.GitHub />
                        </a>
                        <button className="bg-slate-800 text-slate-400 cursor-not-allowed px-4 py-2 rounded-lg font-medium transition">
                            Coming Soon
                        </button>
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden">
                        <button onClick={() => setIsMenuOpen(!isMenuOpen)}>
                            {isMenuOpen ? <Icons.X /> : <Icons.Menu />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
                <div className="md:hidden bg-slate-900/90">
                    <nav className="flex flex-col gap-4 px-4 py-6 text-slate-300">
                        {CONFIG.navLinks.map((link) => (
                            <Link
                                key={link.href}
                                to={link.href}
                                className="hover:text-white transition"
                                onClick={() => setIsMenuOpen(false)}
                            >
                                {link.label}
                            </Link>
                        ))}
                        <a
                            href={CONFIG.project.githubUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-slate-400 hover:text-white transition"
                        >
                            <Icons.GitHub /> GitHub
                        </a>
                        <button className="bg-slate-800 text-slate-400 cursor-not-allowed px-4 py-2 rounded-lg font-medium transition w-full">
                            Coming Soon
                        </button>
                    </nav>
                </div>
            )}
        </header>
    );
};

export default Navbar;
