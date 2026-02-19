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
 * Check for undefined citations.
 *
 * The Python transformer records which bibtex keys failed to resolve as
 * unknownTargetlabels on each Cite node. We surface those as warnings.
 *
 * Note: Cite nodes currently carry start_point [-1, -1] because they are
 * synthetic nodes created after tree transformation rather than directly from
 * the parse tree. Diagnostics for such nodes are skipped until the serializer
 * provides real positions.
 */
export function checkUndefinedCitations(ast: ASTNode): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  for (const cite of findNodesByType(ast, 'Cite')) {
    const unknownLabels = cite.unknownTargetlabels as string[] | undefined;
    if (!unknownLabels || unknownLabels.length === 0) continue;

    if (cite.start_point[0] === -1) continue;

    for (const label of unknownLabels) {
      diagnostics.push({
        severity: DiagnosticSeverity.Warning,
        range: tuplesToRange(cite.start_point, cite.end_point),
        message: `Undefined citation: '${label}'`,
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
