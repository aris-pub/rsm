import { describe, it, expect } from 'vitest';
import { parseWithPython, testPythonCLI } from '../../../src/layer2/python';

describe('Python subprocess integration', () => {
  it('should parse simple document', async () => {
    const text = '# Test\n\nHello world.';
    const result = await parseWithPython(text);

    expect(result.ast).toBeDefined();
    expect(result.ast.nodeclass).toBe('Manuscript');
    expect(result.ast.title).toBe('Test');
    expect(result.elapsed).toBeGreaterThan(0);
  });

  it('should handle multiline documents', async () => {
    const text = `# Test Document

This is a paragraph.

:theorem: {:label: thm1} This is a theorem.

:proof:
  The proof is trivial.
::
`;
    const result = await parseWithPython(text);

    expect(result.ast.nodeclass).toBe('Manuscript');
    expect(result.ast.title).toBe('Test Document');
    expect(result.ast.children).toBeDefined();
    expect(result.ast.children!.length).toBeGreaterThan(0);
  });

  it('should parse documents with labels', async () => {
    const text = ':theorem: {:label: test-label} Test theorem.';
    const result = await parseWithPython(text);

    expect(result.ast.children).toBeDefined();
    const theorem = result.ast.children![0];
    expect(theorem.nodeclass).toBe('Theorem');
    expect(theorem.label).toBe('test-label');
  });

  it('should handle documents with syntax errors', async () => {
    const text = ':theorem:\n\nUnclosed theorem';
    const result = await parseWithPython(text);

    // Should still parse, but may have Error nodes
    expect(result.ast).toBeDefined();
    expect(result.ast.nodeclass).toBe('Manuscript');
  });

  it('should test if Python CLI is available', async () => {
    const available = await testPythonCLI();
    expect(available).toBe(true);
  });

  it('should handle timeout gracefully', async () => {
    // This test would need a very large document to trigger timeout
    // For now, we just verify the timeout parameter works
    const text = '# Test';
    const result = await parseWithPython(text, 10000); // 10 second timeout
    expect(result.ast).toBeDefined();
  }, 15000);
});
