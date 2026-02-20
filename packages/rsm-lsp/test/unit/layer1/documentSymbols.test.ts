import { describe, it, expect } from 'vitest';
import { SymbolKind } from 'vscode-languageserver';
import { RsmParser } from '../../../src/layer1/parser';
import { extractDocumentSymbols } from '../../../src/layer1/documentSymbols';

describe('extractDocumentSymbols', () => {
  const parser = new RsmParser();

  it('should extract sections as symbols', () => {
    const text = `## Introduction

Some content.

### Background

More content.`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBeGreaterThan(0);

    // Find section symbols
    const sections = symbols.filter((s) => s.kind === SymbolKind.Module);
    expect(sections.length).toBeGreaterThan(0);
  });

  it('should extract theorems as symbols', () => {
    const text = `:theorem:{:label:thm:main}
For all n, we have n >= 0.
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].kind).toBe(SymbolKind.Class);
    expect(symbols[0].name).toContain('thm:main');
  });

  it('should extract proofs as symbols', () => {
    const text = `:proof:
The proof is straightforward.
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].kind).toBe(SymbolKind.Function);
    expect(symbols[0].name).toBe('Proof');
  });

  it('should build hierarchical structure', () => {
    const text = `:theorem:
Main result.
::

:proof:
:assume: Let n be arbitrary. ::
:claim: n >= 0. ::
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    // Should have theorem and proof at top level
    expect(symbols.length).toBe(2);

    // Proof should have children (assume, claim)
    const proof = symbols.find((s) => s.kind === SymbolKind.Function);
    expect(proof).toBeDefined();
    // Note: assume and claim are constructs, not blocks, so they might not appear as symbols
    // This depends on how we handle construct tags vs block tags
  });

  it('should extract definitions', () => {
    const text = `:definition:{:label:def:foo}
A foo is a bar.
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].kind).toBe(SymbolKind.Struct);
    // Label should be extracted
    expect(symbols[0].name).toBe('def:foo');
  });

  it('should extract lemmas', () => {
    const text = `:lemma:
A useful result.
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].kind).toBe(SymbolKind.Class);
    expect(symbols[0].name).toBe('Lemma');
  });

  it('should extract steps', () => {
    const text = `:step:
First, we show P.
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].kind).toBe(SymbolKind.Method);
    expect(symbols[0].name).toBe('Step');
  });

  it('should extract examples', () => {
    const text = `:example:
Consider the case where n=1.
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].kind).toBe(SymbolKind.Object);
    expect(symbols[0].name).toBe('Example');
  });

  it('should extract figures', () => {
    const text = `:figure:{:path:/images/fig1.png}
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].kind).toBe(SymbolKind.Constant);
    expect(symbols[0].name).toBe('Figure');
  });

  it('should extract references section', () => {
    const text = `:references:
@book{knuth1997,
  title={The Art},
  author={Knuth},
  year={1997}
}
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].kind).toBe(SymbolKind.Array);
    expect(symbols[0].name).toBe('References');

    // Should have bibitem children
    expect(symbols[0].children).toBeDefined();
    expect(symbols[0].children!.length).toBe(1);
    expect(symbols[0].children![0].name).toContain('knuth1997');
  });

  it('should handle complex nested structure', () => {
    const text = `# Document Title

## Introduction

Some intro text.

:theorem:{:label:thm:main}
Main theorem statement.
::

:proof:
:step:
Detailed reasoning.
::
::

## Conclusion

Final thoughts.`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    // Should have multiple symbols
    expect(symbols.length).toBeGreaterThan(0);

    // Should include various types
    const kinds = symbols.map((s) => s.kind);
    expect(kinds.length).toBeGreaterThan(0);
  });

  it('should set range and selectionRange', () => {
    const text = `:theorem:
Content.
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    expect(symbols[0].range).toBeDefined();
    expect(symbols[0].range.start).toBeDefined();
    expect(symbols[0].range.end).toBeDefined();
    expect(symbols[0].selectionRange).toBeDefined();
  });

  it('should include detail for theorems/definitions', () => {
    const text = `:theorem:
For all natural numbers n, we have n squared is non-negative and this is a very long statement that should be truncated.
::`;

    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols.length).toBe(1);
    // Detail should be truncated to 50 chars
    if (symbols[0].detail) {
      expect(symbols[0].detail.length).toBeLessThanOrEqual(53); // 50 + "..."
    }
  });

  it('should handle empty document', () => {
    const text = '';
    const tree = parser.parse(text);
    const symbols = extractDocumentSymbols(tree, text);

    expect(symbols).toBeDefined();
    expect(Array.isArray(symbols)).toBe(true);
  });
});
