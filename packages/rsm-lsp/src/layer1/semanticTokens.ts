import { Tree } from 'tree-sitter';
import { Query, QueryCapture } from 'tree-sitter';
import { SemanticTokensBuilder } from 'vscode-languageserver';
import { readFileSync } from 'fs';
import { join } from 'path';
import { logger } from '../utils/logger';

// eslint-disable-next-line @typescript-eslint/no-var-requires
const TreeSitterRSM = require('tree-sitter-rsm');

/**
 * LSP Semantic Token Types
 *
 * Standard token types defined by LSP specification.
 * Order determines the token type index sent to clients.
 */
export const TOKEN_TYPES = [
  'namespace',      // 0
  'type',           // 1
  'class',          // 2
  'enum',           // 3
  'interface',      // 4
  'struct',         // 5
  'typeParameter',  // 6
  'parameter',      // 7
  'variable',       // 8
  'property',       // 9
  'enumMember',     // 10
  'event',          // 11
  'function',       // 12
  'method',         // 13
  'macro',          // 14
  'keyword',        // 15
  'modifier',       // 16
  'comment',        // 17
  'string',         // 18
  'number',         // 19
  'regexp',         // 20
  'operator',       // 21
] as const;

/**
 * LSP Semantic Token Modifiers
 *
 * Modifiers provide additional context about tokens.
 */
export const TOKEN_MODIFIERS = [
  'declaration',
  'definition',
  'readonly',
  'static',
  'deprecated',
  'abstract',
  'async',
  'modification',
  'documentation',
  'defaultLibrary',
] as const;

/**
 * Map tree-sitter highlight captures to LSP token types
 *
 * Tree-sitter capture names (from highlights.scm) are mapped to
 * LSP semantic token type indices.
 */
const CAPTURE_TO_TOKEN_TYPE: Record<string, number> = {
  // Keywords
  'keyword': TOKEN_TYPES.indexOf('keyword'),
  'keyword.function': TOKEN_TYPES.indexOf('keyword'),
  'keyword.modifier': TOKEN_TYPES.indexOf('modifier'),
  'keyword.directive': TOKEN_TYPES.indexOf('keyword'),

  // Functions and calls
  'function': TOKEN_TYPES.indexOf('function'),
  'function.builtin': TOKEN_TYPES.indexOf('function'),

  // Types
  'type': TOKEN_TYPES.indexOf('type'),

  // Properties and attributes
  'property': TOKEN_TYPES.indexOf('property'),

  // Strings and literals
  'string': TOKEN_TYPES.indexOf('string'),
  'string.special': TOKEN_TYPES.indexOf('string'),

  // Numbers
  'number': TOKEN_TYPES.indexOf('number'),

  // Comments
  'comment': TOKEN_TYPES.indexOf('comment'),

  // Operators
  'operator': TOKEN_TYPES.indexOf('operator'),

  // Constants
  'constant': TOKEN_TYPES.indexOf('enumMember'),
  'constant.builtin': TOKEN_TYPES.indexOf('enumMember'),

  // Markup (for RSM document structure)
  'markup.heading': TOKEN_TYPES.indexOf('namespace'),
  'markup.heading.1': TOKEN_TYPES.indexOf('namespace'),
  'markup.heading.2': TOKEN_TYPES.indexOf('namespace'),
  'markup.heading.3': TOKEN_TYPES.indexOf('namespace'),
  'markup.heading.4': TOKEN_TYPES.indexOf('namespace'),
  'markup.math': TOKEN_TYPES.indexOf('macro'),
  'markup.raw': TOKEN_TYPES.indexOf('string'),
  'markup.raw.block': TOKEN_TYPES.indexOf('string'),
  'markup.link.url': TOKEN_TYPES.indexOf('string'),

  // Punctuation (map to operator as fallback)
  'punctuation.bracket': TOKEN_TYPES.indexOf('operator'),
  'punctuation.delimiter': TOKEN_TYPES.indexOf('operator'),
  'punctuation.special': TOKEN_TYPES.indexOf('operator'),
};

/**
 * Semantic tokens provider using tree-sitter highlight queries
 */
export class SemanticTokensProvider {
  private query: Query | null = null;

  constructor() {
    this.loadHighlightQuery();
  }

  /**
   * Load highlights.scm query from tree-sitter-rsm package
   */
  private loadHighlightQuery() {
    try {
      // Try multiple paths to support both development and production
      const possiblePaths = [
        // Production: compiled to dist/
        join(__dirname, '../../../tree-sitter-rsm/queries/highlights.scm'),
        // Development: running from src/
        join(__dirname, '../../../../tree-sitter-rsm/queries/highlights.scm'),
        // Alternative: resolve from tree-sitter-rsm package
        join(require.resolve('tree-sitter-rsm'), '../queries/highlights.scm'),
      ];

      let querySource: string | null = null;
      let loadedPath: string | null = null;

      for (const path of possiblePaths) {
        try {
          querySource = readFileSync(path, 'utf8');
          loadedPath = path;
          break;
        } catch {
          // Try next path
          continue;
        }
      }

      if (!querySource || !loadedPath) {
        throw new Error('Could not find highlights.scm in any expected location');
      }

      this.query = new Query(TreeSitterRSM, querySource);

      logger.info(`Loaded highlight query from ${loadedPath} (${querySource.length} bytes)`);
    } catch (error) {
      logger.error('Failed to load highlight query:', error);
      throw error;
    }
  }

  /**
   * Generate semantic tokens for a document
   *
   * @param tree - Parsed tree-sitter tree
   * @returns Builder containing encoded semantic tokens
   */
  provideSemanticTokens(tree: Tree): SemanticTokensBuilder {
    const builder = new SemanticTokensBuilder();

    if (!this.query) {
      logger.warn('No highlight query loaded, returning empty tokens');
      return builder;
    }

    // Execute query to get all captures
    const captures: QueryCapture[] = this.query.captures(tree.rootNode);

    logger.debug(`Processing ${captures.length} highlight captures`);

    // Convert captures to semantic tokens
    for (const capture of captures) {
      const { name, node } = capture;

      // Get token type index from capture name
      const tokenType = CAPTURE_TO_TOKEN_TYPE[name];

      if (tokenType === undefined) {
        // Skip unknown capture types (might be from query but not mapped)
        logger.debug(`Skipping unmapped capture: ${name}`);
        continue;
      }

      const startLine = node.startPosition.row;
      const endLine = node.endPosition.row;

      if (startLine === endLine) {
        // Single-line token: use text length (not byte length) for accuracy
        const len = node.text?.length ?? (node.endIndex - node.startIndex);
        builder.push(startLine, node.startPosition.column, len, tokenType, 0);
      } else {
        // Multi-line token: LSP requires one token per line.
        // Split using the node's text content.
        const lines = (node.text ?? '').split('\n');
        for (let i = 0; i < lines.length; i++) {
          const lineText = lines[i];
          if (!lineText.length) continue;
          const col = i === 0 ? node.startPosition.column : 0;
          builder.push(startLine + i, col, lineText.length, tokenType, 0);
        }
      }
    }

    return builder;
  }
}
