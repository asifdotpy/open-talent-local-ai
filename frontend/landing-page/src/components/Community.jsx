import React from 'react';
import { Icons } from './Icons';
import { CONFIG } from '../config';

const Community = () => {
  return (
    <section id="community" className="py-24 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Join the Community</h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Our project is open-source and community-driven. Join us on our journey to build the future of recruitment.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <a href={CONFIG.project.githubUrl} target="_blank" rel="noopener noreferrer" className="card-gradient border border-slate-800 rounded-2xl p-6 hover:border-primary-500/50 transition flex items-center gap-4">
                <Icons.GitHub />
                <div>
                    <h3 className="text-xl font-semibold mb-2">GitHub</h3>
                    <p className="text-slate-400">Contribute to the codebase, report bugs, and suggest new features.</p>
                </div>
            </a>
            <a href="#" className="card-gradient border border-slate-800 rounded-2xl p-6 hover:border-primary-500/50 transition flex items-center gap-4">
                <Icons.Bot />
                <div>
                    <h3 className="text-xl font-semibold mb-2">Discord</h3>
                    <p className="text-slate-400">Join our community of developers and recruiters to chat and get support.</p>
                </div>
            </a>
            <a href="#" className="card-gradient border border-slate-800 rounded-2xl p-6 hover:border-primary-500/50 transition flex items-center gap-4">
                <Icons.Search />
                <div>
                    <h3 className="text-xl font-semibold mb-2">Twitter</h3>
                    <p className="text-slate-400">Follow us on Twitter for the latest news and updates.</p>
                </div>
            </a>
        </div>
      </div>
    </section>
  );
};

export default Community;
