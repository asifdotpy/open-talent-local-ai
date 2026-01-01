export const CONFIG = {
    project: {
        name: "OpenTalent",
        githubUrl: "https://github.com/asifdotpy/open-talent-local-ai",
        contactEmail: "asifdotpy@gmail.com",
        tagline: "Source. Interview. Hire.",
        description: "The only platform that combines 1.8B+ profile sourcing with local AI interviewing. 100% privacy-first. 97% cheaper than LinkedIn + HireVue combined.",
    },
    navigation: [
        { name: 'Features', href: '#features' },
        { name: 'Blog', href: '#blog' },
        { name: 'Pricing', href: '#pricing' },
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
    }
};
