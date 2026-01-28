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
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';
import { RsmParser, ParseTreeCache } from './layer1/parser';
import { getTagCompletions, getPartialTag } from './layer1/completion';
import { parseWithPython } from './layer2/python';
import { ASTCache, Debouncer } from './layer2';
import { runSemanticDiagnostics } from './diagnostics/engine';
import { logger } from './utils/logger';

// Create LSP connection
const connection = createConnection(ProposedFeatures.all);

// Create document manager
const documents = new TextDocuments(TextDocument);

// Layer 1: Tree-sitter parser and cache
const parser = new RsmParser();
const parseCache = new ParseTreeCache();

// Layer 2: Python AST cache and debouncer
const astCache = new ASTCache();
const debouncer = new Debouncer(500); // 500ms debounce

// Initialize server
connection.onInitialize((_params: InitializeParams) => {
  logger.info('Initializing RSM Language Server');

  const result: InitializeResult = {
    capabilities: {
      textDocumentSync: TextDocumentSyncKind.Incremental,
      completionProvider: {
        triggerCharacters: [':'],
      },
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
    const layer1 = parser.getSyntaxErrors(parseCache.get(uri)?.tree!);

    // Merge Layer 1 and Layer 2 diagnostics
    const allDiagnostics = [...layer1, ...layer2];

    connection.sendDiagnostics({ uri, diagnostics: allDiagnostics });

    logger.debug(`Sent ${allDiagnostics.length} total diagnostics (${layer1.length} syntax + ${layer2.length} semantic) for ${uri}`);
  } catch (error) {
    logger.error(`Python parse failed for ${uri}:`, error);

    // Fall back to Layer 1 diagnostics only
    const layer1 = parser.getSyntaxErrors(parseCache.get(uri)?.tree!);
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
    return getTagCompletions(partialTag);
  }

  return [];
});

// Make the text document manager listen on the connection
documents.listen(connection);

// Start listening
connection.listen();

logger.info('RSM Language Server started');
