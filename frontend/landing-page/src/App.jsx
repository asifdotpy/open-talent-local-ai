import { useState } from 'react'
import Blog from './Blog'

// Icons as simple SVG components
const Icons = {
    Download: () => (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
    ),
    GitHub: () => (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
        </svg>
    ),
    Shield: () => (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
    ),
    Search: () => (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
    ),
    Bot: () => (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
    ),
    Zap: () => (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
    ),
    Check: () => (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
    ),
    Windows: () => (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801" />
        </svg>
    ),
    Apple: () => (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
        </svg>
    ),
    Linux: () => (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587.26 1.24.43 1.922.43 1.104 0 2.19-.388 3.124-1.086.49.37 1.17.645 1.98.645.867-.001 1.715-.333 2.25-.812.425.253.88.42 1.35.456.416.031.82-.062 1.158-.255.67-.382.767-1.156.73-1.873a.84.84 0 01-.003-.081c.31-.424.531-.945.531-1.516 0-.334-.055-.665-.225-.96a8.7 8.7 0 00-.45-.788c-.1-.164-.2-.31-.27-.466a2.76 2.76 0 01-.117-.35c-.148-.628-.14-1.26.025-1.886.048-.184.103-.368.175-.555.181-.49.374-.99.416-1.55.043-.553-.056-1.12-.309-1.64a8.69 8.69 0 00-.728-1.199c-.437-.57-.958-1.095-1.399-1.67-.324-.42-.646-.976-.711-1.514-.027-.234-.003-.475.068-.69.014-.058.032-.114.053-.169.063-.164.134-.213.146-.223-.114-.033-.243-.067-.333-.112a.586.586 0 01-.126-.072 1.41 1.41 0 00-.228-.085c-.1-.026-.203-.048-.308-.048a2.89 2.89 0 00-.3 0 2.34 2.34 0 00-.25.032 2.97 2.97 0 00-.326.082c-.108.034-.217.077-.324.121a4.31 4.31 0 00-.27.117c-.078.038-.161.072-.24.11-.141.073-.284.147-.422.229" />
        </svg>
    ),
    Menu: () => (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
        </svg>
    ),
    Close: () => (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
    )
}

// GitHub URL
const GITHUB_URL = "https://github.com/asifdotpy/open-talent-local-ai"

