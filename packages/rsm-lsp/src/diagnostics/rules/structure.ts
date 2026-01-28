/**
 * Semantic diagnostics for document structure
 */

import { Diagnostic, DiagnosticSeverity } from 'vscode-languageserver';
import { ASTNode, findNodesByType, isNodeOfType } from '../../layer2/ast';
import { tuplesToRange } from '../../utils/location';

/**
 * Check if manuscript has a title
 */
export function checkMissingTitle(ast: ASTNode): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  if (isNodeOfType(ast, 'Manuscript')) {
    if (!ast.title || ast.title.trim() === '') {
      diagnostics.push({
        severity: DiagnosticSeverity.Warning,
        range: tuplesToRange(ast.start_point, ast.start_point),
        message: 'Manuscript is missing a title',
        source: 'rsm-lsp (semantic)',
      });
    }
  }

  return diagnostics;
}

/**
 * Check for sections without labels
 */
export function checkSectionsWithoutLabels(ast: ASTNode): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  const sections = findNodesByType(ast, 'Section');

  for (const section of sections) {
    if (!section.label) {
      const title = section.title || 'Untitled Section';
      diagnostics.push({
        severity: DiagnosticSeverity.Information,
        range: tuplesToRange(section.start_point, section.end_point),
        message: `Section "${title}" has no label`,
        source: 'rsm-lsp (semantic)',
      });
    }
  }

  return diagnostics;
}

/**
 * Check for theorems/definitions without labels
 */
export function checkTheoremsWithoutLabels(ast: ASTNode): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  const theoremTypes = ['Theorem', 'Lemma', 'Proposition', 'Corollary', 'Definition'];

  for (const type of theoremTypes) {
    const nodes = findNodesByType(ast, type);

    for (const node of nodes) {
      if (!node.label) {
        diagnostics.push({
          severity: DiagnosticSeverity.Information,
          range: tuplesToRange(node.start_point, node.end_point),
          message: `${type} has no label (recommended for cross-referencing)`,
          source: 'rsm-lsp (semantic)',
        });
      }
    }
  }

  return diagnostics;
}

/**
 * Check for empty sections
 */
export function checkEmptySections(ast: ASTNode): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];

  const sections = findNodesByType(ast, 'Section');

  for (const section of sections) {
    if (!section.children || section.children.length === 0) {
      const title = section.title || 'Untitled Section';
      diagnostics.push({
        severity: DiagnosticSeverity.Warning,
        range: tuplesToRange(section.start_point, section.end_point),
        message: `Section "${title}" is empty`,
        source: 'rsm-lsp (semantic)',
      });
    }
  }

  return diagnostics;
}

/**
 * Run all structure-related diagnostics
 */
export function checkStructure(ast: ASTNode): Diagnostic[] {
  return [
    ...checkMissingTitle(ast),
    ...checkSectionsWithoutLabels(ast),
    ...checkTheoremsWithoutLabels(ast),
    ...checkEmptySections(ast),
  ];
}
