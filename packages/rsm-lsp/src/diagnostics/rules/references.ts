/**
 * Semantic diagnostics for references and citations
 */

import { Diagnostic, DiagnosticSeverity } from 'vscode-languageserver';
import { ASTNode, findNodesByType, extractLabels, extractReferences } from '../../layer2/ast';
import { tuplesToRange } from '../../utils/location';

/**
 * Check for undefined label references
 *
 * Note: The Python transformer already detects undefined references
 * and converts them to Error nodes with text like "[unknown label \"foo\"]"
 */
export function checkUndefinedReferences(ast: ASTNode): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  // Find all Error nodes
  const errors = findNodesByType(ast, 'Error');

  // Check for undefined reference errors
  for (const error of errors) {
    const text = error.text as string;
    if (text && text.includes('[unknown label')) {
      // Extract label name from error message: [unknown label "foo"]
      const match = text.match(/\[unknown label "([^"]+)"\]/);
      const label = match ? match[1] : 'unknown';

      // Find parent to get better position information
      // For now, we'll skip diagnostics for Error nodes with [-1, -1] positions
      // since we can't accurately position them in the editor
      if (error.start_point[0] === -1) {
        continue;
      }

      diagnostics.push({
        severity: DiagnosticSeverity.Error,
        range: tuplesToRange(error.start_point, error.end_point),
        message: `Undefined reference: '${label}'`,
        source: 'rsm-lsp (semantic)',
      });
    }
  }

  return diagnostics;
}

/**
 * Check for undefined citations
 */
export function checkUndefinedCitations(ast: ASTNode): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  // Find all Cite nodes
  const citations = findNodesByType(ast, 'Cite');

  // Find the References section (bibliography)
  const referencesNodes = findNodesByType(ast, 'References');
  const bibEntries = new Set<string>();

  // Extract bibliography entries from References node
  if (referencesNodes.length > 0) {
    // TODO: Extract actual bib entries from the References node
    // For now, we'll skip this check until we understand the structure better
    return diagnostics;
  }

  // Check each citation
  for (const cite of citations) {
    const target = cite.target as string;
    if (target && !bibEntries.has(target)) {
      diagnostics.push({
        severity: DiagnosticSeverity.Warning,
        range: tuplesToRange(cite.start_point, cite.end_point),
        message: `Undefined citation: '${target}'`,
        source: 'rsm-lsp (semantic)',
      });
    }
  }

  return diagnostics;
}

/**
 * Check for unused labels
 */
export function checkUnusedLabels(ast: ASTNode): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  // Extract all labels
  const labels = extractLabels(ast);

  // Extract all references
  const references = extractReferences(ast);
  const referencedLabels = new Set(references.map((r) => r.target));

  // Check each label
  for (const [label, node] of labels.entries()) {
    if (!referencedLabels.has(label)) {
      diagnostics.push({
        severity: DiagnosticSeverity.Information,
        range: tuplesToRange(node.start_point, node.end_point),
        message: `Unused label: '${label}'`,
        source: 'rsm-lsp (semantic)',
      });
    }
  }

  return diagnostics;
}

/**
 * Run all reference-related diagnostics
 */
export function checkReferences(ast: ASTNode): Diagnostic[] {
  return [
    ...checkUndefinedReferences(ast),
    ...checkUndefinedCitations(ast),
    // Skip unused labels check - Python transformer has already resolved references
    // so we can't easily determine which labels are referenced
    // ...checkUnusedLabels(ast),
  ];
}
