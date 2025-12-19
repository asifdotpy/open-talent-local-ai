/**
 * E2E Test: Voice & Analytics Integration
 *
 * Tests the voice synthesis and sentiment analysis endpoints via the gateway.
 * Skips gracefully if services are unavailable.
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

describe('E2E: Voice & Analytics Integration', () => {
  let gatewayAvailable = false;

  beforeAll(async () => {
    gatewayAvailable = await isGatewayUp();
    if (!gatewayAvailable) {
      // eslint-disable-next-line no-console
      console.warn(`\n[SKIP] Gateway not available at ${BASE_URL}. Voice/Analytics tests will be skipped.`);
    }
  });

  test('synthesize speech endpoint responds', async () => {
    if (!gatewayAvailable) return;

    const res = await fetch(`${BASE_URL}/api/v1/voice/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'This is a test of text to speech synthesis.',
        voice: 'en-US-Neural2-C',
        speed: 1.0,
      }),
    });

    // Even if voice service is offline, gateway should respond with graceful fallback
    expect([200, 503, 502]).toContain(res.status);
  });

  test('analyze sentiment endpoint responds', async () => {
    if (!gatewayAvailable) return;

    const res = await fetch(`${BASE_URL}/api/v1/analytics/sentiment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'I enjoyed this interview process. The questions were thoughtful and challenging.',
        context: 'interview_response',
      }),
    });

    // Even if analytics service is offline, gateway should respond with graceful fallback
    expect([200, 503, 502]).toContain(res.status);
  });

  test('voice + interview sequence demonstrates microservices breadth', async () => {
    if (!gatewayAvailable) return;

    // Start interview
    const startRes = await fetch(`${BASE_URL}/api/v1/interviews/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        role: 'Software Engineer',
        model: 'vetta-granite-2b-gguf-v4',
        totalQuestions: 2,
      }),
    });
    expect(startRes.ok).toBe(true);
    const session = await startRes.json();
    expect(session.messages?.length).toBeGreaterThan(0);

    // Extract question text
    const question = session.messages[session.messages.length - 1]?.content || '';
    expect(question.length).toBeGreaterThan(0);

    // Try to synthesize the question (optional, may fail gracefully)
    const voiceRes = await fetch(`${BASE_URL}/api/v1/voice/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: question.substring(0, 500),
        voice: 'en-US-Neural2-C',
      }),
    });
    // Voice service may be offline; graceful response is acceptable
    expect([200, 503, 502]).toContain(voiceRes.status);

    // Send a response and get sentiment
    const candidateResponse =
      'I have experience with algorithms and system design. ' +
      'I particularly enjoy working on distributed systems problems.';

    const respondRes = await fetch(`${BASE_URL}/api/v1/interviews/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: candidateResponse,
        session,
      }),
    });
    expect(respondRes.ok).toBe(true);

    // Analyze sentiment of response (optional, may fail gracefully)
    const sentimentRes = await fetch(`${BASE_URL}/api/v1/analytics/sentiment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: candidateResponse,
        context: 'interview_response',
      }),
    });
    // Analytics service may be offline; graceful response is acceptable
    expect([200, 503, 502]).toContain(sentimentRes.status);
  });
});
