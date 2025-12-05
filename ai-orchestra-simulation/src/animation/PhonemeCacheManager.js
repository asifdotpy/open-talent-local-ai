/**
 * PhonemeCacheManager - Multi-Level Caching System for Phoneme Animation Performance
 *
 * Implements 3-tier caching architecture for Phase 3 performance optimization:
 * - L1: In-memory LRU cache (fastest, limited size)
 * - L2: localStorage (persistent, medium speed)
 * - L3: IndexedDB (large capacity, async)
 *
 * Caches expensive computations: matrix calculations, coarticulation factors,
 * blend states, and precomputed phoneme sequences.
 */

import { Logger } from '../utils/Logger.js';

export class PhonemeCacheManager {
  constructor(config = {}) {
    this.logger = new Logger('PhonemeCacheManager');

    this.config = {
      l1MaxSize: config.l1MaxSize || 100, // Max entries in memory cache
      l2MaxSize: config.l2MaxSize || 500, // Max entries in localStorage
      l3Enabled: config.l3Enabled !== false, // Enable IndexedDB
      cacheExpiryMs: config.cacheExpiryMs || 24 * 60 * 60 * 1000, // 24 hours
      enableCompression: config.enableCompression || false,
      ...config,
    };

    // L1: In-memory LRU cache
    this.l1Cache = new Map();

    // L2: localStorage wrapper
    this.l2Cache = new LocalStorageCache({
      maxSize: this.config.l2MaxSize,
      prefix: 'phoneme_cache_',
      logger: this.logger,
    });

    // L3: IndexedDB wrapper
    this.l3Cache = this.config.l3Enabled ?
      new IndexedDBCache({
        dbName: 'PhonemeCacheDB',
        storeName: 'phonemeCache',
        logger: this.logger,
      }) : null;

    // Cache statistics
    this.stats = {
      l1: { hits: 0, misses: 0, evictions: 0 },
      l2: { hits: 0, misses: 0, evictions: 0 },
      l3: { hits: 0, misses: 0, evictions: 0 },
      totalRequests: 0,
      cacheSize: 0,
    };

    // Cache warming state
    this.warmingInProgress = false;
    this.warmedKeys = new Set();

    this.logger.log('PhonemeCacheManager initialized', {
      l1MaxSize: this.config.l1MaxSize,
      l2MaxSize: this.config.l2MaxSize,
      l3Enabled: this.config.l3Enabled,
    });
  }

  /**
   * Get cached value with multi-level lookup
   * @param {string} key - Cache key
   * @returns {Promise<any>} Cached value or null
   */
  async get(key) {
    this.stats.totalRequests++;

    // L1 lookup (fastest)
    if (this.l1Cache.has(key)) {
      const value = this.l1Cache.get(key);
      if (this.isExpired(value)) {
        this.l1Cache.delete(key);
        this.stats.l1.misses++;
      } else {
        this.stats.l1.hits++;
        this.updateLRU(key); // Move to end (most recently used)
        return value.data;
      }
    }

    // L2 lookup
    const l2Value = this.l2Cache.get(key);
    if (l2Value && !this.isExpired(l2Value)) {
      this.stats.l2.hits++;
      // Promote to L1
      this.setL1(key, l2Value.data, l2Value.timestamp);
      return l2Value.data;
    }

    // L3 lookup (async)
    if (this.l3Cache) {
      try {
        const l3Value = await this.l3Cache.get(key);
        if (l3Value && !this.isExpired(l3Value)) {
          this.stats.l3.hits++;
          // Promote to L1 and L2
          this.setL1(key, l3Value.data, l3Value.timestamp);
          this.l2Cache.set(key, l3Value.data, l3Value.timestamp);
          return l3Value.data;
        }
      } catch (error) {
        this.logger.warn('L3 cache lookup failed', { key, error: error.message });
      }
    }

    // Cache miss
    this.stats.l1.misses++;
    this.stats.l2.misses++;
    this.stats.l3.misses++;
    return null;
  }

  /**
   * Set value in all cache levels
   * @param {string} key - Cache key
   * @param {any} value - Value to cache
   * @param {number} ttlMs - Time to live in milliseconds (optional)
   */
  async set(key, value, ttlMs = null) {
    const timestamp = Date.now();
    const expiry = ttlMs ? timestamp + ttlMs : timestamp + this.config.cacheExpiryMs;

    // L1 (immediate)
    this.setL1(key, value, timestamp, expiry);

    // L2 (immediate)
    this.l2Cache.set(key, value, timestamp, expiry);

    // L3 (async, fire-and-forget)
    if (this.l3Cache) {
      try {
        await this.l3Cache.set(key, value, timestamp, expiry);
      } catch (error) {
        this.logger.warn('L3 cache set failed', { key, error: error.message });
      }
    }

    this.updateCacheSize();
  }

  /**
   * Set value in L1 cache only
   */
  setL1(key, value, timestamp, expiry = null) {
    if (this.l1Cache.size >= this.config.l1MaxSize) {
      // Evict least recently used
      const firstKey = this.l1Cache.keys().next().value;
      this.l1Cache.delete(firstKey);
      this.stats.l1.evictions++;
    }

    this.l1Cache.set(key, {
      data: value,
      timestamp: timestamp,
      expiry: expiry || (timestamp + this.config.cacheExpiryMs),
    });
  }

