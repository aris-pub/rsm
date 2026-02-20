import { describe, it, expect } from 'vitest';
import { RsmParser } from '../../../src/layer1/parser';
import {
  SemanticTokensProvider,
  TOKEN_TYPES,
  TOKEN_MODIFIERS,
} from '../../../src/layer1/semanticTokens';

describe('SemanticTokensProvider', () => {
  const parser = new RsmParser();
  const provider = new SemanticTokensProvider();

  it('should load highlight query successfully', () => {
    expect(provider).toBeDefined();
  });

  it('should provide semantic tokens for document', () => {
    const text = '# Document Title\n\n:theorem:\nSome theorem.\n::';
    const tree = parser.parse(text);

    const builder = provider.provideSemanticTokens(tree);
    const tokens = builder.build();

    expect(tokens).toBeDefined();
    expect(tokens.data).toBeDefined();
    expect(Array.isArray(tokens.data)).toBe(true);
    expect(tokens.data.length).toBeGreaterThan(0);
  });

  it('should generate tokens for keywords', () => {
    const text = ':theorem:\nContent\n::';
    const tree = parser.parse(text);

    const builder = provider.provideSemanticTokens(tree);
    const tokens = builder.build();

    // Should have at least one token (for :theorem:)
    expect(tokens.data.length).toBeGreaterThan(0);
  });

  it('should generate tokens for math blocks', () => {
    const text = '$$\nx^2 + y^2\n$$';
    const tree = parser.parse(text);

    const builder = provider.provideSemanticTokens(tree);
    const tokens = builder.build();

    // Should have tokens for math content
    expect(tokens.data.length).toBeGreaterThan(0);
  });

  it('should generate tokens for references', () => {
    const text = ':ref:thm:main:: is the result.';
    const tree = parser.parse(text);

    const builder = provider.provideSemanticTokens(tree);
    const tokens = builder.build();

    // Should have tokens for :ref: and the label
    expect(tokens.data.length).toBeGreaterThan(0);
  });

  it('should generate tokens for comments', () => {
    const text = '% This is a comment\n:theorem:\nContent\n::';
    const tree = parser.parse(text);

    const builder = provider.provideSemanticTokens(tree);
    const tokens = builder.build();

    // Should have tokens including the comment
    expect(tokens.data.length).toBeGreaterThan(0);
  });

  it('should handle complex documents', () => {
    const text = `# Sample Document

:theorem:{:label:thm:main}
For all $n \\in \\mathbb{N}$, we have $n^2 \\geq 0$.
::

:proof:
:assume: Let $n$ be arbitrary. ::
:claim: $n^2 \\geq 0$. ::
:prove: This follows from axioms. ::
::

:ref:thm:main:: shows the main result.
`;
    const tree = parser.parse(text);

    const builder = provider.provideSemanticTokens(tree);
    const tokens = builder.build();

    // Complex document should have many tokens
    expect(tokens.data.length).toBeGreaterThan(10);

    // Tokens array should be divisible by 5 (encoding format)
    expect(tokens.data.length % 5).toBe(0);
  });

  it('should return empty tokens for empty document', () => {
    const text = '';
    const tree = parser.parse(text);

    const builder = provider.provideSemanticTokens(tree);
    const tokens = builder.build();

    expect(tokens.data).toBeDefined();
    expect(tokens.data.length).toBe(0);
  });

  it('should have valid token types legend', () => {
    expect(TOKEN_TYPES).toBeDefined();
    expect(TOKEN_TYPES.length).toBeGreaterThan(0);
    expect(TOKEN_TYPES).toContain('keyword');
    expect(TOKEN_TYPES).toContain('function');
    expect(TOKEN_TYPES).toContain('string');
    expect(TOKEN_TYPES).toContain('comment');
  });

  it('should have valid token modifiers legend', () => {
    expect(TOKEN_MODIFIERS).toBeDefined();
    expect(TOKEN_MODIFIERS.length).toBeGreaterThan(0);
    expect(TOKEN_MODIFIERS).toContain('declaration');
    expect(TOKEN_MODIFIERS).toContain('readonly');
  });

  it('should encode tokens in LSP delta format', () => {
    const text = ':theorem:\nContent\n::';
    const tree = parser.parse(text);

    const builder = provider.provideSemanticTokens(tree);
    const tokens = builder.build();

    // Each token is 5 integers: [deltaLine, deltaChar, length, tokenType, tokenModifiers]
    expect(tokens.data.length % 5).toBe(0);

    // All values should be non-negative integers
    for (const value of tokens.data) {
      expect(Number.isInteger(value)).toBe(true);
      expect(value).toBeGreaterThanOrEqual(0);
    }
  });
});
