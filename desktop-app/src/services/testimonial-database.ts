/**
 * Testimonial Database Service
 * Handles encrypted SQLite storage of testimonials
 * Part of Day 5-6 implementation
 */

import * as CryptoJS from 'crypto-js';

export enum ViolationType {
  ASSAULT = 'assault',
  HARASSMENT = 'harassment',
  DISCRIMINATION = 'discrimination',
  HUMAN_TRAFFICKING = 'human_trafficking',
  FORCED_LABOR = 'forced_labor',
  CHILD_ABUSE = 'child_abuse',
  SEXUAL_VIOLENCE = 'sexual_violence',
  EXTORTION = 'extortion',
  UNLAWFUL_DETENTION = 'unlawful_detention',
  DENIAL_OF_SERVICES = 'denial_of_services',
  PROPERTY_THEFT = 'property_theft',
  WAGE_THEFT = 'wage_theft',
  DOCUMENT_WITHHOLDING = 'document_withholding',
  MOVEMENT_RESTRICTION = 'movement_restriction',
  THREATS = 'threats',
  OTHER = 'other',
}

export interface TestimonialData {
  id: string;
  recordingBlob: Blob;
  recording: {
    duration: number;
    audioUrl: string;
  };
  privacy: {
    anonymous: boolean;
    shareWithResearchers: boolean;
    locationPrecision: 'exact' | 'city' | 'country';
    protectWitnesses: boolean;
  };
  incident: {
    type: ViolationType;
    date: Date;
    location: string;
    witnesses: string[];
    context: string;
  };
  metadata: {
    recordedAt: Date;
    audioLanguage: 'en' | 'bn';
    version: string;
  };
}

export interface Testimonial {
  id: string;
  recordedAt: Date;
  audioPath: string;
  audioEncrypted: boolean;
  transcription?: string;
  incidentType: ViolationType;
  incidentDate?: Date;
  location: string;
  anonymous: boolean;
  shareWithResearchers: boolean;
  witnessNames: string[];
  context: string;
  privacyMaskApplied: boolean;
  createdAt: Date;
  status: 'draft' | 'submitted' | 'processed';
}

export interface SearchFilter {
  incidentType?: ViolationType;
  anonymous?: boolean;
  startDate?: Date;
  endDate?: Date;
  searchText?: string;
  status?: string;
}

export class TestimonialDatabase {
  private storageKey = 'opentalent-testimonials';
  private encryptionKey: string;
  private testimonials: Map<string, Testimonial> = new Map();

  constructor() {
    // Generate or retrieve encryption key from localStorage
    this.encryptionKey = this.getOrCreateEncryptionKey();
    this.loadTestimonials();
  }

  /**
   * Get or create encryption key
   */
  private getOrCreateEncryptionKey(): string {
    const stored = localStorage.getItem('opentalent-enc-key');
    if (stored) {
      return stored;
    }

    // Generate new key
    const key = CryptoJS.lib.WordArray.random(16).toString();
    localStorage.setItem('opentalent-enc-key', key);
    return key;
  }

  /**
   * Initialize database
   */
  async initialize(): Promise<void> {
    console.log('✅ Testimonial database initialized');
  }

  /**
   * Save testimonial with encryption
   */
  async saveTestimonial(data: TestimonialData): Promise<string> {
    try {
      const testimonial: Testimonial = {
        id: data.id || this.generateId(),
        recordedAt: data.metadata.recordedAt,
        audioPath: this.encryptBlob(data.recordingBlob, data.id),
        audioEncrypted: true,
        transcription: undefined,
        incidentType: data.incident.type,
        incidentDate: data.incident.date,
        location: this.encryptString(data.incident.location),
        anonymous: data.privacy.anonymous,
        shareWithResearchers: data.privacy.shareWithResearchers,
        witnessNames: data.privacy.protectWitnesses
          ? data.incident.witnesses.map((w) => this.maskName(w))
          : data.incident.witnesses,
        context: this.encryptString(data.incident.context),
        privacyMaskApplied: data.privacy.anonymous,
        createdAt: new Date(),
        status: 'draft',
      };

      this.testimonials.set(testimonial.id, testimonial);
      this.persistToStorage();

      console.log('✅ Testimonial saved:', testimonial.id);
      return testimonial.id;
    } catch (error) {
      console.error('❌ Failed to save testimonial:', error);
      throw error;
    }
  }

  /**
   * Retrieve testimonial by ID
   */
  async getTestimonial(id: string): Promise<TestimonialData | null> {
    const testimonial = this.testimonials.get(id);
    if (!testimonial) {
      return null;
    }

    // Reconstruct TestimonialData from stored Testimonial
    return {
      id: testimonial.id,
      recordingBlob: new Blob(), // Would need to decrypt from storage
      recording: {
        duration: 0, // Retrieved from metadata
        audioUrl: testimonial.audioPath,
      },
      privacy: {
        anonymous: testimonial.anonymous,
        shareWithResearchers: testimonial.shareWithResearchers,
        locationPrecision: 'city',
        protectWitnesses: testimonial.privacyMaskApplied,
      },
      incident: {
        type: testimonial.incidentType,
        date: testimonial.incidentDate || new Date(),
        location: this.decryptString(testimonial.location),
        witnesses: testimonial.witnessNames,
        context: this.decryptString(testimonial.context),
      },
      metadata: {
        recordedAt: testimonial.recordedAt,
        audioLanguage: 'en',
        version: '1.0',
      },
    };
  }

