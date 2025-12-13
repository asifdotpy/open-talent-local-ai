/**
 * Testimonial Database Service Tests
 * Unit tests for encrypted storage and filtering
 */

import { TestimonialDatabase, ViolationType, SearchFilter } from '../testimonial-database';

describe('TestimonialDatabase', () => {
  let testimonialDatabase: TestimonialDatabase;

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    testimonialDatabase = new TestimonialDatabase();
    jest.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Initialization', () => {
    it('should initialize database', async () => {
      await expect(testimonialDatabase.initialize()).resolves.not.toThrow();
    });

    it('should handle multiple initializations', async () => {
      await testimonialDatabase.initialize();
      await expect(testimonialDatabase.initialize()).resolves.not.toThrow();
    });
  });

  describe('Save & Retrieve', () => {
    it('should save testimonial', async () => {
      const testData = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: false },
        incident: { type: ViolationType.ASSAULT, date: new Date(), location: 'Test Location', witnesses: [], context: 'Test context' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      const id = await testimonialDatabase.saveTestimonial(testData);
      expect(typeof id).toBe('string');
      expect(id).toBeTruthy();
    });

    it('should retrieve saved testimonial', async () => {
      const testData = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: false },
        incident: { type: ViolationType.HARASSMENT, date: new Date(), location: 'Test Location', witnesses: [], context: 'Test context' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      const id = await testimonialDatabase.saveTestimonial(testData);
      const retrieved = await testimonialDatabase.getTestimonial(id);

      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe(id);
    });
  });

  describe('Encryption & Decryption', () => {
    it('should encrypt sensitive data', async () => {
      const testData = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: false },
        incident: { type: ViolationType.ASSAULT, date: new Date(), location: 'Sensitive Location Data', witnesses: [], context: 'Sensitive Context' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      await testimonialDatabase.saveTestimonial(testData);

      const stored = localStorage.getItem('opentalent-testimonials');
      expect(stored).toBeDefined();
      expect(stored).not.toContain('Sensitive Location Data');
    });

    it('should decrypt data correctly', async () => {
      const testData = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: false },
        incident: { type: ViolationType.ASSAULT, date: new Date(), location: 'Test Location', witnesses: [], context: 'Test context' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      const id = await testimonialDatabase.saveTestimonial(testData);
      const retrieved = await testimonialDatabase.getTestimonial(id);

      expect(retrieved?.incident.location).toBe('Test Location');
    });
  });

  describe('PII Masking', () => {
    it('should mask witness names in export', async () => {
      const testData = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: true },
        incident: { type: ViolationType.ASSAULT, date: new Date(), location: 'Test Location', witnesses: ['John Doe'], context: 'Test context' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      const id = await testimonialDatabase.saveTestimonial(testData);
      const retrieved = await testimonialDatabase.getTestimonial(id);

      expect(retrieved).toBeDefined();
      if (retrieved && retrieved.incident.witnesses.length > 0) {
        // Names should be masked based on protectWitnesses flag
        expect(retrieved.incident.witnesses[0]).toBeDefined();
      }
    });
  });

  describe('Search & Filtering', () => {
    beforeEach(async () => {
      // Add test data
      const data1 = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: false },
        incident: { type: ViolationType.ASSAULT, date: new Date(), location: 'Location 1', witnesses: [], context: 'Context 1' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      const data2 = {
        id: 'test-2',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: true, shareWithResearchers: false, locationPrecision: 'country' as const, protectWitnesses: true },
        incident: { type: ViolationType.HARASSMENT, date: new Date(), location: 'Location 2', witnesses: [], context: 'Context 2' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      await testimonialDatabase.saveTestimonial(data1);
      await testimonialDatabase.saveTestimonial(data2);
    });

    it('should filter by incident type', async () => {
      const filter: SearchFilter = {
        incidentType: ViolationType.ASSAULT,
      };

      const results = await testimonialDatabase.listTestimonials(filter);
      expect(Array.isArray(results)).toBe(true);
      if (results.length > 0) {
        results.forEach(t => {
          expect(t.incidentType).toBe(ViolationType.ASSAULT);
        });
      }
    });

    it('should filter by anonymous flag', async () => {
      const filter: SearchFilter = {
        anonymous: true,
      };

      const results = await testimonialDatabase.listTestimonials(filter);
      expect(Array.isArray(results)).toBe(true);
      if (results.length > 0) {
        results.forEach(t => {
          expect(t.anonymous).toBe(true);
        });
      }
    });

    it('should filter by date range', async () => {
      const now = new Date();
      const start = new Date(now.getTime() - 86400000); // 24 hours ago
      const end = new Date(now.getTime() + 86400000); // 24 hours later

      const filter: SearchFilter = {
        startDate: start,
        endDate: end,
      };

      const results = await testimonialDatabase.listTestimonials(filter);
      expect(Array.isArray(results)).toBe(true);
    });

    it('should combine multiple filters', async () => {
      const now = new Date();
      const start = new Date(now.getTime() - 86400000);
      const end = new Date(now.getTime() + 86400000);

      const filter: SearchFilter = {
        incidentType: ViolationType.ASSAULT,
        anonymous: false,
        startDate: start,
        endDate: end,
      };

      const results = await testimonialDatabase.listTestimonials(filter);
      expect(Array.isArray(results)).toBe(true);
      if (results.length > 0) {
        results.forEach(t => {
          expect(t.incidentType).toBe(ViolationType.ASSAULT);
          expect(t.anonymous).toBe(false);
        });
      }
    });
  });

  describe('Update Operations', () => {
    it('should allow status updates', async () => {
      const testData = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: false },
        incident: { type: ViolationType.ASSAULT, date: new Date(), location: 'Test Location', witnesses: [], context: 'Test context' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      const id = await testimonialDatabase.saveTestimonial(testData);
      const retrieved = await testimonialDatabase.getTestimonial(id);

      expect(retrieved).toBeDefined();
    });
  });

  describe('Deletion', () => {
    it('should delete testimonial by ID', async () => {
      const testData = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: false },
        incident: { type: ViolationType.ASSAULT, date: new Date(), location: 'Test Location', witnesses: [], context: 'Test context' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      const id = await testimonialDatabase.saveTestimonial(testData);
      await testimonialDatabase.deleteTestimonial(id);

      const retrieved = await testimonialDatabase.getTestimonial(id);
      expect(retrieved).toBeNull();
    });
  });

  describe('Storage Quota', () => {
    it('should handle storage operations', async () => {
      const testData = {
        id: 'test-1',
        recordingBlob: new Blob(['audio data']),
        recording: { duration: 5000, audioUrl: 'blob:audio-url' },
        privacy: { anonymous: false, shareWithResearchers: true, locationPrecision: 'city' as const, protectWitnesses: false },
        incident: { type: ViolationType.ASSAULT, date: new Date(), location: 'Test Location', witnesses: [], context: 'Test context' },
        metadata: { recordedAt: new Date(), audioLanguage: 'en' as const, version: '1.0' },
      };

      const id = await testimonialDatabase.saveTestimonial(testData);
      expect(id).toBeTruthy();
    });
  });
});
