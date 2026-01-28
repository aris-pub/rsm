import Parser, { SyntaxNode, Tree } from 'tree-sitter';
import { Diagnostic, DiagnosticSeverity } from 'vscode-languageserver';
import { pointsToRange } from '../utils/location';
import { logger } from '../utils/logger';

// Import tree-sitter-rsm parser
// eslint-disable-next-line @typescript-eslint/no-var-requires
const TreeSitterRSM = require('tree-sitter-rsm');

/**
 * Wrapper around tree-sitter parser for RSM documents
 * Provides incremental parsing and syntax error detection
 */
export class RsmParser {
  private parser: Parser;

  constructor() {
    this.parser = new Parser();
    try {
      this.parser.setLanguage(TreeSitterRSM.language);
      logger.debug('RSM parser initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize RSM parser:', error);
      throw error;
    }
  }

  /**
   * Parse RSM document text
   * @param text - Document text
   * @param oldTree - Previous parse tree for incremental parsing
   * @returns Parse tree
   */
  parse(text: string, oldTree?: Tree): Tree {
    const startTime = Date.now();
    const tree = this.parser.parse(text, oldTree);
    const elapsed = Date.now() - startTime;
    logger.debug(`Parsed document in ${elapsed}ms`);
    return tree;
  }

  /**
   * Extract syntax errors from parse tree
   * @param tree - Parse tree
   * @returns Array of LSP diagnostics
   */
  getSyntaxErrors(tree: Tree): Diagnostic[] {
    const diagnostics: Diagnostic[] = [];
    this.visitNode(tree.rootNode, (node) => {
      if (node.type === 'ERROR' || node.isMissing) {
        diagnostics.push(this.createSyntaxError(node));
      }
    });
    return diagnostics;
  }

  /**
   * Visit all nodes in tree depth-first
   */
  private visitNode(node: SyntaxNode, callback: (node: SyntaxNode) => void) {
    callback(node);
    for (let i = 0; i < node.childCount; i++) {
      const child = node.child(i);
      if (child) {
        this.visitNode(child, callback);
      }
    }
  }

  /**
   * Create diagnostic for syntax error node
   */
  private createSyntaxError(node: SyntaxNode): Diagnostic {
    const range = pointsToRange(node.startPosition, node.endPosition);
    let message: string;

    if (node.isMissing) {
      message = `Missing ${node.type}`;
    } else {
      message = `Syntax error: unexpected ${node.type}`;

      // Try to provide more helpful context
      if (node.parent) {
        message += ` in ${node.parent.type}`;
      }
    }

    return {
      severity: DiagnosticSeverity.Error,
      range,
      message,
      source: 'rsm-lsp (syntax)',
    };
  }

  /**
   * Find node at given position
   */
  findNodeAt(tree: Tree, line: number, column: number): SyntaxNode | null {
    return tree.rootNode.descendantForPosition({ row: line, column });
  }

  /**
   * Extract all nodes of a given type
   */
  findNodesByType(tree: Tree, type: string): SyntaxNode[] {
    const nodes: SyntaxNode[] = [];
    this.visitNode(tree.rootNode, (node) => {
      if (node.type === type) {
        nodes.push(node);
      }
    });
    return nodes;
  }

  /**
   * Get text content of a node
   */
  getNodeText(node: SyntaxNode, text: string): string {
    return text.substring(node.startIndex, node.endIndex);
  }
}

/**
 * Cache for parsed trees
 * Maps document URI to { tree, version }
 */
export class ParseTreeCache {
  private cache = new Map<string, { tree: Tree; version: number }>();

  set(uri: string, tree: Tree, version: number) {
    this.cache.set(uri, { tree, version });
  }

  get(uri: string): { tree: Tree; version: number } | undefined {
    return this.cache.get(uri);
  }

  delete(uri: string) {
    this.cache.delete(uri);
  }

  clear() {
    this.cache.clear();
  }
}
