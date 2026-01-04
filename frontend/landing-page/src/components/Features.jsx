import React from 'react';
import { Icons } from './Icons';
import { CONFIG } from '../config';

const Features = () => {
  return (
    <section id="features" className="py-24 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Everything You Need to Recruit</h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            One platform replaces your entire recruiting stack
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {CONFIG.features.map((feature, i) => (
            <div key={i} className="card-gradient border border-slate-800 rounded-2xl p-6 hover:border-primary-500/50 transition">
              <div className="w-14 h-14 bg-primary-500/20 rounded-xl flex items-center justify-center text-primary-400 mb-4">
                {i === 0 && <Icons.Search />}
                {i === 1 && <Icons.Bot />}
                {i === 2 && <Icons.Shield />}
                {i === 3 && <Icons.Zap />}
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-slate-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