function App() {
    const [activeTab, setActiveTab] = useState('monthly')
    const [isMenuOpen, setIsMenuOpen] = useState(false)

    const navLinks = [
        { name: 'Features', href: '#features' },
        { name: 'Blog', href: '#blog' },
        { name: 'Pricing', href: '#pricing' },
    ]

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Navigation */}
            <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-lg border-b border-slate-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-betwee                        <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg"></div>
                            <span className="text-xl font-bold">OpenTalent</span>
                        </div>         
                        {/* Desktop Menu */}
                        <div className="hidden md:flex items-center space-x-8">
                            {navLinks.map((link) => (
                                <a key={link.name} href={link.href} className="text-slate-300 hover:text-white transition">
                                    {link.name}
                                </a>
                            ))}
                            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="text-slate-300 hover:text-white transition flex items-center gap-2">
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
                        {navLinks.map((link) => (
                            <a 
                                key={link.name} 
                                href={link.href} 
                                onClick={() => setIsMenuOpen(false)}
                                className="block text-slate-300 hover:text-white transition text-lg"
                            >
                                {link.name}
                            </a>
                        ))}
                        <a 
                            href={GITHUB_URL} 
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

            {/* Hero Section */}
            <section className="hero-gradient pt-32 pb-20 px-4 relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-50"></div>
                <div className="max-w-7xl mx-auto text-center relative">
                    <div className="inline-flex items-center gap-2 bg-slate-800/50 border border-slate-700 rounded-full px-4 py-2 mb-8">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        <span className="text-sm text-slate-300">Now Open Source</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
                        All-in-One Recruiting<br />
                        <span className="gradient-text">Source. Interview. Hire.</span>
                    </h1>

                    <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-10">
                        The only platform that combines <strong className="text-white">1.8B+ profile sourcing</strong> with
                        <strong className="text-white"> local AI interviewing</strong>. 100% privacy-first.
                        97% cheaper than LinkedIn + HireVue combined.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
                        <button className="bg-slate-800 text-slate-400 cursor-not-allowed px-8 py-4 rounded-xl font-semibold text-lg transition flex items-center justify-center gap-3">
                            Coming Soon
                        </button>
                        <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="bg-slate-800 hover:bg-slate-700 border border-slate-700 px-8 py-4 rounded-xl font-semibold text-lg transition flex items-center justify-center gap-3">
                            <Icons.GitHub /> View on GitHub
                        </a>
                    </div>

                    <div className="flex flex-wrap justify-center gap-8 text-slate-400">
                        <div className="flex items-center gap-2">
                            <Icons.Check />
                            <span>GDPR Compliant</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Icons.Check />
                            <span>Local AI Processing</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Icons.Check />
                            <span>Open Source</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
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
                        <div className="text-4xl font-bold gradient-text">15</div>
                        <div className="text-slate-400 mt-2">Microservices</div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-24 px-4">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold mb-4">Everything You Need to Recruit</h2>
                        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                            One platform replaces your entire recruiting stack
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {[
                            {
                                icon: <Icons.Search />,
                                title: "Multi-Platform Sourcing",
                                description: "Search LinkedIn, GitHub, Stack Overflow, and the open web. 1.8B+ profiles at your fingertips."
                            },
                            {
                                icon: <Icons.Bot />,
                                title: "Local AI Interviews",
                                description: "Run structured interviews with Granite AI models locally. Zero cloud dependency."
                            },
                            {
                                icon: <Icons.Shield />,
                                title: "Privacy First",
                                description: "All candidate data stays on your device. GDPR and CCPA compliant by design."
                            },
                            {
                                icon: <Icons.Zap />,
                                title: "BYOK Model",
                                description: "Bring Your Own Key for API access. Pay vendors directly at wholesale prices."
                            }
                        ].map((feature, i) => (
                            <div key={i} className="card-gradient border border-slate-800 rounded-2xl p-6 hover:border-primary-500/50 transition">
                                <div className="w-14 h-14 bg-primary-500/20 rounded-xl flex items-center justify-center text-primary-400 mb-4">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                                <p className="text-slate-400">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-24 px-4 bg-slate-900/30">
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
                                ${activeTab === 'monthly' ? '49' : '41'}<span className="text-lg text-slate-400">/mo</span>
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
                            <a href="mailto:asifdotpy@gmail.com" className="block text-center bg-slate-800 hover:bg-slate-700 py-3 rounded-lg font-medium transition">
                                Contact Sales
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            {/* Blog Section */}
            <Blog />

            {/* Download Section */}
            <section id="download" className="py-24 px-4">
                <div className="max-w-4xl mx-auto text-center">
                    <h2 className="text-4xl font-bold mb-4">Download OpenTalent</h2>
                    <p className="text-xl text-slate-400 mb-12">
                        Available for Windows, macOS, and Linux. Free forever on the Free tier.
                    </p>

                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="flex flex-col items-center gap-4 border border-slate-800 rounded-2xl p-8 bg-slate-900/50 opacity-75">
                            <Icons.Windows />
                            <div>
                                <div className="font-semibold text-lg">Windows</div>
                                <div className="text-slate-400 text-sm">Windows 10+</div>
                            </div>
                            <span className="text-slate-500 text-sm font-medium">Coming Soon</span>
                        </div>

                        <div className="flex flex-col items-center gap-4 border border-slate-800 rounded-2xl p-8 bg-slate-900/50 opacity-75">
                            <Icons.Apple />
                            <div>
                                <div className="font-semibold text-lg">macOS</div>
                                <div className="text-slate-400 text-sm">macOS 11+</div>
                            </div>
                            <span className="text-slate-500 text-sm font-medium">Coming Soon</span>
                        </div>

                        <div className="flex flex-col items-center gap-4 border border-slate-800 rounded-2xl p-8 bg-slate-900/50 opacity-75">
                            <Icons.Linux />
                            <div>
                                <div className="font-semibold text-lg">Linux</div>
                                <div className="text-slate-400 text-sm">Ubuntu/Debian</div>
                            </div>
                            <span className="text-slate-500 text-sm font-medium">Coming Soon</span>
                        </div>
                    </div>

                    <p className="mt-8 text-slate-500">
                        Or build from source: <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:underline">github.com/asifdotpy/open-talent-local-ai</a>
                    </p>
                </div>
            </section>

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
                        <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="border border-white/30 hover:bg-white/10 px-8 py-4 rounded-xl font-semibold text-lg transition flex items-center justify-center gap-3">
                            <Icons.GitHub /> Star on GitHub
                        </a>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-4 border-t border-slate-800">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg"></div>
                        <span className="text-xl font-bold">OpenTalent</span>
                    </div>
                    <div className="flex items-center gap-6 text-slate-400">
                        <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="hover:text-white transition flex items-center gap-2">
                            <Icons.GitHub /> GitHub
                        </a>
                        <a href="mailto:asifdotpy@gmail.com" className="hover:text-white transition">Contact</a>
                        <a href="#" className="hover:text-white transition">Privacy</a>
                        <a href="#" className="hover:text-white transition">Terms</a>
                    </div>
                    <div className="text-slate-500 text-sm">
                        © 2025 OpenTalent. Open Source under MIT.
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default App
