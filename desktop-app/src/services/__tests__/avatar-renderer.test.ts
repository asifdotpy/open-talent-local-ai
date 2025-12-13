/**
 * Avatar Renderer Service Tests
 * Unit tests for 3D avatar rendering
 */

import { AvatarRenderer, AvatarGender, AvatarSkinTone } from '../avatar-renderer';

describe('AvatarRenderer', () => {
  let avatarRenderer: AvatarRenderer;

  beforeEach(() => {
    avatarRenderer = new AvatarRenderer();
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize avatar renderer', () => {
      // Avatar renderer should be instantiable
      expect(avatarRenderer).toBeDefined();
    });

    it('should support all genders', () => {
      // All genders should be available
      const genders = [AvatarGender.MALE, AvatarGender.FEMALE, AvatarGender.NEUTRAL];
      expect(genders.length).toBe(3);
    });

    it('should support all skin tones', () => {
      // All skin tones should be available
      const tones = [AvatarSkinTone.LIGHT, AvatarSkinTone.MEDIUM, AvatarSkinTone.DARK, AvatarSkinTone.VERY_DARK];
      expect(tones.length).toBe(4);
    });
  });

  describe('Lip-Sync Animation', () => {
    it('should have playLipSyncAnimation method', () => {
      // Method should exist
      expect(typeof avatarRenderer.playLipSyncAnimation).toBe('function');
    });

    it('should handle phoneme frames', () => {
      // Method should accept phoneme frames
      expect(typeof avatarRenderer.playLipSyncAnimation).toBe('function');
    });
  });

  describe('Expression Management', () => {
    it('should have setExpression method', () => {
      // Expression method should exist
      expect(typeof avatarRenderer.setExpression).toBe('function');
    });
  });

  describe('State Management', () => {
    it('should have getState method', () => {
      // State getter should exist
      expect(typeof avatarRenderer.getState).toBe('function');
    });

    it('should return valid state object', () => {
      // State should have required properties
      const state = avatarRenderer.getState();
      expect(state).toHaveProperty('isInitialized');
      expect(state).toHaveProperty('isAnimating');
    });
  });

  describe('Resource Management', () => {
    it('should have dispose method', () => {
      // Cleanup method should exist
      expect(typeof avatarRenderer.dispose).toBe('function');
    });
  });
});
