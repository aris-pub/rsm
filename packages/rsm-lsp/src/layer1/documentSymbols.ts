import { Tree, SyntaxNode } from 'tree-sitter';
import { DocumentSymbol, SymbolKind, Range } from 'vscode-languageserver';
import { pointsToRange } from '../utils/location';
import { logger } from '../utils/logger';

/**
 * Map RSM node types to LSP SymbolKind
 *
 * This mapping determines how different RSM constructs appear
 * in outline views and other LSP clients.
 */
const NODE_TYPE_TO_SYMBOL_KIND: Record<string, SymbolKind> = {
  // Document structure - Modules
  source_file: SymbolKind.Module,
  section: SymbolKind.Module,
  subsection: SymbolKind.Module,
  subsubsection: SymbolKind.Module,
  appendix: SymbolKind.Module,

  // Mathematical constructs - Classes
  theorem: SymbolKind.Class,
  lemma: SymbolKind.Class,
  corollary: SymbolKind.Class,
  proposition: SymbolKind.Class,

  // Definitions - Structs
  definition: SymbolKind.Struct,

  // Proofs and reasoning - Functions
  proof: SymbolKind.Function,
  sketch: SymbolKind.Function,
  subproof: SymbolKind.Function,

  // Proof steps - Methods
  step: SymbolKind.Method,

  // Examples and remarks - Objects
  example: SymbolKind.Object,
  remark: SymbolKind.Object,

  // Figures and media - Constants
  figure: SymbolKind.Constant,
  video: SymbolKind.Constant,
  table: SymbolKind.Constant,

  // Abstract and metadata - Namespace
  abstract: SymbolKind.Namespace,
  author: SymbolKind.Namespace,

  // Bibliography - Array
  references: SymbolKind.Array,
  bibitem: SymbolKind.Object,
};

/**
 * Node types that should be included as document symbols
 */
const SYMBOL_NODE_TYPES = new Set(Object.keys(NODE_TYPE_TO_SYMBOL_KIND));

/**
 * Node types that can contain other symbols (for hierarchy)
 */
const CONTAINER_NODE_TYPES = new Set([
  'source_file',
  'section',
  'subsection',
  'subsubsection',
  'theorem',
  'lemma',
  'corollary',
  'proposition',
  'proof',
  'sketch',
  'subproof',
  'step',
  'definition',
  'example',
  'remark',
  'figure',
  'table',
  'references',
]);

/**
 * Extract the title/name for a symbol from its node
 */
function extractSymbolName(node: SyntaxNode, text: string): string {
  // Try to get title from named field
  const titleNode = node.childForFieldName('title');
  if (titleNode) {
    return text.substring(titleNode.startIndex, titleNode.endIndex).trim();
  }

  // For nodes with meta, try to get label or name
  const metaNode = node.childForFieldName('meta');
  if (metaNode) {
    // Look for :label: or :name: in meta
    for (let i = 0; i < metaNode.childCount; i++) {
      const pairNode = metaNode.child(i);
      if (!pairNode || pairNode.type !== 'pair') continue;

      // Get the metakey (first child of pair)
      const keyNode = pairNode.child(0);
      if (!keyNode) continue;

      // Check if this is a metakey_text containing label or name
      if (keyNode.type === 'metakey_text') {
        const labelOrName = keyNode.child(0);
        if (labelOrName && (labelOrName.type === 'label' || labelOrName.type === 'name')) {
          // Get the metaval (second child of pair)
          const valueNode = pairNode.child(1);
          if (valueNode && valueNode.type === 'metaval_text') {
            return text.substring(valueNode.startIndex, valueNode.endIndex).trim();
          }
        }
      }
    }
  }

  // For bibitem, extract the label
  if (node.type === 'bibitem') {
    const labelNode = node.childForFieldName('label');
    if (labelNode) {
      return text.substring(labelNode.startIndex, labelNode.endIndex).trim();
    }
  }

  // Default name based on node type
  const typeToDefaultName: Record<string, string> = {
    theorem: 'Theorem',
    lemma: 'Lemma',
    corollary: 'Corollary',
    proposition: 'Proposition',
    definition: 'Definition',
    proof: 'Proof',
    sketch: 'Sketch',
    subproof: 'Subproof',
    step: 'Step',
    example: 'Example',
    remark: 'Remark',
    figure: 'Figure',
    video: 'Video',
    table: 'Table',
    abstract: 'Abstract',
    author: 'Author',
    references: 'References',
    appendix: 'Appendix',
    section: 'Section',
    subsection: 'Subsection',
    subsubsection: 'Subsubsection',
  };

  // Use effective type for default name
  const effectiveType = getEffectiveNodeType(node);
  return typeToDefaultName[effectiveType] || effectiveType;
}

