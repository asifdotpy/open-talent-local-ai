import React, { useState } from 'react';
import { CONFIG } from '../config';
import { Icons } from './Icons';

const FAQ = () => {
    const [openIndex, setOpenIndex] = useState(null);

    const toggleAccordion = (index) => {
        setOpenIndex(openIndex === index ? null : index);
    };

    return (
        <section id="faq" className="py-24 bg-slate-950">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                        Frequently Asked Questions
                    </h2>
                    <p className="text-xl text-slate-400">
                        Everything you need to know about OpenTalent and how it can transform your recruiting process.
                    </p>
                </div>

                {/* FAQ Accordion */}
                <div className="space-y-4">
                    {CONFIG.faq.map((item, index) => (
                        <div
                            key={index}
                            className="border border-slate-800 rounded-lg overflow-hidden hover:border-slate-700 transition"
                        >
                            {/* Question Button */}
                            <button
                                onClick={() => toggleAccordion(index)}
                                className="w-full px-6 py-5 flex items-center justify-between bg-slate-900/50 hover:bg-slate-900 transition text-left"
                            >
                                <h3 className="text-lg font-semibold text-white pr-4">
                                    {item.question}
                                </h3>
                                <div className={`flex-shrink-0 transition-transform duration-300 ${openIndex === index ? 'rotate-180' : ''}`}>
                                    <svg
                                        className="w-6 h-6 text-primary-500"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M19 14l-7 7m0 0l-7-7m7 7V3"
                                        />
                                    </svg>
                                </div>
                            </button>

                            {/* Answer Content */}
                            {openIndex === index && (
                                <div className="px-6 py-5 bg-slate-800/30 border-t border-slate-800 animate-in slide-in-from-top duration-300">
                                    <p className="text-slate-300 leading-relaxed">
                                        {item.answer}
                                    </p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* CTA Section */}
                <div className="mt-16 text-center">
                    <p className="text-slate-400 mb-6">
                        Still have questions? We're here to help!
                    </p>
                    <a
                        href={`mailto:${CONFIG.project.contactEmail}`}
                        className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white font-semibold px-8 py-3 rounded-lg transition shadow-lg shadow-primary-500/20"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        Contact Us
                    </a>
                </div>
            </div>
        </section>
    );
};

export default FAQ;
