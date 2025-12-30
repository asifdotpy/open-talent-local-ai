import { ScoutCoordinatorClient, PipelineConfig } from '../scoutCoordinatorClient';

// Mock fetch
global.fetch = jest.fn();

describe('ScoutCoordinatorClient', () => {
    let client: ScoutCoordinatorClient;

    beforeEach(() => {
        client = new ScoutCoordinatorClient();
        (fetch as jest.Mock).mockClear();
    });

    describe('createPipeline', () => {
        test('sends correct request with all parameters', async () => {
            const mockResponse = {
                pipeline_id: 'test-pipeline-123',
                status: 'pending',
                message: 'Pipeline created successfully'
            };

            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            });

            const config: PipelineConfig = {
                jobDescription: 'Senior React Developer in NYC',
                location: 'New York',
                skills: ['React', 'TypeScript'],
                tools: ['github', 'stackoverflow']
            };

            const result = await client.createPipeline(config);

            expect(fetch).toHaveBeenCalledWith(
                expect.stringContaining('/pipelines/create'),
                expect.objectContaining({
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: expect.stringContaining('Senior React Developer')
                })
            );

            expect(result.pipeline_id).toBe('test-pipeline-123');
        });

        test('handles API error gracefully', async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                statusText: 'Internal Server Error',
                text: async () => 'Service unavailable'
            });

            const config: PipelineConfig = {
                jobDescription: 'Test',
                tools: ['github']
            };

            await expect(client.createPipeline(config))
                .rejects.toThrow('Pipeline creation failed');
        });
    });

    describe('getPipelineStatus', () => {
        test('fetches pipeline status successfully', async () => {
            const mockStatus = {
                pipeline_id: 'test-123',
                state: 'scanning',
                progress_percentage: 50,
                recent_activities: []
            };

            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => mockStatus
            });

            const status = await client.getPipelineStatus('test-123');

            expect(status.state).toBe('scanning');
            expect(status.progress_percentage).toBe(50);
        });

        test('handles status fetch error', async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                statusText: 'Not Found'
            });

            await expect(client.getPipelineStatus('invalid-id'))
                .rejects.toThrow('Failed to get status');
        });
    });

    describe('getCandidates', () => {
        test('fetches candidates successfully', async () => {
            const mockCandidates = {
                pipeline_id: 'test-123',
                total_candidates: 5,
                candidates: [
                    { id: '1', name: 'Alice', score: 85 },
                    { id: '2', name: 'Bob', score: 90 }
                ]
            };

            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => mockCandidates
            });

            const result = await client.getCandidates('test-123');

            expect(result.total_candidates).toBe(5);
            expect(result.candidates).toHaveLength(2);
        });
    });

    describe('getAgentHealth', () => {
        test('fetches agent health successfully', async () => {
            const mockHealth = {
                'scout-coordinator': { status: 'healthy' },
                'data-enrichment': { status: 'healthy' }
            };

            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => mockHealth
            });

            const health = await client.getAgentHealth();

            expect(health['scout-coordinator'].status).toBe('healthy');
        });

        test('returns fallback health on error', async () => {
            (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

            const health = await client.getAgentHealth();

            expect(health['scout-coordinator'].status).toBe('unreachable');
        });
    });

    describe('checkHealth', () => {
        test('returns true when service is healthy', async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true
            });

            const isHealthy = await client.checkHealth();
            expect(isHealthy).toBe(true);
        });

        test('returns false when service is down', async () => {
            (fetch as jest.Mock).mockRejectedValueOnce(new Error('Connection refused'));

            const isHealthy = await client.checkHealth();
            expect(isHealthy).toBe(false);
        });
    });
});
