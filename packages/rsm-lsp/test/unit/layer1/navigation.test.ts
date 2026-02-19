import { describe, it, expect, beforeEach } from 'vitest';
import { extractLabels, extractReferences } from '../../../src/layer1/navigation';
import { RsmParser } from '../../../src/layer1/parser';

describe('extractLabels', () => {
  let parser: RsmParser;

  beforeEach(() => {
    parser = new RsmParser();
  });

  it('should extract a single label from metadata', () => {
    const text = ':theorem: {\n  :label: thm1\n}\n\nFoo.\n\n::';
    const tree = parser.parse(text);
    const labels = extractLabels(tree, text);

    expect(labels).toHaveLength(1);
    expect(labels[0].name).toBe('thm1');
  });

  it('should extract multiple labels from document', () => {
    const text = ':theorem: {\n  :label: thm1\n}\n\nFoo.\n\n::\n\n:lemma: {\n  :label: lem2\n}\n\nBar.\n\n::';
    const tree = parser.parse(text);
    const labels = extractLabels(tree, text);

    const names = labels.map((l) => l.name);
    expect(names).toContain('thm1');
    expect(names).toContain('lem2');
  });

  it('should return empty array when no labels are defined', () => {
    const text = ':theorem:\n\nFoo.\n\n::';
    const tree = parser.parse(text);
    const labels = extractLabels(tree, text);

    expect(labels).toHaveLength(0);
  });

  it('should include nodeType in returned labels', () => {
    const text = ':theorem: {\n  :label: thm1\n}\n\nFoo.\n\n::';
    const tree = parser.parse(text);
    const labels = extractLabels(tree, text);

    expect(labels[0].nodeType).toBeDefined();
    expect(typeof labels[0].nodeType).toBe('string');
  });

  it('should include a valid range in returned labels', () => {
    const text = ':theorem: {\n  :label: thm1\n}\n\nFoo.\n\n::';
    const tree = parser.parse(text);
    const labels = extractLabels(tree, text);

    const range = labels[0].range;
    expect(range.start).toBeDefined();
    expect(range.end).toBeDefined();
    expect(range.start.line).toBeGreaterThanOrEqual(0);
    expect(range.start.character).toBeGreaterThanOrEqual(0);
  });

  it('should extract labels from the valid fixture', () => {
    const { readFileSync } = require('fs');
    const { join } = require('path');
    const text = readFileSync(join(__dirname, '../../fixtures/valid.rsm'), 'utf-8');
    const tree = parser.parse(text);
    const labels = extractLabels(tree, text);

    const names = labels.map((l) => l.name);
    expect(names).toContain('thm1');
    expect(names).toContain('intro');
  });
});

describe('extractReferences', () => {
  let parser: RsmParser;

  beforeEach(() => {
    parser = new RsmParser();
  });

  it('should extract a single reference', () => {
    const text = ':theorem: {\n  :label: thm1\n}\n\nFoo.\n\n::\n\nSee :ref:thm1::.';
    const tree = parser.parse(text);
    const refs = extractReferences(tree, text);

    const targets = refs.map((r) => r.target);
    expect(targets).toContain('thm1');
  });

  it('should extract multiple references', () => {
    const text = ':theorem: {\n  :label: thm1\n}\n\nFoo.\n\n::\n\n:lemma: {\n  :label: lem2\n}\n\nBar.\n\n::\n\nSee :ref:thm1:: and :ref:lem2::.';
    const tree = parser.parse(text);
    const refs = extractReferences(tree, text);

    const targets = refs.map((r) => r.target);
    expect(targets).toContain('thm1');
    expect(targets).toContain('lem2');
  });

  it('should return empty array when no references exist', () => {
    const text = ':theorem:\n\nFoo.\n\n::';
    const tree = parser.parse(text);
    const refs = extractReferences(tree, text);

    expect(refs).toHaveLength(0);
  });

  it('should include a valid range for each reference', () => {
    const text = ':theorem: {\n  :label: thm1\n}\n\nFoo.\n\n::\n\nSee :ref:thm1::.';
    const tree = parser.parse(text);
    const refs = extractReferences(tree, text);

    const ref = refs.find((r) => r.target === 'thm1');
    expect(ref).toBeDefined();
    expect(ref!.range.start.line).toBeGreaterThanOrEqual(0);
    expect(ref!.range.start.character).toBeGreaterThanOrEqual(0);
  });

  it('should extract references from the valid fixture', () => {
    const { readFileSync } = require('fs');
    const { join } = require('path');
    const text = readFileSync(join(__dirname, '../../fixtures/valid.rsm'), 'utf-8');
    const tree = parser.parse(text);
    const refs = extractReferences(tree, text);

    const targets = refs.map((r) => r.target);
    expect(targets).toContain('thm1');
    expect(targets).toContain('intro');
  });
});
