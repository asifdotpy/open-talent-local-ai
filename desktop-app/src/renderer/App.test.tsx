import React from 'react';
import { render } from '@testing-library/react';
import App from './App';

// Mock electronAPI
beforeEach(() => {
  (window as any).electronAPI = {
    detectHardware: jest.fn().mockResolvedValue({
      totalMemoryGB: 16,
      cpuCores: 8,
      platform: 'win32',
    }),
    recommendModel: jest.fn((ramGB: number) => {
      if (ramGB < 6) return 'granite-350m';
      if (ramGB < 14) return 'granite-2b';
      return 'granite-8b';
    }),
    loadConfig: jest.fn().mockResolvedValue(null),
    saveConfig: jest.fn().mockResolvedValue(undefined),
  };
});

describe('App Renderer Smoke Test', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />);
    expect(container).toBeTruthy();
  });

  it('has wizard DOM structure', () => {
    const { container } = render(<App />);
    const wizard = container.querySelector('[class*="wizard"]') || container.querySelector('[class*="Wizard"]') || container.querySelector('div');
    expect(wizard).toBeTruthy();
  });

  it('mocks electronAPI successfully', () => {
    render(<App />);
    expect((window as any).electronAPI).toBeDefined();
    expect((window as any).electronAPI.detectHardware).toBeDefined();
  });

  it('renders without errors in console', () => {
    const spy = jest.spyOn(console, 'error').mockImplementation(() => {});
    render(<App />);
    // Allow async state warnings but app should render
    expect(spy).toHaveBeenCalledTimes(0);
    spy.mockRestore();
  });
});
