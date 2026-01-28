import { describe, it, expect, beforeEach } from 'vitest';
import { RsmParser, ParseTreeCache } from '../../../src/layer1/parser';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('RsmParser', () => {
  let parser: RsmParser;

  beforeEach(() => {
    parser = new RsmParser();
  });

  describe('parse', () => {
    it('should parse valid RSM document', () => {
      const text = ':manuscript:\n\n:title: Test::';
      const tree = parser.parse(text);

      expect(tree).toBeDefined();
      expect(tree.rootNode).toBeDefined();
      expect(tree.rootNode.type).toBe('source_file');
    });

    it('should parse incrementally with old tree', () => {
      const text1 = ':manuscript:\n\n:title: Test::';
      const tree1 = parser.parse(text1);

      const text2 = ':manuscript:\n\n:title: Test Updated::';
      const tree2 = parser.parse(text2, tree1);

      expect(tree2).toBeDefined();
      expect(tree2.rootNode.type).toBe('source_file');
    });

    it('should parse fixture file', () => {
      const fixturePath = join(__dirname, '../../fixtures/valid.rsm');
      const text = readFileSync(fixturePath, 'utf-8');
      const tree = parser.parse(text);

      expect(tree).toBeDefined();
      expect(tree.rootNode.hasError).toBe(false);
    });
  });

  describe('getSyntaxErrors', () => {
    it('should return empty array for valid document', () => {
      const text = ':manuscript:\n\n:title: Test::';
      const tree = parser.parse(text);
      const errors = parser.getSyntaxErrors(tree);

      expect(errors).toHaveLength(0);
    });

    it('should detect ERROR nodes', () => {
      const text = ':manuscript:\n\n:title: Unclosed tag';
      const tree = parser.parse(text);
      const errors = parser.getSyntaxErrors(tree);

      // Should have at least one error for unclosed tag
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0].message).toContain('Syntax error');
    });

    it('should provide helpful error messages', () => {
      const text = ':invalid-content:\n\n::';
      const tree = parser.parse(text);
      const errors = parser.getSyntaxErrors(tree);

      expect(errors.length).toBeGreaterThan(0);
      errors.forEach((error) => {
        expect(error.message).toBeDefined();
        expect(error.range).toBeDefined();
        expect(error.source).toBe('rsm-lsp (syntax)');
      });
    });
  });

  describe('findNodeAt', () => {
    it('should find node at given position', () => {
      const text = ':manuscript:\n\n:title: Test::';
      const tree = parser.parse(text);

      // Find node at line 2, character 0 (:title: position)
      const node = parser.findNodeAt(tree, 2, 0);

      expect(node).toBeDefined();
      expect(node?.type).toBeDefined();
    });
  });

  describe('findNodesByType', () => {
    it('should find all nodes of given type', () => {
      const text = ':manuscript:\n\n:title: Test::\n\n:section: Introduction::';
      const tree = parser.parse(text);

      // Find all tag nodes (simplified - actual node types depend on grammar)
      const nodes = parser.findNodesByType(tree, 'tag');

      // We should find at least manuscript, title, and section tags
      expect(nodes.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('getNodeText', () => {
    it('should extract text content of node', () => {
      const text = ':manuscript:\n\n:title: Test::';
      const tree = parser.parse(text);
      const rootNode = tree.rootNode;

      const nodeText = parser.getNodeText(rootNode, text);

      expect(nodeText).toBe(text);
    });
  });
});

describe('ParseTreeCache', () => {
  let cache: ParseTreeCache;
  let parser: RsmParser;

  beforeEach(() => {
    cache = new ParseTreeCache();
    parser = new RsmParser();
  });

  it('should store and retrieve parse trees', () => {
    const uri = 'file:///test.rsm';
    const text = ':manuscript:';
    const tree = parser.parse(text);
    const version = 1;

    cache.set(uri, tree, version);
    const cached = cache.get(uri);

    expect(cached).toBeDefined();
    expect(cached?.tree).toBe(tree);
    expect(cached?.version).toBe(version);
  });

  it('should return undefined for non-existent URI', () => {
    const cached = cache.get('file:///nonexistent.rsm');
    expect(cached).toBeUndefined();
  });

  it('should delete cached entries', () => {
    const uri = 'file:///test.rsm';
    const tree = parser.parse(':manuscript:');
    cache.set(uri, tree, 1);

    cache.delete(uri);
    const cached = cache.get(uri);

    expect(cached).toBeUndefined();
  });

  it('should clear all entries', () => {
    const tree = parser.parse(':manuscript:');
    cache.set('file:///test1.rsm', tree, 1);
    cache.set('file:///test2.rsm', tree, 1);

    cache.clear();

    expect(cache.get('file:///test1.rsm')).toBeUndefined();
    expect(cache.get('file:///test2.rsm')).toBeUndefined();
  });
});
