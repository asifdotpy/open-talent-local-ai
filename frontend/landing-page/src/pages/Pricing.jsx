import React, { useState } from 'react';
import { CONFIG } from '../config';
import { Icons } from '../components/Icons';

const PricingPage = () => {
    const [activeTab, setActiveTab] = useState('monthly');

    return (
        <section id="pricing" className="py-24 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-8">
                        Start free, scale as you grow. No hidden fees.
                    </p>
                    <div className="inline-flex bg-slate-800 rounded-lg p-1">
                        <button
                            onClick={() => setActiveTab('monthly')}
                            className={`px-4 py-2 rounded-md transition ${activeTab === 'monthly' ? 'bg-primary-600' : ''}`}
                        >
                            Monthly
                        </button>
                        <button
                            onClick={() => setActiveTab('yearly')}
                            className={`px-4 py-2 rounded-md transition ${activeTab === 'yearly' ? 'bg-primary-600' : ''}`}
                        >
                            Yearly <span className="text-xs text-green-400 ml-1">Save 17%</span>
                        </button>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                    {/* Free Tier */}
                    <div className="border border-slate-800 rounded-2xl p-8 bg-slate-900/50">
                        <div className="text-lg font-semibold text-slate-400 mb-2">Free</div>
                        <div className="text-4xl font-bold mb-4">$0<span className="text-lg text-slate-400">/mo</span></div>
                        <p className="text-slate-400 mb-6">Perfect for trying out OpenTalent</p>
                        <ul className="space-y-3 mb-8">
                            {['50 sourced profiles/month', '10 AI interviews/month', 'X-Ray search only', 'Community support'].map((item, i) => (
                                <li key={i} className="flex items-center gap-2 text-slate-300">
                                    <Icons.Check /> {item}
                                </li>
                            ))}
                        </ul>
                        <button className="w-full bg-slate-800 text-slate-400 cursor-not-allowed py-3 rounded-lg font-medium transition">
                            Coming Soon
                        </button>
                    </div>

                    {/* Pro Tier */}
                    <div className="border-2 border-primary-500 rounded-2xl p-8 bg-slate-900/50 relative">
                        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary-600 text-sm px-3 py-1 rounded-full">
                            Most Popular
                        </div>
                        <div className="text-lg font-semibold text-primary-400 mb-2">Pro</div>
                        <div className="text-4xl font-bold mb-4">
                            ${activeTab === 'monthly' ? CONFIG.pricing.monthly.pro : CONFIG.pricing.yearly.pro}<span className="text-lg text-slate-400">/mo</span>
                        </div>
                        <p className="text-slate-400 mb-6">For active recruiters and small agencies</p>
                        <ul className="space-y-3 mb-8">
                            {['500 profiles/month via BYOK', 'Unlimited AI interviews', 'All sourcing platforms', 'Email support', 'ATS integrations'].map((item, i) => (
                                <li key={i} className="flex items-center gap-2 text-slate-300">
                                    <Icons.Check /> {item}
                                </li>
                            ))}
                        </ul>
                        <button className="w-full bg-slate-800 text-slate-400 cursor-not-allowed py-3 rounded-lg font-medium transition">
                            Coming Soon
                        </button>
                    </div>

                    {/* Enterprise Tier */}
                    <div className="border border-slate-800 rounded-2xl p-8 bg-slate-900/50">
                        <div className="text-lg font-semibold text-slate-400 mb-2">Enterprise</div>
                        <div className="text-4xl font-bold mb-4">$500<span className="text-lg text-slate-400">/yr</span></div>
                        <p className="text-slate-400 mb-6">For large agencies and HR departments</p>
                        <ul className="space-y-3 mb-8">
                            {['Unlimited everything', 'White-label deployment', 'On-premise option', 'Custom workflows', 'Priority support', 'SOC2 compliance'].map((item, i) => (
                                <li key={i} className="flex items-center gap-2 text-slate-300">
                                    <Icons.Check /> {item}
                                </li>
                            ))}
                        </ul>
                        <a href={`mailto:${CONFIG.project.contactEmail}`} className="block text-center bg-slate-800 hover:bg-slate-700 py-3 rounded-lg font-medium transition">
                            Contact Sales
                        </a>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default PricingPage;
