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
    blog: [
        {
            title: "The Rise of Local AI: Why Privacy is the New Competitive Advantage in Recruitment",
            description: "Discover how local AI recruitment platforms like OpenTalent are redefining data privacy and compliance, turning them into strategic assets for talent acquisition.",
            author: "Manus AI",
            date: "January 11, 2026",
            image: "/blog-images/privacy_advantage.webp",
            content: "In an increasingly data-driven world, the recruitment industry faces a paradox: the more we leverage AI for efficiency, the greater the risk to candidate privacy. Traditional cloud-based AI recruitment platforms, while powerful, often require sensitive candidate data to be transmitted and stored on third-party servers, raising concerns about data breaches, compliance, and control. However, a new paradigm is emerging: Local AI Recruitment, where privacy isn't just a feature, but a fundamental architectural principle.\n\n## The Imperative of Privacy-First Hiring\n\nWith regulations like GDPR and CCPA setting stringent standards for data protection, companies are under immense pressure to safeguard personal information. For HR and talent acquisition, this means re-evaluating every tool and process that handles candidate data. Cloud-based solutions, by their very nature, introduce external dependencies and potential vulnerabilities. A single data breach can lead to severe financial penalties, reputational damage, and a loss of trust from candidates.\n\nPrivacy-First Hiring shifts the focus from reactive compliance to proactive data protection. It's about designing recruitment workflows where data security is embedded from the ground up, ensuring that sensitive information remains under the direct control of the organization.\n\n## Local AI: The Ultimate Privacy Solution\n\nThis is where Local AI Recruitment becomes a game-changer. Unlike cloud AI, which processes data on remote servers, local AI executes all operations directly on your desktop or on-premise infrastructure. This means zero data transmission, full compliance, enhanced security, and cost efficiency.\n\nOpenTalent embodies this privacy-first approach. By leveraging local LLMs like Granite 4, it enables recruiters to conduct AI-powered interviews, analyze candidate responses, and manage talent pipelines without ever uploading sensitive information to the cloud."
        },
        {
            title: "Beyond the Hype: Why Critical Thinking is the Most Important AI Skill for 2026",
            description: "As AI tools become ubiquitous, learn why critical thinking, not just AI proficiency, is the most valuable skill for recruiters in the human-AI partnership.",
            author: "Manus AI",
            date: "January 11, 2026",
            image: "/blog-images/critical_thinking_ai.webp",
            content: "The year 2026 is poised to be a pivotal moment for AI in the workplace, particularly in recruitment. While the buzz often centers around the latest AI tools and their capabilities, a deeper look into talent acquisition trends reveals a surprising truth: the most coveted skill isn't about mastering AI, but mastering critical thinking.\n\n## The AI Paradox: Tools vs. Judgment\n\nBoardrooms are abuzz with the need for AI-certified hires, pushing for AI training and expertise across the board. Yet, a significant majority of talent acquisition leaders (73%) identify critical thinking and problem-solving as their top recruiting priorities for 2026. Why this discrepancy?\n\nThe answer lies in the nature of AI itself. Tools like ChatGPT are becoming increasingly sophisticated and accessible. Anyone can learn to generate content or analyze data with AI in a matter of weeks. However, the true value isn't in the generation, but in the evaluation.\n\n## The Human-AI Partnership: A New Skillset\n\nThe future of work isn't about AI replacing humans, but about a Human-AI Power Couple. This partnership demands a new skillset where human intelligence augments artificial intelligence. Critical thinkers are those who can question AI output, identify nuances that AI often lacks, solve unstructured problems, and ensure ethical AI application.\n\nFor talent acquisition professionals, this means a shift in focus. Instead of merely looking for candidates who can operate AI tools, the emphasis will be on those who can think critically with AI."
        },
        {
            title: "Building a Future-Proof Talent Stack: The Case for Open-Source, Desktop-First AI",
            description: "Explore the benefits of open-source, desktop-first AI platforms for recruitment, offering unparalleled control, cost efficiency, and data privacy.",
            author: "Manus AI",
            date: "January 11, 2026",
            image: "/blog-images/future_proof_talent_stack.webp",
            content: "In the rapidly evolving landscape of talent acquisition, building a robust and adaptable technology stack is paramount. Many organizations find themselves locked into expensive, proprietary cloud solutions that offer limited control and pose significant data privacy risks. However, a compelling alternative is emerging: Open-Source, Desktop-First AI platforms.\n\n## The Limitations of Traditional Cloud-Based Solutions\n\nTraditional cloud-based recruitment platforms create vendor lock-in situations, raise data sovereignty concerns, incur high operating costs, and restrict customization. These limitations are driving organizations to seek alternative solutions.\n\n## The Open-Source Advantage: Transparency, Flexibility, and Community\n\nOpen-Source AI fundamentally changes this dynamic. By making the source code publicly available, it fosters transparency, provides flexibility, enables community-driven innovation, and achieves cost efficiency.\n\n## Desktop-First AI: Control, Privacy, and Performance\n\nDesktop-First AI architecture ensures that core AI processing occurs directly on the user's local machine. The benefits include ultimate data privacy, reduced latency, offline capability, and significant cost savings.\n\nOpenTalent exemplifies this powerful combination. As an Open-Source, Desktop-First AI Recruitment Platform, it offers a future-proof talent stack that prioritizes data privacy, cost efficiency, and organizational control."
        }
    ],
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
