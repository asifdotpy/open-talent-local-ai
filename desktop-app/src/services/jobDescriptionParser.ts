/**
 * Job Description Parser Service
 *
 * Parses free-form job descriptions into structured format
 * using conversation-service's job_description_service.py
 */

const CONVERSATION_SERVICE_URL = process.env.REACT_APP_CONVERSATION_SERVICE_URL || 'http://localhost:8003';

export interface ParsedJobDescription {
    raw_description: string;
    job_title: string;
    location: string | null;
    experience_years: number | null;
    skills: string[];
    required_qualifications?: string[];
    nice_to_have?: string[];
    salary_range?: {
        min: number;
        max: number;
        currency: string;
    };
}

export class JobDescriptionParser {
    private baseUrl: string;

    constructor(baseUrl?: string) {
        this.baseUrl = baseUrl || CONVERSATION_SERVICE_URL;
    }

    /**
     * Parse user prompt into structured job requirements
     */
    async parsePrompt(prompt: string): Promise<ParsedJobDescription> {
        // Try API first
        try {
            const response = await fetch(`${this.baseUrl}/parse-job-description`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: prompt }),
                signal: AbortSignal.timeout(5000), // 5 second timeout
            });

            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Job description parsing API failed, using fallback:', error);
        }

        // Fallback to local parsing
        return this.fallbackParse(prompt);
    }

    /**
     * Fallback parser using regex patterns
     */
    private fallbackParse(prompt: string): ParsedJobDescription {
        // Extract location
        const locationMatch = prompt.match(/\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/);
        const location = locationMatch ? locationMatch[1] : null;

        // Extract years of experience
        const yearsMatch = prompt.match(/(\d+)\+?\s*years?/i);
        const experienceYears = yearsMatch ? parseInt(yearsMatch[1]) : null;

        // Extract skills (common tech terms)
        const techTerms = [
            'React', 'Vue', 'Angular', 'JavaScript', 'TypeScript', 'Python', 'Java',
            'Node.js', 'Express', 'Django', 'Flask', 'AWS', 'Azure', 'GCP',
            'Docker', 'Kubernetes', 'PostgreSQL', 'MongoDB', 'Redis', 'GraphQL',
            'REST', 'API', 'Git', 'CI/CD', 'Agile', 'Scrum', 'TDD', 'SQL',
            'NoSQL', 'Microservices', 'Machine Learning', 'ML', 'AI', 'Data Science',
            'CSS', 'HTML', 'Sass', 'Less', 'Webpack', 'Vite', 'Next.js', 'Nuxt',
            'Go', 'Golang', 'Rust', 'C++', 'C#', '.NET', 'Ruby', 'Rails',
            'PHP', 'Laravel', 'Terraform', 'Ansible', 'Jenkins', 'GitHub Actions'
        ];

        const skillsMatch = techTerms.filter(term => {
            const regex = new RegExp(`\\b${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
            return regex.test(prompt);
        });

        const skills = [...new Set(skillsMatch.map(s => s.toLowerCase()))];

        // Extract job title
        const jobTitle = this.extractJobTitle(prompt);

        // Extract salary if mentioned
        const salaryMatch = prompt.match(/\$?([\d,]+)k?\s*-\s*\$?([\d,]+)k?/i);
        let salary_range = undefined;
        if (salaryMatch) {
            const min = parseInt(salaryMatch[1].replace(/,/g, ''));
            const max = parseInt(salaryMatch[2].replace(/,/g, ''));
            salary_range = {
                min: min * (salaryMatch[1].endsWith('k') || salaryMatch[1].includes('k') ? 1000 : 1),
                max: max * (salaryMatch[2].endsWith('k') || salaryMatch[2].includes('k') ? 1000 : 1),
                currency: 'USD'
            };
        }

        return {
            raw_description: prompt,
            job_title: jobTitle,
            location,
            experience_years: experienceYears,
            skills,
            salary_range
        };
    }

    /**
     * Extract job title from prompt
     */
    private extractJobTitle(prompt: string): string {
        // Common job title patterns
        const patterns = [
            /\b(senior|junior|lead|staff|principal|mid-level)?\s*(software|full[- ]stack|front[- ]end|back[- ]end|web|mobile|ios|android)?\s*(engineer|developer|architect|programmer)\b/i,
            /\b(senior|junior|lead|staff|principal)?\s*(product|project|program|engineering)?\s*manager\b/i,
            /\b(senior|junior|lead|staff|principal)?\s*data\s*(scientist|analyst|engineer)\b/i,
            /\b(senior|junior|lead|staff|principal)?\s*(devops|sre|site reliability)\s*engineer\b/i,
            /\b(senior|junior|lead|staff|principal)?\s*(qa|quality assurance|test)\s*engineer\b/i,
            /\b(senior|junior|lead|staff|principal)?\s*(ux|ui|product)\s*designer\b/i,
        ];

        for (const pattern of patterns) {
            const match = prompt.match(pattern);
            if (match) {
                return match[0].trim();
            }
        }

        // Default fallback
        return 'Software Engineer';
    }

    /**
     * Check if parser service is available
     */
    async checkHealth(): Promise<boolean> {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(3000),
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }
}

// Export singleton instance
export const jobDescriptionParser = new JobDescriptionParser();