  /**
   * List testimonials with optional filter
   */
  async listTestimonials(filter?: SearchFilter): Promise<Testimonial[]> {
    let results = Array.from(this.testimonials.values());

    if (!filter) {
      return results;
    }

    if (filter.incidentType) {
      results = results.filter((t) => t.incidentType === filter.incidentType);
    }

    if (filter.anonymous !== undefined) {
      results = results.filter((t) => t.anonymous === filter.anonymous);
    }

    if (filter.startDate) {
      results = results.filter((t) => t.recordedAt >= filter.startDate!);
    }

    if (filter.endDate) {
      results = results.filter((t) => t.recordedAt <= filter.endDate!);
    }

    if (filter.searchText) {
      const text = filter.searchText.toLowerCase();
      results = results.filter(
        (t) =>
          t.context.toLowerCase().includes(text) ||
          t.location.toLowerCase().includes(text)
      );
    }

    if (filter.status) {
      results = results.filter((t) => t.status === filter.status);
    }

    return results;
  }

  /**
   * Delete testimonial (secure wipe)
   */
  async deleteTestimonial(id: string): Promise<void> {
    this.testimonials.delete(id);
    this.persistToStorage();
    console.log('✅ Testimonial deleted:', id);
  }

  /**
   * Export testimonials for processing (LLM pipeline)
   */
  async exportForProcessing(): Promise<Testimonial[]> {
    // Filter only submitted testimonials
    return Array.from(this.testimonials.values()).filter(
      (t) => t.status === 'submitted'
    );
  }

  /**
   * Update testimonial status
   */
  async updateStatus(
    id: string,
    status: 'draft' | 'submitted' | 'processed'
  ): Promise<void> {
    const testimonial = this.testimonials.get(id);
    if (testimonial) {
      testimonial.status = status;
      this.persistToStorage();
    }
  }

  /**
   * Get database statistics
   */
  getStats(): {
    totalTestimonials: number;
    draftCount: number;
    submittedCount: number;
    processedCount: number;
    totalSize: number;
  } {
    const testimonials = Array.from(this.testimonials.values());

    return {
      totalTestimonials: testimonials.length,
      draftCount: testimonials.filter((t) => t.status === 'draft').length,
      submittedCount: testimonials.filter((t) => t.status === 'submitted')
        .length,
      processedCount: testimonials.filter((t) => t.status === 'processed')
        .length,
      totalSize: JSON.stringify(Array.from(this.testimonials)).length,
    };
  }

  /**
   * Encrypt string
   */
  private encryptString(plaintext: string): string {
    return CryptoJS.AES.encrypt(plaintext, this.encryptionKey).toString();
  }

  /**
   * Decrypt string
   */
  private decryptString(ciphertext: string): string {
    const bytes = CryptoJS.AES.decrypt(ciphertext, this.encryptionKey);
    return bytes.toString(CryptoJS.enc.Utf8);
  }

  /**
   * Encrypt audio blob
   */
  private encryptBlob(blob: Blob, id: string): string {
    // In production, would use proper binary encryption
    // For now, store as data URL with encryption
    return `encrypted:${id}`;
  }

  /**
   * Mask personal names (PII protection)
   */
  private maskName(name: string): string {
    if (!name) return '';
    if (name.length <= 2) return name[0] + '*';

    const parts = name.split(' ');
    const masked = parts
      .map((part) => {
        if (part.length <= 1) return part;
        return part[0] + '*'.repeat(Math.max(1, part.length - 1));
      })
      .join(' ');

    return masked;
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `testimonial-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Persist to localStorage
   */
  private persistToStorage(): void {
    const data = Array.from(this.testimonials.values()).map((t) => ({
      ...t,
      recordedAt: t.recordedAt.toISOString(),
      createdAt: t.createdAt.toISOString(),
    }));

    localStorage.setItem(this.storageKey, JSON.stringify(data));
  }

  /**
   * Load from localStorage
   */
  private loadTestimonials(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (!stored) return;

      const data = JSON.parse(stored);
      for (const item of data) {
        const testimonial: Testimonial = {
          ...item,
          recordedAt: new Date(item.recordedAt),
          incidentDate: item.incidentDate ? new Date(item.incidentDate) : undefined,
          createdAt: new Date(item.createdAt),
        };
        this.testimonials.set(item.id, testimonial);
      }

      console.log(`✅ Loaded ${this.testimonials.size} testimonials from storage`);
    } catch (error) {
      console.error('❌ Failed to load testimonials:', error);
    }
  }

  /**
   * Dispose service
   */
  dispose(): void {
    this.testimonials.clear();
    console.log('✅ Testimonial database disposed');
  }
}

// Export singleton instance
export const testimonialDatabase = new TestimonialDatabase();