  /**
   * Update LRU order for L1 cache
   */
  updateLRU(key) {
    const value = this.l1Cache.get(key);
    this.l1Cache.delete(key);
    this.l1Cache.set(key, value);
  }

  /**
   * Check if cached value is expired
   */
  isExpired(cacheEntry) {
    return Date.now() > cacheEntry.expiry;
  }

  /**
   * Delete from all cache levels
   * @param {string} key - Cache key
   */
  async delete(key) {
    this.l1Cache.delete(key);
    this.l2Cache.delete(key);
    if (this.l3Cache) {
      try {
        await this.l3Cache.delete(key);
      } catch (error) {
        this.logger.warn('L3 cache delete failed', { key, error: error.message });
      }
    }
    this.updateCacheSize();
  }

  /**
   * Clear all caches
   */
  async clear() {
    this.l1Cache.clear();
    this.l2Cache.clear();
    if (this.l3Cache) {
      try {
        await this.l3Cache.clear();
      } catch (error) {
        this.logger.warn('L3 cache clear failed', { error: error.message });
      }
    }
    this.warmedKeys.clear();
    this.resetStats();
    this.logger.log('All caches cleared');
  }

  /**
   * Get cache statistics
   */
  async getStats() {
    const l1HitRate = this.stats.totalRequests > 0 ?
      (this.stats.l1.hits / this.stats.totalRequests) : 0;
    const l2HitRate = this.stats.totalRequests > 0 ?
      (this.stats.l2.hits / this.stats.totalRequests) : 0;
    const l3HitRate = this.stats.totalRequests > 0 ?
      (this.stats.l3.hits / this.stats.totalRequests) : 0;

    const l3Size = this.l3Cache ? await this.l3Cache.size() : 0;

    return {
      ...this.stats,
      l1HitRate: l1HitRate.toFixed(3),
      l2HitRate: l2HitRate.toFixed(3),
      l3HitRate: l3HitRate.toFixed(3),
      l1Size: this.l1Cache.size,
      l2Size: this.l2Cache.size(),
      l3Size,
      config: this.config,
    };
  }

  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      l1: { hits: 0, misses: 0, evictions: 0 },
      l2: { hits: 0, misses: 0, evictions: 0 },
      l3: { hits: 0, misses: 0, evictions: 0 },
      totalRequests: 0,
      cacheSize: 0,
    };
  }

  /**
   * Update total cache size estimate
   */
  updateCacheSize() {
    // Rough estimate based on L1 and L2 sizes
    this.stats.cacheSize = this.l1Cache.size + this.l2Cache.size();
  }

  /**
   * Cache warming for common phoneme computations
   * @param {object} phonemeMapper - Reference to PhonemeMapper instance
   */
  async warmCache(phonemeMapper) {
    if (this.warmingInProgress) return;
    this.warmingInProgress = true;

    try {
      this.logger.log('Starting cache warming...');

      // Warm common phoneme mappings
      const commonPhonemes = ['aa', 'eh', 'ih', 'oh', 'uw', 'b', 'd', 'g', 'm', 'n', 'p', 's', 't', 'k'];
      const commonMorphTargets = ['jawOpen', 'mouthClose', 'mouthSmile', 'mouthFunnel'];

      // Precompute intensity matrices for common combinations
      for (const phoneme of commonPhonemes) {
        for (const target of commonMorphTargets) {
          const key = `intensity_${phoneme}_${target}`;
          if (!this.warmedKeys.has(key)) {
            const intensity = phonemeMapper.intensityMatrix?.calculateDynamicIntensity(phoneme, target, {});
            if (intensity !== undefined) {
              await this.set(key, intensity);
              this.warmedKeys.add(key);
            }
          }
        }
      }

      // Warm coarticulation factors for common transitions
      for (let i = 0; i < commonPhonemes.length - 1; i++) {
        const current = commonPhonemes[i];
        const next = commonPhonemes[i + 1];
        const key = `coart_${current}_${next}`;
        if (!this.warmedKeys.has(key)) {
          const factors = phonemeMapper.coarticulationEngine?.getCoarticulationFactors(current, { nextPhoneme: next });
          if (factors) {
            await this.set(key, factors);
            this.warmedKeys.add(key);
          }
        }
      }

      this.logger.log('Cache warming completed', { warmedKeys: this.warmedKeys.size });
    } catch (error) {
      this.logger.error('Cache warming failed', error);
    } finally {
      this.warmingInProgress = false;
    }
  }

  /**
   * Generate cache key for phoneme computations
   * @param {string} type - Computation type (intensity, coart, blend)
   * @param {object} params - Parameters object
   * @returns {string} Cache key
   */
  generateKey(type, params) {
    const paramStr = Object.keys(params)
      .sort()
      .map(key => `${key}:${JSON.stringify(params[key])}`)
      .join('|');
    return `${type}_${paramStr}`;
  }

  /**
   * Compress data if enabled
   * @param {any} data - Data to compress
   * @returns {any} Compressed data or original
   */
  compress(data) {
    if (!this.config.enableCompression) return data;

    // Simple compression for objects (can be enhanced with proper compression)
    if (typeof data === 'object') {
      return JSON.stringify(data);
    }
    return data;
  }

  /**
   * Decompress data if enabled
   * @param {any} data - Data to decompress
   * @returns {any} Decompressed data or original
   */
  decompress(data) {
    if (!this.config.enableCompression) return data;

    // Simple decompression for objects
    if (typeof data === 'string') {
      try {
        return JSON.parse(data);
      } catch {
        return data;
      }
    }
    return data;
  }
}

