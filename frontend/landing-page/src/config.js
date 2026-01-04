export const CONFIG = {
    project: {
        name: "OpenTalent",
        githubUrl: "https://github.com/asifdotpy/open-talent-local-ai",
        contactEmail: "asifdotpy@gmail.com",
        tagline: "Source. Interview. Hire.",
        description: "The only platform that combines 1.8B+ profile sourcing with local AI interviewing. 100% privacy-first. 97% cheaper than LinkedIn + HireVue combined.",
    },
    navLinks: [
        { label: 'Features', href: '/features' },
        { label: 'Blog', href: '/blog' },
        { label: 'Pricing', href: '/pricing' },
        { label: 'Community', href: '/community' },
        { label: 'FAQ', href: '/faq' },
        { label: 'Download', href: '/download' },
    ],
    features: [
        {
            title: "Multi-Platform Sourcing",
            description: "Search LinkedIn, GitHub, Stack Overflow, and the open web. 1.8B+ profiles at your fingertips."
        },
        {
            title: "Local AI Interviews",
            description: "Run structured interviews with Granite AI models locally. Zero cloud dependency."
        },
        {
            title: "Privacy First",
            description: "All candidate data stays on your device. GDPR and CCPA compliant by design."
        },
        {
            title: "BYOK Model",
            description: "Bring Your Own Key for API access. Pay vendors directly at wholesale prices."
        }
    ],
    pricing: {
        monthly: {
            free: 0,
            pro: 49,
        },
        yearly: {
            free: 0,
            pro: 41,
        }
    },
    downloads: {
        windows: { name: "Windows", version: "Windows 10+", status: "Coming Soon" },
        macos: { name: "macOS", version: "macOS 11+", status: "Coming Soon" },
        linux: { name: "Linux", version: "Ubuntu/Debian", status: "Coming Soon" },
    },
    faq: [
        {
            question: "What is OpenTalent?",
            answer: "OpenTalent is the world's first desktop-first, open-source AI recruitment platform. It allows recruiters to source, interview, and hire candidates using 100% local AI processing, ensuring complete data privacy and significant cost savings."
        },
        {
            question: "How does OpenTalent ensure data privacy?",
            answer: "All data processing, including AI interviews and candidate data storage, happens exclusively on your local machine. No candidate data, interview transcripts, or user activity is ever sent to our servers or any third-party cloud services. This is a core architectural principle."
        },
        {
            question: "What does 'Local AI' mean?",
            answer: "'Local AI' means the platform runs powerful AI models (like Granite 4) directly on your computer using technologies like Ollama. This eliminates cloud dependency, reduces latency, and guarantees that your sensitive hiring data never leaves your device."
        },
        {
            question: "Is OpenTalent truly open source?",
            answer: "Yes, the core software is licensed under the MIT License. This allows for full transparency, community contributions, and the freedom to use, modify, and distribute the software."
        },
        {
            question: "How much does OpenTalent cost?",
            answer: "OpenTalent offers a Free tier that is free forever. Paid tiers (Pro and Enterprise) are available for power users and large organizations, offering a 97% cost saving compared to traditional cloud-based recruitment stacks."
        },
        {
            question: "What is the BYOK (Bring Your Own Key) model?",
            answer: "For features that require external APIs (e.g., sourcing from LinkedIn), OpenTalent uses a BYOK model. You provide your own API keys, establishing a direct connection with the third-party provider. OpenTalent does not act as a data intermediary."
        },
        {
            question: "What are the system requirements?",
            answer: "OpenTalent is designed to run on modern Windows, macOS, and Linux systems. While it is optimized for local AI, a machine with a dedicated GPU is recommended for the best performance during AI interviews."
        }
    ]
};
