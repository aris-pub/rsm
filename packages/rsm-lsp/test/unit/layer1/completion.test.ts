import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import { getTagCompletions, getPartialTag } from '../../../src/layer1/completion';
import { CompletionItemKind } from 'vscode-languageserver';

const GRAMMAR_PATH = resolve(__dirname, '../../../../../tree-sitter-rsm/grammar.js');

// Every tag and meta key in the grammar is written as a quoted string such as
// ':theorem:' or ':as-paragraph:'. Other quoted strings (the Halmos '::' and the
// item markers ':-:', ':--:', ':---:') do not start with a letter after the colon.
function grammarTags(): string[] {
  const source = readFileSync(GRAMMAR_PATH, 'utf8');
  const tags = new Set<string>();
  for (const match of source.matchAll(/['"](:[a-z][a-z0-9-]*:)['"]/g)) {
    tags.add(match[1]);
  }
  return [...tags].sort();
}

describe('getTagCompletions', () => {
  it('should return all tags when no filter provided', () => {
    const completions = getTagCompletions();

    expect(completions.length).toBeGreaterThan(0);
    expect(completions.every((c) => c.kind === CompletionItemKind.Keyword)).toBe(true);
    expect(completions.every((c) => c.label.startsWith(':'))).toBe(true);
  });

  it('should filter tags by partial input', () => {
    const completions = getTagCompletions(':the');

    expect(completions.length).toBeGreaterThan(0);
    expect(completions.some((c) => c.label === ':theorem:')).toBe(true);
    expect(completions.every((c) => c.label.startsWith(':the'))).toBe(true);
  });

  it('should be case insensitive', () => {
    const lower = getTagCompletions(':the');
    const upper = getTagCompletions(':THE');

    expect(lower).toEqual(upper);
  });

  it('should return specific tags for exact matches', () => {
    const completions = getTagCompletions(':proof');

    expect(completions.length).toBe(1);
    expect(completions[0].label).toBe(':proof:');
    expect(completions[0].detail).toBeDefined();
  });

  it('should return empty array for non-matching filter', () => {
    const completions = getTagCompletions(':nonexistent');

    expect(completions).toHaveLength(0);
  });

  it('should include common tags', () => {
    const allCompletions = getTagCompletions();
    const labels = allCompletions.map((c) => c.label);

    expect(labels).toContain(':section:');
    expect(labels).toContain(':theorem:');
    expect(labels).toContain(':proof:');
    expect(labels).toContain(':definition:');
    expect(labels).toContain(':lemma:');
    expect(labels).toContain(':ref:');
    expect(labels).toContain(':cite:');
  });

  it('should include proof constructs', () => {
    const allCompletions = getTagCompletions();
    const labels = allCompletions.map((c) => c.label);

    expect(labels).toContain(':claim:');
    expect(labels).toContain(':step:');
    expect(labels).toContain(':p:');
    expect(labels).toContain(':qed:');
    expect(labels).toContain(':let:');
    expect(labels).toContain(':assume:');
  });
});

describe('tag list matches tree-sitter-rsm/grammar.js', () => {
  const labels = getTagCompletions().map((c) => c.label);

  it('finds tags in the grammar', () => {
    expect(grammarTags()).toContain(':theorem:');
    expect(grammarTags().length).toBeGreaterThan(80);
  });

  it('offers every tag and meta key defined by the grammar', () => {
    const missing = grammarTags().filter((t) => !labels.includes(t));
    expect(missing).toEqual([]);
  });

  it('offers nothing that the grammar does not define', () => {
    const grammar = grammarTags();
    const extra = labels.filter((t) => !grammar.includes(t));
    expect(extra).toEqual([]);
  });

  it('offers each tag once', () => {
    expect(new Set(labels).size).toBe(labels.length);
  });

  it('offers :rawhtml: and other tags missing before', () => {
    for (const tag of [':rawhtml:', ':html:', ':video:', ':calc:', ':case:', ':suffices:',
      ':wlog:', ':span:', ':sketch:', ':as-paragraph:', ':goal:']) {
      expect(labels).toContain(tag);
    }
  });

  it('does not offer tags that are not in the grammar', () => {
    for (const tag of [':manuscript:', ':conjecture:', ':eqref:', ':item:', ':date:',
      ':bibitem:', ':emph:', ':todo:']) {
      expect(labels).not.toContain(tag);
    }
  });

  it('gives every tag a description', () => {
    expect(getTagCompletions().every((c) => typeof c.detail === 'string' && c.detail.length > 0)).toBe(true);
  });
});

describe('getPartialTag', () => {
  it('should detect partial tag after colon', () => {
    const line = 'Some text :the';
    const partial = getPartialTag(line, line.length);

    expect(partial).toBe(':the');
  });

  it('should detect colon only', () => {
    const line = 'Some text :';
    const partial = getPartialTag(line, line.length);

    expect(partial).toBe(':');
  });

  it('should return null when not after colon', () => {
    const line = 'Some text';
    const partial = getPartialTag(line, line.length);

    expect(partial).toBeNull();
  });

  it('should return null when colon not followed by lowercase letters', () => {
    const line = 'Some text :123';
    const partial = getPartialTag(line, line.length);

    expect(partial).toBeNull();
  });

  it('should handle colon at start of line', () => {
    const line = ':pro';
    const partial = getPartialTag(line, line.length);

    expect(partial).toBe(':pro');
  });

  it('should handle multiple colons', () => {
    const line = ':theorem: something :ref';
    const partial = getPartialTag(line, line.length);

    expect(partial).toBe(':ref');
  });

  it('should respect cursor position', () => {
    const line = ':theorem: something :ref';
    const partial = getPartialTag(line, 8); // Position after ':theorem'

    expect(partial).toBe(':theorem');
  });
});
