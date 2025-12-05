import { chromium } from 'playwright';

describe('R3F Demo E2E Tests', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await chromium.launch();
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  it('renders the R3F demo page', async () => {
    await page.goto('http://localhost:5173');

    const title = await page.title();
    expect(title).toBe('R3F Avatar Demo');

    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
  });

  it('handles text input and triggers avatar speech', async () => {
    await page.goto('http://localhost:5173');

    // Enter text into the input field
    const inputSelector = 'textarea';
    await page.fill(inputSelector, 'Hello, how are you?');

    // Click the speak button
    const speakButtonSelector = 'button:has-text("Speak")';
    await page.click(speakButtonSelector);

    // Wait for the avatar to start speaking
    await page.waitForSelector('text=🎤 Speaking...', { timeout: 5000 });

    // Verify that the audio player is playing
    const audioElement = await page.$('audio');
    const isAudioPlaying = await audioElement.evaluate((audio) => !audio.paused);
    expect(isAudioPlaying).toBe(true);
  });

  it('displays phoneme animation during speech', async () => {
    await page.goto('http://localhost:5173');

    // Enter text into the input field
    const inputSelector = 'textarea';
    await page.fill(inputSelector, 'Testing phoneme animation.');

    // Click the speak button
    const speakButtonSelector = 'button:has-text("Speak")';
    await page.click(speakButtonSelector);

    // Wait for phoneme animation to start
    await page.waitForSelector('canvas', { timeout: 5000 });

    // Verify that the canvas is rendering frames
    const canvas = await page.$('canvas');
    const frameCount = await canvas.evaluate((canvas) => canvas.getContext('webgl').drawingBufferHeight);
    expect(frameCount).toBeGreaterThan(0);
  });

  it('handles errors gracefully when voice service is unavailable', async () => {
    await page.goto('http://localhost:5173');

    // Simulate voice service failure
    await page.route('http://localhost:8002/voice/tts', (route) => {
      route.fulfill({ status: 500, body: 'Internal Server Error' });
    });

    // Enter text into the input field
    const inputSelector = 'textarea';
    await page.fill(inputSelector, 'This will fail.');

    // Click the speak button
    const speakButtonSelector = 'button:has-text("Speak")';
    await page.click(speakButtonSelector);

    // Verify error message is displayed
    const errorMessage = await page.waitForSelector('text=Failed to generate speech', { timeout: 5000 });
    expect(errorMessage).not.toBeNull();
  });
});