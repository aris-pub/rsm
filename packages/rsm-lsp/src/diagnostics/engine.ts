/**
 * Diagnostic engine - coordinates running all semantic analysis rules
 */

import { Diagnostic } from 'vscode-languageserver';
import { ASTNode } from '../layer2/ast';
import { checkReferences } from './rules/references';
import { checkStructure } from './rules/structure';
import { logger } from '../utils/logger';

/**
 * Run all semantic diagnostics on the AST
 */
export function runSemanticDiagnostics(ast: ASTNode): Diagnostic[] {
  const startTime = Date.now();
  const diagnostics: Diagnostic[] = [];

  try {
    // Run all diagnostic rule sets
    diagnostics.push(...checkReferences(ast));
    diagnostics.push(...checkStructure(ast));

    const elapsed = Date.now() - startTime;
    logger.debug(`Ran semantic diagnostics in ${elapsed}ms, found ${diagnostics.length} issues`);
  } catch (error) {
    logger.error('Error running semantic diagnostics:', error);
  }

  return diagnostics;
}
