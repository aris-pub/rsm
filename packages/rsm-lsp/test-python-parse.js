#!/usr/bin/env node
/**
 * Test Python parsing directly to verify it works correctly
 */

const { parseWithPython } = require('./dist/layer2/python');

const testDoc = `# Test Document

This is a paragraph.

:theorem: {:label: thm1} This is a theorem.

:proof:
  The proof is trivial.
::

See :ref:thm1:: for details.
`;

async function test() {
  console.log('Testing Python parse with multiline document...\n');

  try {
    const result = await parseWithPython(testDoc);
    console.log('Success! Parsed in', result.elapsed, 'ms\n');
    console.log('AST:', JSON.stringify(result.ast, null, 2));
  } catch (error) {
    console.error('Failed:', error);
    process.exit(1);
  }
}

test();