/**
 * LocalStorage Cache Wrapper with LRU eviction
 */
class LocalStorageCache {
  constructor({ maxSize = 500, prefix = 'cache_', logger }) {
    this.maxSize = maxSize;
    this.prefix = prefix;
    this.logger = logger;
    this.accessOrder = []; // For LRU tracking
  }

  get(key) {
    try {
      const item = localStorage.getItem(this.prefix + key);
      if (!item) return null;

      const parsed = JSON.parse(item);
      if (Date.now() > parsed.expiry) {
        this.delete(key);
        return null;
      }

      // Update access order for LRU
      this.updateAccessOrder(key);
      return parsed;
    } catch (error) {
      this.logger?.warn('LocalStorage get failed', { key, error: error.message });
      return null;
    }
  }

  set(key, value, timestamp, expiry) {
    try {
      const data = { data: value, timestamp, expiry };

      // Check size limit
      if (this.size() >= this.maxSize) {
        this.evictLRU();
      }

      localStorage.setItem(this.prefix + key, JSON.stringify(data));
      this.updateAccessOrder(key);
    } catch (error) {
      this.logger?.warn('LocalStorage set failed', { key, error: error.message });
    }
  }

  delete(key) {
    try {
      localStorage.removeItem(this.prefix + key);
      this.removeFromAccessOrder(key);
    } catch (error) {
      this.logger?.warn('LocalStorage delete failed', { key, error: error.message });
    }
  }

  clear() {
    try {
      const keys = Object.keys(localStorage).filter(key => key.startsWith(this.prefix));
      keys.forEach(key => localStorage.removeItem(key));
      this.accessOrder = [];
    } catch (error) {
      this.logger?.warn('LocalStorage clear failed', { error: error.message });
    }
  }

  size() {
    try {
      return Object.keys(localStorage).filter(key => key.startsWith(this.prefix)).length;
    } catch {
      return 0;
    }
  }

  updateAccessOrder(key) {
    this.removeFromAccessOrder(key);
    this.accessOrder.push(key);
  }

  removeFromAccessOrder(key) {
    const index = this.accessOrder.indexOf(key);
    if (index > -1) {
      this.accessOrder.splice(index, 1);
    }
  }

  evictLRU() {
    if (this.accessOrder.length > 0) {
      const lruKey = this.accessOrder.shift();
      this.delete(lruKey);
    }
  }
}

/**
 * IndexedDB Cache Wrapper for large datasets
 */
class IndexedDBCache {
  constructor({ dbName = 'CacheDB', storeName = 'cache', logger }) {
    this.dbName = dbName;
    this.storeName = storeName;
    this.logger = logger;
    this.dbPromise = this.initDB();
  }

  async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onerror = () => {
        this.logger?.warn('IndexedDB init failed');
        resolve(null); // Graceful degradation
      };

      request.onsuccess = () => resolve(request.result);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          const store = db.createObjectStore(this.storeName, { keyPath: 'key' });
          store.createIndex('expiry', 'expiry', { unique: false });
        }
      };
    });
  }

  async get(key) {
    const db = await this.dbPromise;
    if (!db) return null;

    return new Promise((resolve) => {
      const transaction = db.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.get(key);

      request.onsuccess = () => {
        const result = request.result;
        if (result && Date.now() > result.expiry) {
          this.delete(key); // Clean up expired entry
          resolve(null);
        } else {
          resolve(result || null);
        }
      };

      request.onerror = () => resolve(null);
    });
  }

  async set(key, value, timestamp, expiry) {
    const db = await this.dbPromise;
    if (!db) return;

    return new Promise((resolve) => {
      const transaction = db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const data = { key, data: value, timestamp, expiry };

      const request = store.put(data);
      request.onsuccess = () => resolve();
      request.onerror = () => resolve(); // Silent failure for cache
    });
  }

  async delete(key) {
    const db = await this.dbPromise;
    if (!db) return;

    return new Promise((resolve) => {
      const transaction = db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => resolve();
    });
  }

  async clear() {
    const db = await this.dbPromise;
    if (!db) return;

    return new Promise((resolve) => {
      const transaction = db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => resolve();
    });
  }

  async size() {
    const db = await this.dbPromise;
    if (!db) return 0;

    return new Promise((resolve) => {
      const transaction = db.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.count();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => resolve(0);
    });
  }
}

export default PhonemeCacheManager;