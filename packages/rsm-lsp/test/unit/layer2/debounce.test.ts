import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { Debouncer } from '../../../src/layer2/debounce';

describe('Debouncer', () => {
  let debouncer: Debouncer;

  beforeEach(() => {
    vi.useFakeTimers();
    debouncer = new Debouncer(100);
  });

  afterEach(() => {
    debouncer.cancelAll();
    vi.useRealTimers();
  });

  describe('debounce', () => {
    it('fires callback after delay', async () => {
      const fn = vi.fn();
      debouncer.debounce('key', fn);
      expect(fn).not.toHaveBeenCalled();
      await vi.advanceTimersByTimeAsync(100);
      expect(fn).toHaveBeenCalledOnce();
    });

    it('does not fire before delay elapses', async () => {
      const fn = vi.fn();
      debouncer.debounce('key', fn);
      await vi.advanceTimersByTimeAsync(50);
      expect(fn).not.toHaveBeenCalled();
    });

    it('resets timer on repeated calls — only fires once', async () => {
      const fn = vi.fn();
      debouncer.debounce('key', fn);
      await vi.advanceTimersByTimeAsync(50);
      debouncer.debounce('key', fn);
      await vi.advanceTimersByTimeAsync(50);
      debouncer.debounce('key', fn);
      await vi.advanceTimersByTimeAsync(100);
      expect(fn).toHaveBeenCalledOnce();
    });

    it('uses per-call delay override', async () => {
      const fn = vi.fn();
      debouncer.debounce('key', fn, 200);
      await vi.advanceTimersByTimeAsync(100);
      expect(fn).not.toHaveBeenCalled();
      await vi.advanceTimersByTimeAsync(100);
      expect(fn).toHaveBeenCalledOnce();
    });

    it('fires independently for different keys', async () => {
      const fn1 = vi.fn();
      const fn2 = vi.fn();
      debouncer.debounce('key1', fn1);
      debouncer.debounce('key2', fn2);
      await vi.advanceTimersByTimeAsync(100);
      expect(fn1).toHaveBeenCalledOnce();
      expect(fn2).toHaveBeenCalledOnce();
    });
  });

  describe('cancel', () => {
    it('prevents pending callback from firing', async () => {
      const fn = vi.fn();
      debouncer.debounce('key', fn);
      debouncer.cancel('key');
      await vi.advanceTimersByTimeAsync(100);
      expect(fn).not.toHaveBeenCalled();
    });

    it('is a no-op for unknown key', () => {
      expect(() => debouncer.cancel('nonexistent')).not.toThrow();
    });
  });

  describe('cancelAll', () => {
    it('cancels all pending operations', async () => {
      const fn1 = vi.fn();
      const fn2 = vi.fn();
      debouncer.debounce('key1', fn1);
      debouncer.debounce('key2', fn2);
      debouncer.cancelAll();
      await vi.advanceTimersByTimeAsync(100);
      expect(fn1).not.toHaveBeenCalled();
      expect(fn2).not.toHaveBeenCalled();
    });
  });

  describe('isPending', () => {
    it('returns true while timer is active', () => {
      debouncer.debounce('key', vi.fn());
      expect(debouncer.isPending('key')).toBe(true);
    });

    it('returns false after callback fires', async () => {
      debouncer.debounce('key', vi.fn());
      await vi.advanceTimersByTimeAsync(100);
      expect(debouncer.isPending('key')).toBe(false);
    });

    it('returns false after cancel', () => {
      debouncer.debounce('key', vi.fn());
      debouncer.cancel('key');
      expect(debouncer.isPending('key')).toBe(false);
    });

    it('returns false for unknown key', () => {
      expect(debouncer.isPending('nonexistent')).toBe(false);
    });
  });

  describe('getPending', () => {
    it('returns empty array when nothing is pending', () => {
      expect(debouncer.getPending()).toEqual([]);
    });

    it('returns all pending keys', () => {
      debouncer.debounce('key1', vi.fn());
      debouncer.debounce('key2', vi.fn());
      expect(debouncer.getPending()).toContain('key1');
      expect(debouncer.getPending()).toContain('key2');
    });

    it('excludes cancelled keys', () => {
      debouncer.debounce('key1', vi.fn());
      debouncer.debounce('key2', vi.fn());
      debouncer.cancel('key1');
      expect(debouncer.getPending()).not.toContain('key1');
      expect(debouncer.getPending()).toContain('key2');
    });
  });
});
