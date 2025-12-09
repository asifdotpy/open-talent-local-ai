import { recommendModel } from './recommender';

describe('recommendModel', () => {
  it('recommends granite-350m for <6GB', () => {
    const res = recommendModel(4);
    expect(res.recommended).toBe('granite-350m');
    expect(res.reason.toLowerCase()).toContain('4');
  });

  it('recommends granite-2b for between 6GB and 14GB', () => {
    const res = recommendModel(8);
    expect(res.recommended).toBe('granite-2b');
  });

  it('recommends granite-8b for >=14GB', () => {
    const res = recommendModel(16);
    expect(res.recommended).toBe('granite-8b');
  });
});
