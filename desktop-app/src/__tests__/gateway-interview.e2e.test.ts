/**
 * E2E Test: Integration Gateway Interview Flow
 *
 * This test suite validates the happy-path through the Desktop Integration Service (gateway)
 * running at http://localhost:8009. It will gracefully skip if the gateway is not available.
 */

const BASE_URL = process.env.INTEGRATION_BASE_URL || 'http://localhost:8009';

async function isGatewayUp(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

describe('E2E: Gateway Interview Flow', () => {
  let gatewayAvailable = false;

  beforeAll(async () => {
    gatewayAvailable = await isGatewayUp();
    if (!gatewayAvailable) {
      // eslint-disable-next-line no-console
      console.warn(`\n[SKIP] Gateway not available at ${BASE_URL}. Start it and re-run tests.`);
    }
  });

  test('health endpoint responds', async () => {
    if (!gatewayAvailable) return;

    const res = await fetch(`${BASE_URL}/health`);
    expect(res.ok).toBe(true);
    const body = await res.json();
    expect(body).toBeDefined();
    expect(typeof body.status === 'string').toBe(true);
  });

  test('models endpoint returns array', async () => {
    if (!gatewayAvailable) return;

    const res = await fetch(`${BASE_URL}/api/v1/models`);
    expect(res.ok).toBe(true);
    const body = await res.json();
    expect(body).toBeDefined();
    expect(Array.isArray(body.models)).toBe(true);
  });

  test('start/respond/summary interview sequence', async () => {
    if (!gatewayAvailable) return;

    // Start interview
    const startRes = await fetch(`${BASE_URL}/api/v1/interviews/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: 'Software Engineer', model: 'vetta-granite-2b-gguf-v4', totalQuestions: 3 }),
    });
    expect(startRes.ok).toBe(true);
    const session = await startRes.json();
    expect(session).toBeDefined();
    expect(session.config).toBeDefined();
    expect(session.messages?.length).toBeGreaterThan(0);

    // Respond to first question
    const respondRes = await fetch(`${BASE_URL}/api/v1/interviews/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: 'I have experience with arrays, hash maps, and trees. I prefer O(n log n) approaches where possible.',
        session,
      }),
    });
    expect(respondRes.ok).toBe(true);
    const updated = await respondRes.json();
    expect(updated).toBeDefined();
    expect(updated.messages?.length).toBeGreaterThan(session.messages.length);
    expect(typeof updated.isComplete === 'boolean').toBe(true);

    // Summary
    const summaryRes = await fetch(`${BASE_URL}/api/v1/interviews/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updated),
    });
    expect(summaryRes.ok).toBe(true);
    const summary = await summaryRes.json();
    expect(summary).toBeDefined();
    expect(typeof summary.summary === 'string').toBe(true);
  });
});
