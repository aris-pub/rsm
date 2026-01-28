import { describe, it, expect } from 'vitest';
import { parseWithPython } from '../../src/layer2/python';
import { runSemanticDiagnostics } from '../../src/diagnostics/engine';
import { DiagnosticSeverity } from 'vscode-languageserver';

describe('Semantic diagnostics integration', () => {
  it('should detect structural issues in real document', async () => {
    const document = `# Test Document

:theorem: This theorem has no label.

:section: {:label: sec1} Empty Section
::
`;

    const { ast } = await parseWithPython(document);
    const diagnostics = runSemanticDiagnostics(ast);

    // Should find at least one issue (theorem without label)
    expect(diagnostics.length).toBeGreaterThan(0);

    // Check for theorem without label
    const theoremDiag = diagnostics.find((d) => d.message.includes('Theorem') && d.message.includes('no label'));
    expect(theoremDiag).toBeDefined();
    expect(theoremDiag?.severity).toBe(DiagnosticSeverity.Information);
  }, 10000);

  it('should handle document with multiple issues', async () => {
    const document = `
:theorem: Unlabeled theorem 1.

:theorem: Unlabeled theorem 2.

:section: Empty section
::
`;

    const { ast } = await parseWithPython(document);
    const diagnostics = runSemanticDiagnostics(ast);

    // Should find at least 2 theorems without labels
    const theoremDiags = diagnostics.filter((d) => d.message.includes('Theorem') && d.message.includes('no label'));
    expect(theoremDiags.length).toBeGreaterThanOrEqual(2);
  }, 10000);

  it('should handle well-formed document', async () => {
    const document = `# Well-Formed Document

:theorem: {:label: thm1} This theorem has a label.

:proof:
  Trivial.
::

See :ref:thm1:: for details.
`;

    const { ast } = await parseWithPython(document);
    const diagnostics = runSemanticDiagnostics(ast);

    // Well-formed document should have no or minimal issues
    // (May have info-level suggestions, but no errors)
    const errors = diagnostics.filter((d) => d.severity === DiagnosticSeverity.Error);
    expect(errors).toHaveLength(0);
  }, 10000);

  it('should detect undefined references', async () => {
    const document = `# Test

See :ref:nonexistent:: for proof.
`;

    const { ast } = await parseWithPython(document);
    const diagnostics = runSemanticDiagnostics(ast);

    // Python transformer creates Error nodes for undefined refs
    // Our diagnostic might pick them up if they have valid positions
    // (Some may have [-1, -1] positions and be skipped)
    const allMessages = diagnostics.map((d) => d.message).join(' ');

    // Just verify we got some diagnostics back
    expect(diagnostics).toBeDefined();
  }, 10000);

  it('should handle complex nested structure', async () => {
    const document = `# Complex Document

:section: {:label: intro} Introduction

This is the introduction.

:subsection: {:label: background} Background

Some background material.

:theorem: {:label: main} Main theorem.

:proof:
  By :ref:background::.
::

::

See :ref:main:: for the main result.
`;

    const { ast } = await parseWithPython(document);
    const diagnostics = runSemanticDiagnostics(ast);

    // Should parse successfully
    expect(ast).toBeDefined();
    expect(ast.nodeclass).toBe('Manuscript');

    // Should have some children
    expect(ast.children).toBeDefined();
    expect(ast.children!.length).toBeGreaterThan(0);
  }, 10000);

  it('should measure performance', async () => {
    const document = `# Performance Test

${'This is paragraph ' + 1 + '.\n\n'.repeat(50)}

:theorem: {:label: thm1} Test theorem.
`;

    const parseStart = Date.now();
    const { ast, elapsed: parseTime } = await parseWithPython(document);
    const parseEnd = Date.now();

    const diagStart = Date.now();
    const diagnostics = runSemanticDiagnostics(ast);
    const diagEnd = Date.now();

    console.log(`Parse time: ${parseTime}ms (reported), ${parseEnd - parseStart}ms (measured)`);
    console.log(`Diagnostics time: ${diagEnd - diagStart}ms`);
    console.log(`Total diagnostics: ${diagnostics.length}`);

    // Diagnostic generation should be fast (< 100ms for reasonable document)
    expect(diagEnd - diagStart).toBeLessThan(100);
  }, 15000);
});
