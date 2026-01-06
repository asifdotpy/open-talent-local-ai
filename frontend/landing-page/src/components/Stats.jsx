import React from 'react';

const Stats = () => {
  return (
    <section className="py-16 bg-slate-900/50 border-y border-slate-800">
      <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
        <div>
          <div className="text-4xl font-bold gradient-text">1.8B+</div>
          <div className="text-slate-400 mt-2">Profiles Accessible</div>
        </div>
        <div>
          <div className="text-4xl font-bold gradient-text">97%</div>
          <div className="text-slate-400 mt-2">Cost Savings</div>
        </div>
        <div>
          <div className="text-4xl font-bold gradient-text">100%</div>
          <div className="text-slate-400 mt-2">Local Privacy</div>
        </div>
        <div>
          <div className="text-4xl font-bold gradient-text">11</div>
          <div className="text-slate-400 mt-2">Microservices</div>
        </div>
      </div>
    </section>
  );
};

export default Stats;
