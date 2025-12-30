import { JobDescriptionParser } from '../jobDescriptionParser';

// Mock fetch
global.fetch = jest.fn();

describe('JobDescriptionParser', () => {
    let parser: JobDescriptionParser;

    beforeEach(() => {
        parser = new JobDescriptionParser();
        (fetch as jest.Mock).mockClear();
    });

    describe('parsePrompt', () => {
        test('uses API when available', async () => {
            const mockParsed = {
                raw_description: 'Test prompt',
                job_title: 'Senior Engineer',
                location: 'San Francisco',
                experience_years: 5,
                skills: ['react', 'typescript']
            };

            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => mockParsed
            });

            const result = await parser.parsePrompt('Test prompt');

            expect(result.job_title).toBe('Senior Engineer');
            expect(result.location).toBe('San Francisco');
        });

        test('falls back to regex parsing on API failure', async () => {
            (fetch as jest.Mock).mockRejectedValueOnce(new Error('API unavailable'));

            const result = await parser.parsePrompt('Senior React developer in New York with 5+ years experience');

            expect(result.location).toBe('New York');
            expect(result.experience_years).toBe(5);
            expect(result.skills).toContain('react');
        });
    });

    describe('fallback parsing', () => {
        beforeEach(() => {
            // Force API to fail for all tests in this group
            (fetch as jest.Mock).mockRejectedValue(new Error('API down'));
        });

        test('extracts location from prompt', async () => {
            const result = await parser.parsePrompt('Frontend developer in San Francisco');
            expect(result.location).toBe('San Francisco');
        });

        test('extracts years of experience', async () => {
            const result = await parser.parsePrompt('Engineer with 8+ years experience');
            expect(result.experience_years).toBe(8);
        });

        test('extracts skills from prompt', async () => {
            const result = await parser.parsePrompt('React developer with TypeScript and Node.js experience');

            expect(result.skills).toContain('react');
            expect(result.skills).toContain('typescript');
            expect(result.skills).toContain('node.js');
        });

        test('identifies job title patterns', async () => {
            const tests = [
                { prompt: 'Senior Software Engineer needed', expected: /Senior Software Engineer/i },
                { prompt: 'Looking for Full Stack Developer', expected: /Full Stack Developer/i },
                { prompt: 'Product Manager role', expected: /Product Manager/i },
                { prompt: 'Data Scientist position', expected: /Data Scientist/i }
            ];

            for (const { prompt, expected } of tests) {
                const result = await parser.parsePrompt(prompt);
                expect(result.job_title).toMatch(expected);
            }
        });

        test('handles prompts without location', async () => {
            const result = await parser.parsePrompt('Senior React Developer');
            expect(result.location).toBeNull();
        });

        test('handles prompts without experience years', async () => {
            const result = await parser.parsePrompt('React Developer in NYC');
            expect(result.experience_years).toBeNull();
        });

        test('extracts salary range if present', async () => {
            const result = await parser.parsePrompt('Engineer in NYC, $120k-$150k');

            expect(result.salary_range).toBeDefined();
            expect(result.salary_range?.min).toBe(120000);
            expect(result.salary_range?.max).toBe(150000);
            expect(result.salary_range?.currency).toBe('USD');
        });

        test('defaults to Software Engineer if no title found', async () => {
            const result = await parser.parsePrompt('Looking for someone with React skills');
            expect(result.job_title).toBe('Software Engineer');
        });

        test('preserves raw description', async () => {
            const prompt = 'This is the original prompt';
            const result = await parser.parsePrompt(prompt);
            expect(result.raw_description).toBe(prompt);
        });
    });

    describe('checkHealth', () => {
        test('returns true when service is available', async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true
            });

            const isHealthy = await parser.checkHealth();
            expect(isHealthy).toBe(true);
        });

        test('returns false when service is unavailable', async () => {
            (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

            const isHealthy = await parser.checkHealth();
            expect(isHealthy).toBe(false);
        });
    });
});