/**
 * Extract detail string for a symbol
 */
function extractSymbolDetail(node: SyntaxNode, text: string): string | undefined {
  const effectiveType = getEffectiveNodeType(node);

  // For theorems/lemmas/etc, show first line of content
  if (
    effectiveType === 'theorem' ||
    effectiveType === 'lemma' ||
    effectiveType === 'corollary' ||
    effectiveType === 'proposition' ||
    effectiveType === 'definition'
  ) {
    // Get first text child
    for (let i = 0; i < node.childCount; i++) {
      const child = node.child(i);
      if (child && child.type === 'text') {
        const content = text.substring(child.startIndex, child.endIndex).trim();
        // Return first 50 chars
        return content.length > 50 ? content.substring(0, 50) + '...' : content;
      }
    }
  }

  return undefined;
}

/**
 * Get the effective node type for symbol extraction
 *
 * For block nodes, return the tag type (theorem, proof, etc.)
 * For other nodes, return the node type directly
 */
function getEffectiveNodeType(node: SyntaxNode): string {
  // For block nodes, get the tag type
  if (node.type === 'block') {
    const tagNode = node.childForFieldName('tag');
    if (tagNode) {
      return tagNode.type;
    }
  }

  // For section/subsection/subsubsection, return directly
  return node.type;
}

/**
 * Build a DocumentSymbol from a tree-sitter node
 */
function buildDocumentSymbol(node: SyntaxNode, text: string): DocumentSymbol | null {
  const effectiveType = getEffectiveNodeType(node);
  const symbolKind = NODE_TYPE_TO_SYMBOL_KIND[effectiveType];

  if (symbolKind === undefined) {
    return null;
  }

  const name = extractSymbolName(node, text);
  const detail = extractSymbolDetail(node, text);
  const range = pointsToRange(node.startPosition, node.endPosition);

  // Selection range is the name/title if available, otherwise the whole node
  let selectionRange: Range = range;
  const titleNode = node.childForFieldName('title');
  if (titleNode) {
    selectionRange = pointsToRange(titleNode.startPosition, titleNode.endPosition);
  }

  const symbol: DocumentSymbol = {
    name,
    kind: symbolKind,
    range,
    selectionRange,
  };

  if (detail) {
    symbol.detail = detail;
  }

  // Recursively add children if this is a container
  if (CONTAINER_NODE_TYPES.has(effectiveType)) {
    const children: DocumentSymbol[] = [];

    for (let i = 0; i < node.childCount; i++) {
      const child = node.child(i);
      if (!child) continue;

      // Skip meta, tag, and other non-content nodes
      if (child.type === 'meta' || child.type === 'blockmeta' || child.type === 'inlinemeta') {
        continue;
      }

      // Recursively process child symbols
      const childSymbol = buildDocumentSymbol(child, text);
      if (childSymbol) {
        children.push(childSymbol);
      } else if (CONTAINER_NODE_TYPES.has(child.type)) {
        // If child is a container but didn't produce a symbol,
        // still process its children
        for (let j = 0; j < child.childCount; j++) {
          const grandchild = child.child(j);
          if (!grandchild) continue;
          const grandchildSymbol = buildDocumentSymbol(grandchild, text);
          if (grandchildSymbol) {
            children.push(grandchildSymbol);
          }
        }
      }
    }

    if (children.length > 0) {
      symbol.children = children;
    }
  }

  return symbol;
}

/**
 * Extract document symbols from a parse tree
 *
 * This provides the structure for outline views, breadcrumbs,
 * and "Go to Symbol" features in LSP clients.
 */
export function extractDocumentSymbols(tree: Tree, text: string): DocumentSymbol[] {
  const symbols: DocumentSymbol[] = [];

  logger.debug('Extracting document symbols from tree');

  // Process the root node's children
  const root = tree.rootNode;

  for (let i = 0; i < root.childCount; i++) {
    const child = root.child(i);
    if (!child) continue;

    const symbol = buildDocumentSymbol(child, text);
    if (symbol) {
      symbols.push(symbol);
    }
  }

  logger.debug(`Extracted ${symbols.length} top-level symbols`);

  return symbols;
}
