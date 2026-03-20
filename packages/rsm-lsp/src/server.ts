#!/usr/bin/env node

import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  InitializeParams,
  TextDocumentSyncKind,
  InitializeResult,
  CompletionParams,
  CompletionItem,
  DefinitionParams,
  Location,
  SemanticTokensParams,
  SemanticTokens,
  SemanticTokensLegend,
  DocumentSymbolParams,
  DocumentSymbol,
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';
import { RsmParser, ParseTreeCache } from './layer1/parser';
import { getTagCompletions, getPartialTag } from './layer1/completion';
import { extractLabels, extractReferences } from './layer1/navigation';
import {
  SemanticTokensProvider,
  TOKEN_TYPES,
  TOKEN_MODIFIERS,
} from './layer1/semanticTokens';
import { extractDocumentSymbols } from './layer1/documentSymbols';
import { parseWithPython } from './layer2/python';
import { ASTCache, Debouncer } from './layer2';
import { runSemanticDiagnostics } from './diagnostics/engine';
import { isPositionInRange } from './utils/location';
import { logger } from './utils/logger';

// Create LSP connection
const connection = createConnection(ProposedFeatures.all);

// Create document manager
const documents = new TextDocuments(TextDocument);

// Layer 1: Tree-sitter parser and cache
const parser = new RsmParser();
const parseCache = new ParseTreeCache();
const semanticTokensProvider = new SemanticTokensProvider();

// Layer 2: Python AST cache and debouncer
const astCache = new ASTCache();
const debouncer = new Debouncer(500); // 500ms debounce

// Initialize server
connection.onInitialize((_params: InitializeParams) => {
  logger.info('Initializing RSM Language Server');

  // Define semantic tokens legend
  const legend: SemanticTokensLegend = {
    tokenTypes: [...TOKEN_TYPES],
    tokenModifiers: [...TOKEN_MODIFIERS],
  };

  const result: InitializeResult = {
    capabilities: {
      textDocumentSync: TextDocumentSyncKind.Incremental,
      completionProvider: {
        triggerCharacters: [':'],
      },
      definitionProvider: true,
      semanticTokensProvider: {
        legend,
        full: true,
        range: false,
      },
      documentSymbolProvider: true,
    },
  };

  return result;
});

connection.onInitialized(() => {
  logger.info('RSM Language Server initialized');
});

/**
 * Validate document (Layer 1: syntax checking)
 */
function validateDocument(document: TextDocument) {
  const text = document.getText();
  const uri = document.uri;
  const version = document.version;

  // Get old tree for incremental parsing
  const cached = parseCache.get(uri);
  const oldTree = cached?.tree;

  // Parse with tree-sitter
  const tree = parser.parse(text, oldTree);
  parseCache.set(uri, tree, version);

  // Extract syntax errors
  const diagnostics = parser.getSyntaxErrors(tree);

  // Send diagnostics to client
  connection.sendDiagnostics({ uri, diagnostics });

  logger.debug(`Found ${diagnostics.length} syntax errors in ${uri}`);
}

/**
 * Validate semantics (Layer 2: Python AST analysis)
 */
async function validateSemantics(document: TextDocument): Promise<void> {
  const text = document.getText();
  const uri = document.uri;
  const version = document.version;

  try {
    logger.debug(`Starting Python parse for ${uri} (version ${version})`);

    // Parse with Python
    const { ast, elapsed } = await parseWithPython(text);

    // Cache the AST
    astCache.set(uri, ast, version);

    logger.info(`Python parse completed in ${elapsed}ms for ${uri}`);

    // Run semantic diagnostics on AST
    const layer2 = runSemanticDiagnostics(ast);

    // Get Layer 1 (syntax) diagnostics
    const cachedTree = parseCache.get(uri)?.tree;
    const layer1 = cachedTree ? parser.getSyntaxErrors(cachedTree) : [];

    // Merge Layer 1 and Layer 2 diagnostics
    const allDiagnostics = [...layer1, ...layer2];

    connection.sendDiagnostics({ uri, diagnostics: allDiagnostics });

    logger.debug(`Sent ${allDiagnostics.length} total diagnostics (${layer1.length} syntax + ${layer2.length} semantic) for ${uri}`);
  } catch (error) {
    logger.error(`Python parse failed for ${uri}:`, error);

    // Fall back to Layer 1 diagnostics only
    const cachedTree = parseCache.get(uri)?.tree;
    const layer1 = cachedTree ? parser.getSyntaxErrors(cachedTree) : [];
    connection.sendDiagnostics({ uri, diagnostics: layer1 });
  }
}

// Document lifecycle handlers
documents.onDidOpen((event) => {
  logger.debug(`Document opened: ${event.document.uri}`);
  validateDocument(event.document);
});

