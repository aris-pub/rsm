import { describe, it, expect, beforeEach } from 'vitest';
import { ASTCache } from '../../../src/layer2/cache';
import { ASTNode } from '../../../src/layer2/ast';

const makeAST = (title: string): ASTNode => ({
  nodeclass: 'Manuscript',
  start_point: [0, 0],
  end_point: [1, 0],
  title,
  children: [],
});

describe('ASTCache', () => {
  let cache: ASTCache;

  beforeEach(() => {
    cache = new ASTCache();
  });

  describe('get / set', () => {
    it('returns undefined for unknown uri', () => {
      expect(cache.get('file:///unknown.rsm')).toBeUndefined();
    });

    it('returns cached entry after set', () => {
      const ast = makeAST('doc');
      cache.set('file:///doc.rsm', ast, 1);
      const entry = cache.get('file:///doc.rsm');
      expect(entry).toBeDefined();
      expect(entry!.ast).toBe(ast);
      expect(entry!.version).toBe(1);
    });

    it('overwrites existing entry on set', () => {
      cache.set('file:///doc.rsm', makeAST('v1'), 1);
      const ast2 = makeAST('v2');
      cache.set('file:///doc.rsm', ast2, 2);
      const entry = cache.get('file:///doc.rsm');
      expect(entry!.ast).toBe(ast2);
      expect(entry!.version).toBe(2);
    });

    it('stores a timestamp', () => {
      const before = Date.now();
      cache.set('file:///doc.rsm', makeAST('doc'), 1);
      const after = Date.now();
      const entry = cache.get('file:///doc.rsm');
      expect(entry!.timestamp).toBeGreaterThanOrEqual(before);
      expect(entry!.timestamp).toBeLessThanOrEqual(after);
    });
  });

  describe('isValid', () => {
    it('returns false for unknown uri', () => {
      expect(cache.isValid('file:///unknown.rsm', 1)).toBe(false);
    });

    it('returns true when version matches', () => {
      cache.set('file:///doc.rsm', makeAST('doc'), 3);
      expect(cache.isValid('file:///doc.rsm', 3)).toBe(true);
    });

    it('returns false when version does not match', () => {
      cache.set('file:///doc.rsm', makeAST('doc'), 3);
      expect(cache.isValid('file:///doc.rsm', 4)).toBe(false);
    });
  });

  describe('delete', () => {
    it('removes entry', () => {
      cache.set('file:///doc.rsm', makeAST('doc'), 1);
      cache.delete('file:///doc.rsm');
      expect(cache.get('file:///doc.rsm')).toBeUndefined();
    });

    it('is a no-op for unknown uri', () => {
      expect(() => cache.delete('file:///unknown.rsm')).not.toThrow();
    });
  });

  describe('clear', () => {
    it('removes all entries', () => {
      cache.set('file:///a.rsm', makeAST('a'), 1);
      cache.set('file:///b.rsm', makeAST('b'), 1);
      cache.clear();
      expect(cache.stats().size).toBe(0);
    });
  });

  describe('stats', () => {
    it('returns size 0 for empty cache', () => {
      expect(cache.stats()).toEqual({ size: 0, uris: [] });
    });

    it('returns correct size and uris', () => {
      cache.set('file:///a.rsm', makeAST('a'), 1);
      cache.set('file:///b.rsm', makeAST('b'), 1);
      const stats = cache.stats();
      expect(stats.size).toBe(2);
      expect(stats.uris).toContain('file:///a.rsm');
      expect(stats.uris).toContain('file:///b.rsm');
    });
  });
});
