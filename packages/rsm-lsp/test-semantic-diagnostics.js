#!/usr/bin/env node
/**
 * Test semantic diagnostics
 */

const { parseWithPython } = require('./dist/layer2/python');
const { runSemanticDiagnostics } = require('./dist/diagnostics/engine');

const testDoc = `# Test Document

This is a paragraph.

:theorem: {:label: thm1} This is a theorem.

:proof:
  See :ref:nonexistent:: for the proof.
::

Another :ref:thm1:: reference.

:theorem: This theorem has no label.
`;

async function test() {
  console.log('Testing semantic diagnostics...\n');

  try {
    // Parse document
    const { ast, elapsed } = await parseWithPython(testDoc);
    console.log(`Parsed in ${elapsed}ms\n`);

    // Run semantic diagnostics
    const diagnostics = runSemanticDiagnostics(ast);

    console.log(`Found ${diagnostics.length} semantic issues:\n`);

    for (const diag of diagnostics) {
      const severity = ['ERROR', 'WARNING', 'INFO', 'HINT'][diag.severity - 1];
      const line = diag.range.start.line + 1;
      console.log(`[${severity}] Line ${line}: ${diag.message}`);
    }

    console.log('\nExpected:');
    console.log('- Undefined reference: nonexistent');
    console.log('- Theorem has no label (line 20)');
    console.log('- Unused label: thm1 (should NOT appear - it is used!)');
  } catch (error) {
    console.error('Failed:', error);
    process.exit(1);
  }
}

test();
