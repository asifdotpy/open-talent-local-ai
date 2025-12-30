import { qualityScoringClient, ScoreResult } from '../services/qualityScoringClient';

describe('QualityScoringClient', () => {
    let fetchMock: jest.SpyInstance;

    beforeEach(() => {
        fetchMock = jest.spyOn(global, 'fetch');
    });

    afterEach(() => {
        fetchMock.mockRestore();
    });

    test('scoreCandidate makes correct API call', async () => {
        const mockResult: ScoreResult = {
            candidate_id: 'c1',
            overall_score: 85,
            skill_match_score: 90,
            experience_score: 80,
            culture_fit_score: 75,
            bias_flags: [],
            recommendation: 'hire',
            timestamp: new Date().toISOString()
        };

        fetchMock.mockResolvedValue({
            ok: true,
            json: async () => mockResult
        });

        const result = await qualityScoringClient.scoreCandidate({
            candidate_id: 'c1',
            job_description: 'React dev',
            candidate_profile: { name: 'Alice' }
        });

        expect(fetchMock).toHaveBeenCalledWith(
            expect.stringContaining('/score'),
            expect.objectContaining({
                method: 'POST',
                body: expect.stringContaining('"candidate_id":"c1"')
            })
        );
        expect(result.overall_score).toBe(85);
    });

    test('checkHealth returns true on success', async () => {
        fetchMock.mockResolvedValue({ ok: true });
        const isHealthy = await qualityScoringClient.checkHealth();
        expect(isHealthy).toBe(true);
    });

    test('checkHealth returns false on error', async () => {
        fetchMock.mockRejectedValue(new Error('Network error'));
        const isHealthy = await qualityScoringClient.checkHealth();
        expect(isHealthy).toBe(false);
    });
});
