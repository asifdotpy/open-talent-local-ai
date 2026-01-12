import React from 'react';
import { Icons } from './Icons';
import { CONFIG } from '../config';

const Download = () => {
  return (
    <section id="download" className="py-24 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-4">Download OpenTalent</h2>
        <p className="text-xl text-slate-400 mb-12">
          Available for Windows, macOS, and Linux. Free forever on the Free tier.
        </p>

        <div className="grid md:grid-cols-3 gap-6">
          {Object.entries(CONFIG.downloads).map(([key, platform]) => (
            <div key={key} className="flex flex-col items-center gap-4 border border-slate-800 rounded-2xl p-8 bg-slate-900/50 opacity-75">
              {key === 'windows' && <Icons.Windows />}
              {key === 'macos' && <Icons.Apple />}
              {key === 'linux' && <Icons.Linux />}
              <div>
                <div className="font-semibold text-lg">{platform.name}</div>
                <div className="text-slate-400 text-sm">{platform.version}</div>
              </div>
              <span className="text-slate-500 text-sm font-medium">{platform.status}</span>
            </div>
          ))}
        </div>

        <p className="mt-8 text-slate-500">
          Or build from source: <a href={CONFIG.project.githubUrl} target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:underline">github.com/asifdotpy/open-talent-local-ai</a>
        </p>
      </div>
    </section>
  );
};

export default Download;