documents.onDidChangeContent((event) => {
  logger.debug(`Document changed: ${event.document.uri}`);

  // Layer 1: Immediate syntax checking (fast)
  validateDocument(event.document);

  // Layer 2: Debounced semantic analysis (slower, via Python)
  const uri = event.document.uri;
  const document = event.document;

  debouncer.debounce(uri, async () => {
    await validateSemantics(document);
  });
});

documents.onDidClose((event) => {
  logger.debug(`Document closed: ${event.document.uri}`);
  parseCache.delete(event.document.uri);
  astCache.delete(event.document.uri);
  debouncer.cancel(event.document.uri);
  connection.sendDiagnostics({ uri: event.document.uri, diagnostics: [] });
});

/**
 * Completion handler
 */
connection.onCompletion((params: CompletionParams): CompletionItem[] => {
  const document = documents.get(params.textDocument.uri);
  if (!document) {
    return [];
  }

  const position = params.position;
  const line = document.getText({
    start: { line: position.line, character: 0 },
    end: position,
  });

  // Check if we're in a position for tag completion
  const partialTag = getPartialTag(line, position.character);
  if (partialTag) {
    logger.debug(`Tag completion triggered: ${partialTag}`);
    // Calculate the start position of the partial tag (where ':' begins)
    const startChar = position.character - partialTag.length;
    return getTagCompletions(partialTag, position.line, startChar, position.character);
  }

  return [];
});

/**
 * Go-to-definition handler
 */
connection.onDefinition((params: DefinitionParams): Location | null => {
  const document = documents.get(params.textDocument.uri);
  if (!document) return null;

  const cached = parseCache.get(params.textDocument.uri);
  if (!cached) return null;

  const text = document.getText();
  const position = params.position;

  // Find which reference (if any) the cursor is on
  const refs = extractReferences(cached.tree, text);
  const ref = refs.find((r) => isPositionInRange(position, r.range));
  if (!ref) return null;

  // Find the label definition for the reference target
  const labels = extractLabels(cached.tree, text);
  const label = labels.find((l) => l.name === ref.target);
  if (!label) return null;

  return Location.create(params.textDocument.uri, label.range);
});

/**
 * Semantic tokens handler (syntax highlighting)
 */
connection.languages.semanticTokens.on((params: SemanticTokensParams): SemanticTokens => {
  const cached = parseCache.get(params.textDocument.uri);
  if (!cached) {
    logger.warn(`No cached tree for semantic tokens: ${params.textDocument.uri}`);
    return { data: [] };
  }

  logger.debug(`Providing semantic tokens for ${params.textDocument.uri}`);

  // Use tree-sitter highlight query to generate tokens
  const builder = semanticTokensProvider.provideSemanticTokens(cached.tree);
  return builder.build();
});

/**
 * Document symbols handler (outline/table of contents)
 */
connection.onDocumentSymbol((params: DocumentSymbolParams): DocumentSymbol[] => {
  const document = documents.get(params.textDocument.uri);
  if (!document) {
    logger.warn(`No document found for symbols: ${params.textDocument.uri}`);
    return [];
  }

  const cached = parseCache.get(params.textDocument.uri);
  if (!cached) {
    logger.warn(`No cached tree for document symbols: ${params.textDocument.uri}`);
    return [];
  }

  logger.debug(`Extracting document symbols for ${params.textDocument.uri}`);

  const text = document.getText();
  const symbols = extractDocumentSymbols(cached.tree, text);

  logger.debug(`Returning ${symbols.length} top-level symbols`);

  return symbols;
});

// Custom requests for source/preview navigation
import { findNodeById, findNodeAtPosition } from './layer2/ast';

connection.onRequest('rsm/nodePosition', (params: { textDocument: { uri: string }; nodeid: number }) => {
  const cached = astCache.get(params.textDocument.uri);
  if (!cached) return null;
  const node = findNodeById(cached.ast, params.nodeid);
  if (!node) return null;
  // contentStart: first child's position (after tag + meta region)
  const firstChild = node.children?.find(c => c.nodeid != null || c.nodeclass === 'Text');
  return {
    startLine: node.start_point[0],
    startCol: node.start_point[1],
    endLine: node.end_point[0],
    endCol: node.end_point[1],
    contentStartLine: firstChild?.start_point[0] ?? node.start_point[0],
    contentStartCol: firstChild?.start_point[1] ?? node.start_point[1],
  };
});

connection.onRequest('rsm/nodeAtPosition', (params: { textDocument: { uri: string }; line: number; character: number }) => {
  const cached = astCache.get(params.textDocument.uri);
  if (!cached) return null;
  const node = findNodeAtPosition(cached.ast, params.line, params.character);
  if (!node || node.nodeid == null) return null;
  return { nodeid: node.nodeid, nodeclass: node.nodeclass };
});

// Make the text document manager listen on the connection
documents.listen(connection);

// Start listening
connection.listen();

logger.info('RSM Language Server started');
