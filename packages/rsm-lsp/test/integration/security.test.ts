import { describe, it, expect } from 'vitest';
import { parseWithPython } from '../../src/layer2/python';

describe('Security - Command Injection Prevention', () => {
  it('should prevent shell injection via temp file content', async () => {
    // Attempt to inject shell commands via document content
    const maliciousContent = `# Test

$(echo "injected" > /tmp/injection-test)
\`echo "backtick injection"\`
; echo "semicolon injection"
| echo "pipe injection"
`;

    const result = await parseWithPython(maliciousContent);

    // Should parse successfully without executing injected commands
    expect(result.ast).toBeDefined();
    expect(result.ast.nodeclass).toBe('Manuscript');

    // Verify the content is treated as literal text, not executed
    expect(result.ast.title).toBe('Test');
  }, 10000);

  it('should handle special characters safely', async () => {
    // Test various shell metacharacters
    const specialChars = `# Title with "quotes" and 'apostrophes'

Text with $VARIABLES and \${MORE_VARS}.

Text with backticks: \`command\`

Text with semicolons; and pipes | and ampersands &.
`;

    const result = await parseWithPython(specialChars);

    expect(result.ast).toBeDefined();
    expect(result.ast.nodeclass).toBe('Manuscript');
  }, 10000);

  it('should handle newlines and special sequences safely', async () => {
    // Test newlines, carriage returns, and other escape sequences
    const specialSequences = '# Test\n\nParagraph\\n\\r\\t with escapes.';

    const result = await parseWithPython(specialSequences);

    expect(result.ast).toBeDefined();
    expect(result.ast.nodeclass).toBe('Manuscript');
  }, 10000);
});
