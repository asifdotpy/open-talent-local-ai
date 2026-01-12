import React from 'react';
import Hero from '../components/Hero';
import Stats from '../components/Stats';

import { Icons } from '../components/Icons';
import { CONFIG } from '../config';

const Home = () => {
    return (
        <>
            <Hero />
            <Stats />
            {/* CTA Section */}
            <section className="py-24 px-4 hero-gradient">
                <div className="max-w-4xl mx-auto text-center">
                    <h2 className="text-4xl font-bold mb-4">Ready to Transform Your Recruiting?</h2>
                    <p className="text-xl text-slate-300 mb-8">
                        Join recruiters saving $1,500+/month with privacy-first hiring.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <button className="bg-white text-slate-900 cursor-not-allowed px-8 py-4 rounded-xl font-semibold text-lg transition flex items-center justify-center gap-3">
                            Coming Soon
                        </button>
                        <a href={CONFIG.project.githubUrl} target="_blank" rel="noopener noreferrer" className="border border-white/30 hover:bg-white/10 px-8 py-4 rounded-xl font-semibold text-lg transition flex items-center justify-center gap-3">
                            <Icons.GitHub /> Star on GitHub
                        </a>
                    </div>
                </div>
            </section>
        </>
    );
};

export default Home;
