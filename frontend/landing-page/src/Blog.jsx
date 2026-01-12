import React, { useState } from 'react';
import { CONFIG } from './config';
import { Icons } from './components/Icons';

const Blog = () => {
    const [selectedArticle, setSelectedArticle] = useState(null);

    const openArticle = (article) => {
        setSelectedArticle(article);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const closeArticle = () => {
        setSelectedArticle(null);
    };

    if (selectedArticle) {
        return (
            <section id="blog" className="py-24 px-4 bg-slate-900/30 min-h-screen">
                <div className="max-w-4xl mx-auto text-white">
                    <button
                        onClick={closeArticle}
                        className="mb-8 flex items-center gap-2 text-primary-400 hover:text-primary-300 transition"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back to Articles
                    </button>

                    <article className="space-y-8">
                        <header className="border-b border-slate-800 pb-8">
                            <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
                                {selectedArticle.title}
                            </h1>
                            <div className="flex items-center gap-4 text-slate-400">
                                <span>{selectedArticle.author}</span>
                                <span>•</span>
                                <span>{selectedArticle.date}</span>
                            </div>
                        </header>

                        <div className="prose prose-invert prose-slate max-w-none text-lg text-slate-300 leading-relaxed space-y-6">
                            {selectedArticle.content.split('\n\n').map((paragraph, idx) => {
                                if (paragraph.startsWith('# ')) {
                                    return (
                                        <h1 key={idx} className="text-3xl font-bold text-white mt-8">
                                            {paragraph.replace('# ', '')}
                                        </h1>
                                    );
                                }
                                if (paragraph.startsWith('## ')) {
                                    return (
                                        <h2 key={idx} className="text-2xl font-bold text-white mt-6">
                                            {paragraph.replace('## ', '')}
                                        </h2>
                                    );
                                }
                                if (paragraph.startsWith('### ')) {
                                    return (
                                        <h3 key={idx} className="text-xl font-bold text-white mt-4">
                                            {paragraph.replace('### ', '')}
                                        </h3>
                                    );
                                }
                                if (paragraph.startsWith('*   ')) {
                                    const items = paragraph.split('\n').filter(line => line.startsWith('*   '));
                                    return (
                                        <ul key={idx} className="list-disc list-inside space-y-2 ml-4">
                                            {items.map((item, i) => (
                                                <li key={i}>{item.replace('*   ', '')}</li>
                                            ))}
                                        </ul>
                                    );
                                }
                                return (
                                    <p key={idx} className="text-slate-300">
                                        {paragraph}
                                    </p>
                                );
                            })}
                        </div>
                    </article>
                </div>
            </section>
        );
    }

    return (
        <section id="blog" className="py-24 px-4 bg-slate-900/30">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                        Industry Insights & Thought Leadership
                    </h2>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                        Explore the latest trends in local AI recruitment, privacy-first hiring, and the future of talent acquisition.
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    {CONFIG.blog.map((article, index) => (
                        <article
                            key={index}
                            className="group cursor-pointer bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden hover:border-primary-500/50 hover:shadow-lg hover:shadow-primary-500/10 transition duration-300"
                            onClick={() => openArticle(article)}
                        >
                            {/* Article Image Placeholder */}
                            <div className="h-48 bg-gradient-to-br from-primary-600/20 to-primary-900/20 flex items-center justify-center border-b border-slate-700 group-hover:from-primary-600/30 group-hover:to-primary-900/30 transition">
                                <div className="text-center">
                                    <Icons.Zap className="w-12 h-12 text-primary-400 mx-auto mb-2" />
                                    <p className="text-sm text-slate-400">Featured Article</p>
                                </div>
                            </div>

                            {/* Article Content */}
                            <div className="p-6 space-y-4">
                                <h3 className="text-xl font-bold text-white group-hover:text-primary-400 transition line-clamp-2">
                                    {article.title}
                                </h3>
                                <p className="text-slate-400 line-clamp-3">
                                    {article.description}
                                </p>

                                {/* Article Meta */}
                                <div className="flex items-center justify-between pt-4 border-t border-slate-700">
                                    <div className="text-sm text-slate-500">
                                        <div className="font-medium text-slate-400">{article.author}</div>
                                        <div>{article.date}</div>
                                    </div>
                                    <div className="text-primary-400 group-hover:translate-x-1 transition">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </article>
                    ))}
                </div>

                {/* CTA Section */}
                <div className="mt-16 text-center">
                    <p className="text-slate-400 mb-6">
                        Want to stay updated with the latest insights on AI recruitment?
                    </p>
                    <a
                        href={`mailto:${CONFIG.project.contactEmail}?subject=Subscribe to OpenTalent Blog`}
                        className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white font-semibold px-8 py-3 rounded-lg transition shadow-lg shadow-primary-500/20"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        Subscribe for Updates
                    </a>
                </div>
            </div>
        </section>
    );
};

export default Blog;
